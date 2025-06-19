# NBA Playoffs Odds Analysis

A modern, modular Python project for analyzing NBA player prop odds and projections to identify value bets. Integrates FanDuel player prop odds ("Over" bets only) from The Odds API and player projections from SportsLine, merging and calculating the "edge" for each bet. Outputs a sorted CSV for value betting.

## Features
- Modular package structure (`nba_odds/`)
- FastAPI API for programmatic access
- Automated pipeline for fetching, merging, and analyzing odds and projections
- **Markets:** Only FanDuel and "Over" NBA player prop bets are included (no other books or bet types)
- SportsLine projections are scraped and matched using fuzzy name matching
- Calculates "edge" (projection - prop line) and implied probability
- Outputs a single, sorted CSV (`data/nba_player_prop_edges.csv`) for value betting
- Automated API key rotation using a key database
- All config and output files are organized in `config/` and `data/` directories
- Pytest-based test suite

## Supported Markets
- **Standard Markets:** Single-stat NBA player props (e.g., points, rebounds, assists) with a single line (e.g., "Over 24.5 Points"). _This project currently only supports standard markets._
- **Alternative Markets:** Props with multiple lines for the same stat (e.g., "Over 20.5 Points", "Over 25.5 Points"). _Not currently supported._
- **Combination Markets:** Props combining multiple stats (e.g., "Points + Rebounds + Assists"). _Not currently supported._

_The pipeline currently fetches only standard FanDuel "Over" player prop markets. Support for alternative and combination markets may be added in the future._

## Setup
1. **Clone the repository and switch to the `dev-mode` branch:**
   ```sh
   git clone <repo-url>
   cd Nba-Playoffs
   git checkout dev-mode
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # macOS/Linux
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure Odds API keys:**
   - Add your Odds API keys (one per line, no comments or blank lines) to `config/odds_api_keys_database.txt`.

## Usage
### Run the Pipeline
Fetches FanDuel "Over" player props, scrapes SportsLine projections, merges, calculates edge, and outputs a sorted CSV:
```sh
python run_pipeline.py
```
- Output: `data/nba_player_prop_edges.csv` (sorted by edge, descending)
- Only FanDuel and "Over" bets are included
- API keys are rotated automatically to avoid quota errors

### FastAPI API
Start the API server:
```sh
uvicorn nba_odds.api:app --reload
```
See the interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure
```
nba_odds/
  analyzer.py         # Core odds/projection logic
  models.py           # Data models
  api.py              # FastAPI API
  sportsline_scraper.py # SportsLine projections scraper
run_pipeline.py        # Main pipeline script
config/
  odds_api_keys_database.txt # API keys (one per line)
data/
  nba_player_prop_edges.csv  # Main output (sorted by edge)
requirements.txt
README.md
```

## Testing
Run all tests with:
```sh
pytest
```

## Notes
- Only the merged, sorted CSV is output (no intermediate CSVs).
- All config and output files are centralized in `config/` and `data/`.
- API key file must not contain comments or blank lines.

## Contributing
- Please use feature branches and submit pull requests to `dev-mode`.
- Ensure all code is tested and documented.

## License
MIT License

## Parlay Generator

The parlay generator is a core feature of this project, designed to efficiently find the best NBA player prop parlays for value betting and promotions. It supports multiple optimization strategies and outputs both machine-readable (CSV) and human-readable (Markdown) summaries.

### How It Works
- **Input:** Uses the merged and filtered player prop data (`data/nba_player_prop_edges.csv`).
- **Markets:** Only points, rebounds, and assists (including alternates) are considered. Only "Over" bets from FanDuel are included.
- **Constraints:**
  - No parlay leg can have American odds worse than -500.
  - Only one prop per player/stat type (e.g., cannot include both "Player Rebounds" and "Alternate Rebounds" for the same player in a parlay).
  - No duplicate player/market in a parlay.
  - Only props with positive edge are considered.
- **Optimization:**
  - Finds the top 5-leg parlays by probability and edge.
  - Generates "ladder" parlays by moving each leg to the next higher line.
  - Always includes the best 2-leg parlay (by edge, with payout constraint if set).
  - Special logic for promos: finds the parlay with the highest expected value (EV) for a "No Sweat" (risk-free) bet, accounting for free bet conversion value and all constraints.
- **Output:**
  - `data/nba_best_parlays.csv`: Machine-readable summary of all top parlays.
  - `data/nba_best_parlays.md`: Human-readable Markdown with:
    - Top 3 most probable 5-leg parlays
    - Ladder versions for each top parlay
    - Best 2-leg parlays (with and without probability filters)
    - **Best Parlay for No Sweat Promo (FanDuel):** Maximizes EV for risk-free bet promos, with all constraints enforced

### No Sweat Promo (FanDuel) Logic
- The generator calculates expected value (EV) for each parlay as:
  - `EV = (Win Probability × Net Win) + (Lose Probability × Free Bet Value)`
  - Free bet value is configurable (default: 70% of stake)
  - Only parlays with no duplicate player/stat type are eligible
  - The parlay with the highest EV is shown in the Markdown output

### Example Output
See `data/nba_best_parlays.md` for a sample of the Markdown output, including all parlay types and the best promo parlay.

### Customization
- You can adjust constraints, free bet conversion rate, and output format in `nba_odds/parlay_generator.py`.
- The generator is modular and can be extended for new promo types or custom user constraints.

---
