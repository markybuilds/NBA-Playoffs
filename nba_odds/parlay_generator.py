"""
Parlay Generator for NBA Player Props
- Dynamically finds the optimal parlay size (starting at 3 legs)
- Balances win probability and edge
- Outputs top parlays to CSV
"""
import pandas as pd
import itertools
from typing import List, Dict, Any
import concurrent.futures
import time

PARLAY_MIN_LEGS = 3
PARLAY_MAX_LEGS = 6
MIN_PROBABILITY = 0.05  # Minimum acceptable win probability for a parlay
TOP_N_PARLAYS = 10
TOP_PROPS = 1000  # Only consider top 250 props by edge for speed and diversity

POINTS_MARKETS = {"player_points", "player_points_alternate"}
REBOUNDS_MARKETS = {"player_rebounds", "player_rebounds_alternate"}
ASSISTS_MARKETS = {"player_assists", "player_assists_alternate"}
ALLOWED_MARKETS = POINTS_MARKETS | REBOUNDS_MARKETS | ASSISTS_MARKETS

AMERICAN_ODDS_CAP = -500  # Maximum allowed negative American odds for any leg


def load_props(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Expect columns: player, market, line, odds, implied_prob, edge
    return df


def parlay_score(parlay: List[Dict[str, Any]], mode: str = "balance") -> float:
    # mode: 'prob', 'edge', or 'balance'
    prob = 1.0
    edge = 0.0
    payout = 1.0
    for leg in parlay:
        prob *= leg["implied_prob"]
        edge += leg["edge"]
        payout *= leg["odds"]
    avg_edge = edge / len(parlay)
    if mode == "prob":
        return prob
    elif mode == "edge":
        return avg_edge
    else:
        # Weighted: 0.5*prob + 0.5*avg_edge (normalize edge to 0-1 for balance)
        norm_edge = (avg_edge + 1) / 2  # crude normalization
        return 0.5 * prob + 0.5 * norm_edge


def is_valid_combo(combo):
    players = set()
    markets = set()
    for leg in combo:
        if leg["player_name"] in players or leg["market_key"] in markets:
            return False
        players.add(leg["player_name"])
        markets.add(leg["market_key"])
    return True


def score_combo(combo, min_prob):
    prob = 1.0
    edge = 0.0
    payout = 1.0
    k = len(combo)
    for leg in combo:
        prob *= leg["implied_prob"]
        edge += leg["edge"]
        payout *= leg["odds_decimal"]
    avg_edge = edge / k
    if prob < min_prob:
        return None
    return {
        "legs": combo,
        "num_legs": k,
        "probability": prob,
        "avg_edge": avg_edge,
        "payout": payout,
    }


def generate_parlays(df: pd.DataFrame, min_legs=PARLAY_MIN_LEGS, max_legs=PARLAY_MAX_LEGS, min_prob=MIN_PROBABILITY, top_n=TOP_N_PARLAYS):
    props = df.to_dict(orient="records")
    best_parlays = []
    for k in range(min_legs, max_legs + 1):
        combos = (combo for combo in itertools.combinations(props, k) if is_valid_combo(combo))
        parlays = []
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for i, combo in enumerate(combos):
                futures.append(executor.submit(score_combo, combo, min_prob))
                if i % 100000 == 0 and i > 0:
                    print(f"Checked {i} combos of size {k}...")
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    parlays.append(result)
        parlays.sort(key=lambda p: 0.5 * p["probability"] + 0.5 * ((p["avg_edge"] + 1) / 2), reverse=True)
        best_parlays.extend(parlays[:top_n])
        if parlays and parlays[0]["probability"] < min_prob * 2:
            break
    return best_parlays


def greedy_parlay_builder(df, min_legs=PARLAY_MIN_LEGS, max_legs=PARLAY_MAX_LEGS, top_n=TOP_N_PARLAYS):
    # Build up to top_n parlays using a greedy approach
    parlays = []
    used_indices = set()
    df = df.copy()
    # Exclude props with odds_decimal <= 1.01 (invalid or zero-division odds)
    df = df[df['odds_decimal'] > 1.01]
    # Filter out props with odds_decimal that convert to American odds < cap
    def decimal_to_american_odds_val(decimal_odds):
        if decimal_odds >= 2.0:
            return (decimal_odds - 1) * 100
        else:
            return -100 / (decimal_odds - 1)
    df = df[df['odds_decimal'].apply(lambda x: decimal_to_american_odds_val(x) >= AMERICAN_ODDS_CAP)]
    # --- Always include the best 2-leg parlay by edge (with constraints and payout >= 3.0) ---
    best_2leg = None
    best_score = float('-inf')
    props = df.to_dict(orient="records")
    for i in range(len(props)):
        for j in range(i+1, len(props)):
            combo = [props[i], props[j]]
            if is_valid_combo(combo):
                prob = props[i]['implied_prob'] * props[j]['implied_prob']
                avg_edge = (props[i]['edge'] + props[j]['edge']) / 2
                payout = props[i]['odds_decimal'] * props[j]['odds_decimal']
                if payout < 3.0:
                    continue  # Only consider parlays with payout >= 3.0
                score = avg_edge  # Use only avg_edge for best 2-leg parlay
                if score > best_score:
                    best_score = score
                    best_2leg = {
                        'legs': combo,
                        'num_legs': 2,
                        'probability': prob,
                        'avg_edge': avg_edge,
                        'payout': payout,
                    }
    if best_2leg:
        parlays.append(best_2leg)
    # --- End best 2-leg inclusion ---
    for _ in range(top_n):
        parlay = []
        available = df[~df.index.isin(used_indices)]
        # Start with the best available prop
        if available.empty:
            break
        first = available.iloc[0]
        parlay.append(first)
        used_indices.add(first.name)
        # Greedily add best non-conflicting props (only exclude same player+market)
        for _ in range(min_legs - 1, max_legs):
            available = df[~df.index.isin(used_indices)]
            for leg in parlay:
                available = available[~((available['player_name'] == leg['player_name']) & (available['market_key'] == leg['market_key']))]
            # Exclude props with odds_decimal <= 1.01
            available = available[available['odds_decimal'] > 1.01]
            # Filter out props with odds_decimal that convert to American odds < cap
            available = available[available['odds_decimal'].apply(lambda x: decimal_to_american_odds_val(x) >= AMERICAN_ODDS_CAP)]
            if available.empty:
                break
            next_leg = available.iloc[0]
            parlay.append(next_leg)
            used_indices.add(next_leg.name)
        if len(parlay) >= min_legs:
            # Score parlay
            prob = 1.0
            edge = 0.0
            payout = 1.0
            for leg in parlay:
                prob *= leg['implied_prob']
                edge += leg['edge']
                payout *= leg['odds_decimal']
            avg_edge = edge / len(parlay)
            parlays.append({
                'legs': parlay,
                'num_legs': len(parlay),
                'probability': prob,
                'avg_edge': avg_edge,
                'payout': payout,
            })
    return parlays


def save_parlays(parlays, out_csv):
    rows = []
    for p in parlays:
        row = {
            "num_legs": p["num_legs"],
            "probability": p["probability"],
            "avg_edge": p["avg_edge"],
            "payout": p["payout"],
            "legs": "; ".join(f"{leg['player_name']} {leg['market_description']} {leg['prop_line']} @ {leg['odds_decimal']}" for leg in p["legs"]),
        }
        rows.append(row)
    pd.DataFrame(rows).to_csv(out_csv, index=False)


def decimal_to_american_odds(decimal_odds):
    if decimal_odds >= 2.0:
        return f"+{int((decimal_odds - 1) * 100):d}"
    else:
        return f"-{int(100 / (decimal_odds - 1))}"


def find_next_higher_leg(df, leg):
    # Find the next higher line for the same player/market, odds must be valid
    player = leg['player_name']
    market = leg['market_key']
    current_line = leg['prop_line']
    # Only consider lines strictly greater than current
    candidates = df[(df['player_name'] == player) & (df['market_key'] == market) & (df['prop_line'] > current_line)]
    if not candidates.empty:
        # Pick the lowest next line
        next_leg = candidates.sort_values('prop_line').iloc[0]
        return next_leg
    else:
        # No higher line, return the original leg
        return leg


def expected_value_no_sweat(parlay, stake=100, free_bet_conversion=0.7):
    """Calculate expected value for a no sweat (risk-free) bet promo.
    stake: amount risked (arbitrary, cancels out for ranking)
    free_bet_conversion: how much a free bet is worth as cash (e.g., 0.7)
    """
    win_prob = parlay["probability"]
    payout = parlay["payout"] * stake
    net_win = payout - stake
    lose_prob = 1 - win_prob
    free_bet_value = stake * free_bet_conversion
    ev = win_prob * net_win + lose_prob * free_bet_value - (lose_prob * stake)
    # The last term subtracts the lost stake, so EV is relative to cash risked
    return ev


def is_valid_no_sweat_combo(combo):
    # No duplicate player for the same stat type (e.g., rebounds/alt rebounds)
    player_market = set()
    for leg in combo:
        # Normalize market to stat type (e.g., 'rebounds' for both 'player_rebounds' and 'player_rebounds_alternate')
        stat_type = leg['market_key'].replace('_alternate', '')
        key = (leg['player_name'], stat_type)
        if key in player_market:
            return False
        player_market.add(key)
    return True


def save_parlays_markdown(parlays, out_md, df):
    """Save parlays to a Markdown file for easy human reading, with ladder versions and value 2-leg parlays."""
    parlays = sorted(parlays, key=lambda p: p["probability"], reverse=True)
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write('# Top NBA Player Prop Parlays\n\n')
        # Top 3 most probable 5-leg parlays
        top_5leg = [p for p in parlays if p["num_legs"] == 5][:3]
        if top_5leg:
            f.write('## Top 3 Most Probable 5-Leg Parlays\n\n')
            for i, p in enumerate(top_5leg, 1):
                f.write(f'### Parlay {i} (5 legs)\n')
                f.write(f'- **Probability:** {p["probability"]:.2%}\n')
                f.write(f'- **Avg Edge:** {p["avg_edge"]:.2f}\n')
                f.write(f'- **Payout:** {p["payout"]:.2f} (Decimal), {decimal_to_american_odds(p["payout"])} (American)\n')
                f.write(f'- **Legs:**\n')
                for leg in p["legs"]:
                    am_odds = decimal_to_american_odds(leg["odds_decimal"])
                    f.write(f'    - {leg["player_name"]}: {leg["market_description"]} Over {leg["prop_line"]} @ {am_odds}\n')
                f.write('\n')
                # Ladder version
                ladder_legs = [find_next_higher_leg(df, leg) for leg in p["legs"]]
                # Remove duplicate legs (if no higher line, may repeat)
                ladder_legs = [dict(t) for t in {tuple(leg.items()) for leg in ladder_legs}]
                if len(ladder_legs) == len(p["legs"]):
                    prob = 1.0
                    edge = 0.0
                    payout = 1.0
                    for leg in ladder_legs:
                        prob *= leg['implied_prob']
                        edge += leg['edge']
                        payout *= leg['odds_decimal']
                    avg_edge = edge / len(ladder_legs)
                    f.write(f'#### Parlay {i} Ladder (next higher line for each leg)\n')
                    f.write(f'- **Probability:** {prob:.2%}\n')
                    f.write(f'- **Avg Edge:** {avg_edge:.2f}\n')
                    f.write(f'- **Payout:** {payout:.2f} (Decimal), {decimal_to_american_odds(payout)} (American)\n')
                    f.write(f'- **Legs:**\n')
                    for leg in ladder_legs:
                        am_odds = decimal_to_american_odds(leg["odds_decimal"])
                        f.write(f'    - {leg["player_name"]}: {leg["market_description"]} Over {leg["prop_line"]} @ {am_odds}\n')
                    f.write('\n')
        # Always output 2-leg value parlays
        two_leg = [p for p in parlays if p["num_legs"] == 2]
        if two_leg:
            best_2leg = max(two_leg, key=lambda p: p["payout"])
            f.write('## Best 2-Leg Parlay (No Probability Filter)\n\n')
            f.write(f'- **Probability:** {best_2leg["probability"]:.2%}\n')
            f.write(f'- **Avg Edge:** {best_2leg["avg_edge"]:.2f}\n')
            f.write(f'- **Payout:** {best_2leg["payout"]:.2f} (Decimal), {decimal_to_american_odds(best_2leg["payout"])} (American)\n')
            f.write(f'- **Legs:**\n')
            for leg in best_2leg["legs"]:
                am_odds = decimal_to_american_odds(leg["odds_decimal"])
                f.write(f'    - {leg["player_name"]}: {leg["market_description"]} Over {leg["prop_line"]} @ {am_odds}\n')
            f.write('\n')
        else:
            f.write('## Best 2-Leg Parlay (No Probability Filter)\n\n- No qualifying parlay found.\n\n')
        # Optionally, still show the >10% and >20% sections
        two_leg_10 = [p for p in parlays if p["num_legs"] == 2 and p["probability"] > 0.10]
        if two_leg_10:
            best_2leg_10 = max(two_leg_10, key=lambda p: p["payout"])
            f.write('## Highest Value 2-Leg Parlay (with >10% win probability)\n\n')
            f.write(f'- **Probability:** {best_2leg_10["probability"]:.2%}\n')
            f.write(f'- **Avg Edge:** {best_2leg_10["avg_edge"]:.2f}\n')
            f.write(f'- **Payout:** {best_2leg_10["payout"]:.2f} (Decimal), {decimal_to_american_odds(best_2leg_10["payout"])} (American)\n')
            f.write(f'- **Legs:**\n')
            for leg in best_2leg_10["legs"]:
                am_odds = decimal_to_american_odds(leg["odds_decimal"])
                f.write(f'    - {leg["player_name"]}: {leg["market_description"]} Over {leg["prop_line"]} @ {am_odds}\n')
            f.write('\n')
        else:
            f.write('## Highest Value 2-Leg Parlay (with >10% win probability)\n\n- No qualifying parlay found.\n\n')
        two_leg_20 = [p for p in parlays if p["num_legs"] == 2 and p["probability"] >= 0.20]
        if two_leg_20:
            best_2leg_20 = max(two_leg_20, key=lambda p: p["payout"])
            f.write('## Highest Value 2-Leg Parlay (with >20% win probability)\n\n')
            f.write(f'- **Probability:** {best_2leg_20["probability"]:.2%}\n')
            f.write(f'- **Avg Edge:** {best_2leg_20["avg_edge"]:.2f}\n')
            f.write(f'- **Payout:** {best_2leg_20["payout"]:.2f} (Decimal), {decimal_to_american_odds(best_2leg_20["payout"])} (American)\n')
            f.write(f'- **Legs:**\n')
            for leg in best_2leg_20["legs"]:
                am_odds = decimal_to_american_odds(leg["odds_decimal"])
                f.write(f'    - {leg["player_name"]}: {leg["market_description"]} Over {leg["prop_line"]} @ {am_odds}\n')
            f.write('\n')
        else:
            f.write('## Highest Value 2-Leg Parlay (with >20% win probability)\n\n- No qualifying parlay found.\n\n')
        # --- Best No Sweat Parlay Section ---
        best_no_sweat = None
        best_ev = float('-inf')
        for p in parlays:
            if is_valid_no_sweat_combo(p['legs']):
                ev = expected_value_no_sweat(p, stake=100, free_bet_conversion=0.7)
                if ev > best_ev:
                    best_ev = ev
                    best_no_sweat = p
        if best_no_sweat:
            f.write('## Best Parlay for No Sweat Promo (FanDuel)\n\n')
            f.write(f'- **Probability:** {best_no_sweat["probability"]:.2%}\n')
            f.write(f'- **Avg Edge:** {best_no_sweat["avg_edge"]:.2f}\n')
            f.write(f'- **Payout:** {best_no_sweat["payout"]:.2f} (Decimal), {decimal_to_american_odds(best_no_sweat["payout"])} (American)\n')
            f.write(f'- **Expected Value (No Sweat, $100 stake, 70% free bet):** ${expected_value_no_sweat(best_no_sweat, stake=100, free_bet_conversion=0.7):.2f}\n')
            f.write(f'- **Legs:**\n')
            for leg in best_no_sweat["legs"]:
                am_odds = decimal_to_american_odds(leg["odds_decimal"])
                f.write(f'    - {leg["player_name"]}: {leg["market_description"]} Over {leg["prop_line"]} @ {am_odds}\n')
            f.write('\n')


def run_parlay_generator():
    df = load_props("data/nba_player_prop_edges.csv")
    # Filter to only points, rebounds, assists (and their alternates)
    df = df[df["market_key"].isin(ALLOWED_MARKETS)]
    # Filter to only props with edge > 0
    df = df[df["edge"] > 0]
    df = df.sort_values(by='edge', ascending=False).head(TOP_PROPS)  # Filter to top N props
    # Use greedy parlay builder for speed
    parlays = greedy_parlay_builder(df, min_legs=2, max_legs=5, top_n=30)

    # --- Patch: Always include the best 2-leg parlay by edge if not present ---
    two_leg_parlays = [p for p in parlays if p['num_legs'] == 2]
    if not two_leg_parlays:
        # Brute-force all valid 2-leg combos (fast for small N)
        props = df.to_dict(orient="records")
        best_2leg = None
        best_score = float('-inf')
        for i in range(len(props)):
            for j in range(i+1, len(props)):
                combo = [props[i], props[j]]
                if is_valid_combo(combo):
                    prob = props[i]['implied_prob'] * props[j]['implied_prob']
                    avg_edge = (props[i]['edge'] + props[j]['edge']) / 2
                    payout = props[i]['odds_decimal'] * props[j]['odds_decimal']
                    score = avg_edge  # or use payout for highest payout
                    if score > best_score:
                        best_score = score
                        best_2leg = {
                            'legs': combo,
                            'num_legs': 2,
                            'probability': prob,
                            'avg_edge': avg_edge,
                            'payout': payout,
                        }
        if best_2leg:
            parlays.append(best_2leg)
    # --- End patch ---

    # Save to CSV and Markdown
    save_parlays(parlays, "data/nba_best_parlays.csv")
    save_parlays_markdown(parlays, "data/nba_best_parlays.md", df)
    print("Saved best parlays to data/nba_best_parlays.csv and data/nba_best_parlays.md")
