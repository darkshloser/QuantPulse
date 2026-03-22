"""Celery tasks for scheduled signal evaluation."""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from shared.celery_app import celery_app
from shared.database import SessionLocal
from shared.models import (
    User, SelectedSymbol, UserSymbolIndicator, Indicator,
    SignalResult,
)
from shared.logging_config import logger as app_logger


@celery_app.task(name="services.data_analyzer.tasks.evaluate_all_signals")
def evaluate_all_signals():
    """
    Evaluate all indicators for all users' selected symbols.

    Runs at 18:00 and 22:00 CET on working days (Mon-Fri).
    For each user → each selected symbol → check assigned indicators.
    If ALL indicators have result=True, create a signal and notify.
    """
    db: Session = SessionLocal()
    try:
        # Get all active, approved users
        active_users = db.query(User).filter(
            User.is_active == True,
            User.approval_status == "APPROVED",
        ).all()

        total_signals = 0

        for user in active_users:
            # Get user's selected symbols
            selected = db.query(SelectedSymbol).filter(
                SelectedSymbol.user_id == user.id,
            ).all()

            for sel in selected:
                symbol = sel.symbol

                # Get assigned indicators for this symbol
                assignments = (
                    db.query(UserSymbolIndicator)
                    .filter(
                        UserSymbolIndicator.user_id == user.id,
                        UserSymbolIndicator.symbol == symbol,
                    )
                    .all()
                )

                if not assignments:
                    continue

                # TODO: Evaluate each indicator against market data
                # For now, skip evaluation — results stay as-is (null)
                # When market data retrieval is implemented:
                # 1. Fetch latest market data for symbol
                # 2. Run each indicator's logic
                # 3. Update assignment.result and assignment.evaluated_at

                # Check if ALL indicators are True
                all_true = all(a.result is True for a in assignments)

                if all_true:
                    now = datetime.now(timezone.utc)
                    signal_id = f"{user.id}:{symbol}:{now.isoformat()}"

                    # Build explanation from indicator names
                    indicator_ids = [a.indicator_id for a in assignments]
                    indicators = db.query(Indicator).filter(
                        Indicator.id.in_(indicator_ids),
                    ).all()
                    indicator_names = [i.name for i in indicators]

                    signal = SignalResult(
                        id=signal_id,
                        user_id=user.id,
                        symbol=symbol,
                        signal_type="ALL_INDICATORS_PASSED",
                        confidence=1.0,
                        explanation=f"All {len(assignments)} indicators passed: {', '.join(indicator_names)}",
                        indicators_passed=",".join(indicator_names),
                        notified=True,
                        notified_at=now,
                    )
                    db.add(signal)

                    # Cleanup: keep only latest 10 signals per user+symbol
                    existing_signals = (
                        db.query(SignalResult)
                        .filter(
                            SignalResult.user_id == user.id,
                            SignalResult.symbol == symbol,
                            SignalResult.notified == True,
                        )
                        .order_by(SignalResult.notified_at.desc())
                        .offset(10)
                        .all()
                    )
                    for old_signal in existing_signals:
                        db.delete(old_signal)

                    total_signals += 1

                    # TODO: Send Slack notification when slack_enabled is True

        db.commit()
        app_logger.info(f"Signal evaluation complete. Generated {total_signals} signal(s).")
        return {"status": "completed", "signals_generated": total_signals}

    except Exception as e:
        db.rollback()
        app_logger.error(f"Signal evaluation failed: {e}")
        raise
    finally:
        db.close()
