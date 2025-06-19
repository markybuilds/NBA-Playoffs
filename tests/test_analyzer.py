import pytest
from nba_odds.analyzer import NBAOddsAnalyzer, NBAMarketKeys

# Example test for NBAOddsAnalyzer initialization
def test_analyzer_init_env(monkeypatch):
    monkeypatch.setenv('ODDS_API_KEY', 'dummy')
    analyzer = NBAOddsAnalyzer()
    assert analyzer.api_key == 'dummy'

def test_market_keys():
    all_markets = NBAMarketKeys.get_all_markets()
    assert 'player_points' in all_markets
    assert 'player_points_rebounds_assists_alternate' in all_markets
