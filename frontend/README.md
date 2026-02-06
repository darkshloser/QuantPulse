# QuantPulse Frontend

React + TypeScript web application for QuantPulse market intelligence platform.

## Architecture

### Layout

**Left Panel:** Searchable list of all available symbols
- Filter by name or Yahoo symbol
- Checkbox to select/deselect symbols
- Selection triggers downstream analysis automatically

**Main Panel:** Selected symbols and triggered signals
- Displays currently selected symbols
- Shows recent signals with:
  - Symbol name
  - Signal type
  - Confidence score
  - Explanation of why signal triggered
  - List of indicators that passed criteria
  - Timestamp
- Manual trigger button to run analysis

**Footer:** Disclaimer (informational only, not financial advice)

### Components

- `SymbolList`: Left panel - symbol search and selection
- `SignalPanel`: Main panel - signals and analysis
- `App`: Main component orchestrating the layout

### API Integration

- Symbol Management Service endpoints (port 8001)
- Real-time signal polling (30s intervals)
- No business logic - pure orchestration and visualization

## Development

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Build for production
npm build

# Format code
npm run format

# Lint code
npm run lint
```

## Environment

Create `.env.local` for development:

```
VITE_API_URL=http://localhost:8001
```

## Design Principles

- Minimalistic MVP design
- Responsive and accessible
- No business logic in frontend
- Pure REST API consumption
- Event-driven updates
