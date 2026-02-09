"""Entry point for auth service when run as a module."""

import sys
import uvicorn
from main import app

# Run immediately when imported as module
print("Starting auth service...", file=sys.stderr, flush=True)

uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    log_level="info",
)

