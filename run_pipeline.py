"""
NBA Odds Data Pipeline Script

This script fetches all NBA player prop odds data using the NBAOddsAnalyzer and saves only the FanDuel 'Over' props to a CSV file.
"""

from nba_odds.analyzer import NBAOddsAnalyzer, NBAMarketKeys
import pandas as pd
from nba_odds.sportsline_scraper import fetch_sportsline_projections
from fuzzywuzzy import process
import os  # Import os module for file path operations

# Initialize analyzer (uses .env for API key)
analyzer = NBAOddsAnalyzer()

def get_market_projection_column():
    # Map market_key to SportsLine projection column
    return {
        "player_points": "PTS",
        "player_assists": "AST",
        "player_rebounds": "TRB",
        "player_threes": "FG",  # SportsLine may not have 3PM, so use FG as proxy if needed
        "player_steals": "ST",
        "player_blocks": "BK",
        "player_turnovers": "TO",
        # Alternate and combo markets can be mapped as needed
        "player_points_alternate": "PTS",
        "player_rebounds_alternate": "TRB",
        "player_assists_alternate": "AST",
        "player_blocks_alternate": "BK",
        "player_steals_alternate": "ST",
        "player_turnovers_alternate": "TO",
        # Add more mappings as needed
    }

def merge_props_with_projections(props_df, merged_csv):
    # Accept props_df as a DataFrame directly
    # Fetch SportsLine projections
    projections_df = fetch_sportsline_projections()
    print("SportsLine projections columns:", projections_df.columns.tolist())
    # Try to find the player name column (case-insensitive)
    player_col = None
    for col in projections_df.columns:
        if col.strip().lower() in ["player", "name", "player name", "playername"]:
            player_col = col
            break
    if not player_col:
        raise ValueError(f"Could not find player name column in projections: {projections_df.columns.tolist()}")
    prop_names = props_df['player_name'].unique()
    # Clean candidate names (dropna, ensure str)
    candidates = projections_df[player_col].dropna().astype(str).tolist()
    # Fuzzy match: map each prop player to best SportsLine player
    name_map = {}
    for name in prop_names:
        try:
            result = process.extractOne(name, candidates)
            if result and isinstance(result, tuple):
                match, score = result
                name_map[name] = match if score > 80 else None
            else:
                print(f"No match for {name}")
                name_map[name] = None
        except Exception as e:
            print(f"Error matching {name}: {e}")
            name_map[name] = None
    props_df['sportsline_player'] = props_df['player_name'].map(name_map)
    merged = props_df.merge(projections_df, left_on='sportsline_player', right_on=player_col, how='left')
    # Add projection value for each row based on market_key
    market_proj_col = get_market_projection_column()
    def get_projection(row):
        col = market_proj_col.get(row['market_key'])
        if col and col in merged.columns:
            try:
                return float(row[col])
            except Exception:
                return None
        return None
    merged['projection'] = merged.apply(get_projection, axis=1)
    merged['projection_type'] = merged['market_key'].map(market_proj_col)
    # Calculate edge (projection - point_value for Over bets)
    merged['edge'] = merged['projection'] - merged['point_value']
    # Calculate implied probability from odds
    merged['implied_prob'] = 1 / merged['price']
    # Only keep and rename relevant columns
    keep_cols = {
        'player_name': 'player_name',
        'market_key': 'market_key',
        'market_description': 'market_description',
        'bookmaker': 'bookmaker',
        'outcome': 'outcome',
        'price': 'odds_decimal',
        'point_value': 'prop_line',
        'description': 'description',
        'projection_type': 'projection_type',
        'projection': 'projection',
        'edge': 'edge',
        'implied_prob': 'implied_prob'
    }
    merged = merged[list(keep_cols.keys())]
    merged = merged.rename(columns=keep_cols)
    # Sort by edge descending (best edge first)
    merged = merged.sort_values(by="edge", ascending=False)
    merged.to_csv(merged_csv, index=False)
    print(f"Merged FanDuel props with SportsLine projections to {merged_csv}")

def main():
    games = analyzer.get_nba_games()
    if not games:
        print("No NBA games found.")
        return
    all_markets = NBAMarketKeys.get_all_markets()
    all_props = []
    for game in games:
        props = analyzer.get_player_props(game.game_id, all_markets)
        all_props.extend(props)
    if not all_props:
        print("No player props found.")
        return
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)  # Create data directory if it doesn't exist
    # No longer save intermediate nba_fanduel_over_props.csv
    props_df = pd.DataFrame(all_props)
    merged_csv = os.path.join(data_dir, "nba_player_prop_edges.csv")
    merge_props_with_projections(props_df, merged_csv)

if __name__ == "__main__":
    main()
