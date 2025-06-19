# FastAPI app for NBA Odds Analyzer
from fastapi import FastAPI, Query
from nba_odds.analyzer import NBAOddsAnalyzer, NBAMarketKeys
from typing import List

app = FastAPI()

@app.get("/games")
def get_games():
    analyzer = NBAOddsAnalyzer()
    games = analyzer.get_nba_games()
    return [game.__dict__ for game in games]

@app.get("/props")
def get_props(game_id: str, markets: List[str] = Query(None)):
    analyzer = NBAOddsAnalyzer()
    props = analyzer.get_player_props(game_id, markets or NBAMarketKeys.get_standard_markets())
    return [prop.__dict__ for prop in props]

@app.get("/best-odds")
def get_best_odds(game_id: str, markets: List[str] = Query(None)):
    analyzer = NBAOddsAnalyzer()
    props = analyzer.get_player_props(game_id, markets or NBAMarketKeys.get_standard_markets())
    best_odds = analyzer.find_best_odds(props)
    return best_odds
