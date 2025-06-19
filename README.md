# NBA Playoffs Odds Analyzer

A comprehensive Python tool for fetching and analyzing NBA player prop odds from The Odds API to identify valuable betting opportunities across all available markets.

## Features

- **Real-time NBA Odds**: Fetch current player prop odds from multiple sportsbooks
- **Comprehensive Market Coverage**: Support for 18 different market types including standard, alternate, and combination props
- **Best Odds Finder**: Automatically identify the best odds for each player prop across all bookmakers
- **CSV Data Export**: Save odds data and analysis results to CSV files for further analysis
- **Flexible Analysis**: Analyze specific games, markets, or focus on particular players
- **Bookmaker Filtering**: Filter analysis to specific bookmakers (e.g., FanDuel only)
- **API Efficiency**: Smart request management with usage tracking
- **Error Handling**: Robust error handling for API failures and data issues

## NBA Market Keys Supported

### Standard Markets
- `player_points` - Player Points (Over/Under)
- `player_rebounds` - Player Rebounds (Over/Under)
- `player_assists` - Player Assists (Over/Under)
- `player_threes` - Player Three-Pointers Made (Over/Under)
- `player_steals` - Player Steals (Over/Under)
- `player_blocks` - Player Blocks (Over/Under)
- `player_turnovers` - Player Turnovers (Over/Under)

### Alternate Markets
- `player_points_alternate` - Alternate Points (Over/Under)
- `player_rebounds_alternate` - Alternate Rebounds (Over/Under)
- `player_assists_alternate` - Alternate Assists (Over/Under)
- `player_threes_alternate` - Alternate Three-Pointers (Over/Under)
- `player_steals_alternate` - Alternate Steals (Over/Under)
- `player_blocks_alternate` - Alternate Blocks (Over/Under)
- `player_turnovers_alternate` - Alternate Turnovers (Over/Under)

### Combination Markets
- `player_points_assists_alternate` - Alternate Points + Assists (Over/Under)
- `player_points_rebounds_alternate` - Alternate Points + Rebounds (Over/Under)
- `player_rebounds_assists_alternate` - Alternate Rebounds + Assists (Over/Under)
- `player_points_rebounds_assists_alternate` - Alternate Points + Rebounds + Assists (Over/Under)

## Setup

1. **Get an API key** from [The Odds API](https://the-odds-api.com/)
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   # On Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set your API key** in the `.env` file:
   ```
   ODDS_API_KEY=your_api_key_here
   ```

## Usage

### Programmatic Usage
Import and use the analyzer in your own scripts:

```python
from nba_odds.analyzer import NBAOddsAnalyzer
from nba_odds.models import NBAMarketKeys

# Initialize analyzer (all bookmakers)
analyzer = NBAOddsAnalyzer()

# Initialize with FanDuel filter only
analyzer = NBAOddsAnalyzer(bookmaker_filter='fanduel')

# Get NBA games
games = analyzer.get_nba_games()

# Analyze specific markets
markets = [NBAMarketKeys.PLAYER_POINTS, NBAMarketKeys.PLAYER_ASSISTS]
analysis = analyzer.analyze_game_props(games[0].game_id, markets)

# Get player props for all markets
all_markets = NBAMarketKeys.get_all_markets()
props = analyzer.get_player_props(games[0].game_id, all_markets)

# Find best odds
best_odds = analyzer.find_best_odds(props)
```

## Project Structure

- `nba_odds/` - Core package (analyzer, models, API)
- `example_usage.py` - Comprehensive usage examples
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API key)
- `api-notes.txt` - The Odds API documentation
- `nba_finals_2025_analysis.md` - Sample analysis data
- `tests/` - Pytest-based tests

## API Usage Notes

- Player props are mainly available for US sports and bookmakers
- Historical data for additional markets is available from May 3rd, 2023 (requires paid plan)
- Additional markets need to be accessed one event at a time
- All available market keys are accepted in the `markets` parameter
- Monitor your API usage with the built-in tracking features

## CSV Data Export

The analyzer provides methods to save odds data to CSV files for further analysis:

### Manual CSV Saving

```python
from nba_odds.analyzer import NBAOddsAnalyzer

# Initialize analyzer
analyzer = NBAOddsAnalyzer(api_key="your_api_key")

# Get data
results = analyzer.analyze_game_props()

# Save to CSV
analyzer.save_props_to_csv(results['all_props'], 'my_odds_data.csv')
analyzer.save_best_odds_to_csv(results['all_props'], 'my_best_odds.csv')
```

### CSV File Structure

**All Odds Data CSV** contains:
- Timestamp
- Player name
- Market key
- Market description
- Bookmaker
- Outcome (Over/Under)
- Price (odds)
- Point value
- Description

**Best Odds CSV** contains:
- Timestamp
- Player name
- Market key
- Market description
- Outcome (Over/Under)
- Price (best odds)
- Point value
- Best bookmaker
- Description

## Output

The analyzer outputs:
- List of NBA games with player props
- Sample props for each game
- Best available odds across all bookmakers
- API usage statistics

## Integration with Statistical Analysis

To integrate with your existing NBA analysis:
1. Import the `NBAPlayerPropOdds` class
2. Use the returned prop data to compare against your statistical models
3. Identify value bets where the odds don't match your projections

## Rate Limiting

The analyzer automatically handles rate limiting by:
- Tracking API usage from response headers
- Adding delays when approaching rate limits
- Providing usage statistics

## License

This project is for educational purposes only. Sports betting may be illegal in your jurisdiction.
