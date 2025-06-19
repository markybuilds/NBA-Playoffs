# NBA Odds Analyzer core logic

import os
from typing import Dict, List, Optional, Any
import requests
from .models import GameInfo, PlayerProp

class APIKeyRotator:
    def __init__(self, key_file: str):
        with open(key_file, 'r') as f:
            self.keys = [line.strip() for line in f if line.strip()]
        self.index = 0
    def get(self):
        return self.keys[self.index]
    def rotate(self):
        self.index = (self.index + 1) % len(self.keys)
        return self.get()

class NBAMarketKeys:
    # ...existing code from nba_odds_analyzer.py NBAMarketKeys...
    PLAYER_POINTS = "player_points"
    PLAYER_REBOUNDS = "player_rebounds"
    PLAYER_ASSISTS = "player_assists"
    PLAYER_THREES = "player_threes"
    PLAYER_STEALS = "player_steals"
    PLAYER_BLOCKS = "player_blocks"
    PLAYER_TURNOVERS = "player_turnovers"
    PLAYER_POINTS_ALTERNATE = "player_points_alternate"
    PLAYER_REBOUNDS_ALTERNATE = "player_rebounds_alternate"
    PLAYER_ASSISTS_ALTERNATE = "player_assists_alternate"
    PLAYER_BLOCKS_ALTERNATE = "player_blocks_alternate"
    PLAYER_STEALS_ALTERNATE = "player_steals_alternate"
    PLAYER_TURNOVERS_ALTERNATE = "player_turnovers_alternate"
    PLAYER_THREES_ALTERNATE = "player_threes_alternate"
    PLAYER_POINTS_ASSISTS_ALTERNATE = "player_points_assists_alternate"
    PLAYER_POINTS_REBOUNDS_ALTERNATE = "player_points_rebounds_alternate"
    PLAYER_REBOUNDS_ASSISTS_ALTERNATE = "player_rebounds_assists_alternate"
    PLAYER_POINTS_REBOUNDS_ASSISTS_ALTERNATE = "player_points_rebounds_assists_alternate"

    @classmethod
    def get_all_markets(cls) -> List[str]:
        return [
            cls.PLAYER_POINTS, cls.PLAYER_REBOUNDS, cls.PLAYER_ASSISTS, cls.PLAYER_THREES,
            cls.PLAYER_STEALS, cls.PLAYER_BLOCKS, cls.PLAYER_TURNOVERS,
            cls.PLAYER_POINTS_ALTERNATE, cls.PLAYER_REBOUNDS_ALTERNATE, cls.PLAYER_ASSISTS_ALTERNATE,
            cls.PLAYER_BLOCKS_ALTERNATE, cls.PLAYER_STEALS_ALTERNATE, cls.PLAYER_TURNOVERS_ALTERNATE,
            cls.PLAYER_THREES_ALTERNATE, cls.PLAYER_POINTS_ASSISTS_ALTERNATE, cls.PLAYER_POINTS_REBOUNDS_ALTERNATE,
            cls.PLAYER_REBOUNDS_ASSISTS_ALTERNATE, cls.PLAYER_POINTS_REBOUNDS_ASSISTS_ALTERNATE
        ]

    @classmethod
    def get_standard_markets(cls) -> List[str]:
        return [
            cls.PLAYER_POINTS, cls.PLAYER_REBOUNDS, cls.PLAYER_ASSISTS, cls.PLAYER_THREES,
            cls.PLAYER_STEALS, cls.PLAYER_BLOCKS, cls.PLAYER_TURNOVERS
        ]

    @classmethod
    def get_market_description(cls, market_key: str) -> str:
        descriptions = {
            cls.PLAYER_POINTS: "Player Points (Over/Under)",
            cls.PLAYER_REBOUNDS: "Player Rebounds (Over/Under)",
            cls.PLAYER_ASSISTS: "Player Assists (Over/Under)",
            cls.PLAYER_THREES: "Player Three-Pointers Made (Over/Under)",
            cls.PLAYER_STEALS: "Player Steals (Over/Under)",
            cls.PLAYER_BLOCKS: "Player Blocks (Over/Under)",
            cls.PLAYER_TURNOVERS: "Player Turnovers (Over/Under)",
            cls.PLAYER_POINTS_ALTERNATE: "Alternate Points (Over/Under)",
            cls.PLAYER_REBOUNDS_ALTERNATE: "Alternate Rebounds (Over/Under)",
            cls.PLAYER_ASSISTS_ALTERNATE: "Alternate Assists (Over/Under)",
            cls.PLAYER_BLOCKS_ALTERNATE: "Alternate Blocks (Over/Under)",
            cls.PLAYER_STEALS_ALTERNATE: "Alternate Steals (Over/Under)",
            cls.PLAYER_TURNOVERS_ALTERNATE: "Alternate Turnovers (Over/Under)",
            cls.PLAYER_THREES_ALTERNATE: "Alternate Three-Pointers (Over/Under)",
            cls.PLAYER_POINTS_ASSISTS_ALTERNATE: "Alternate Points + Assists (Over/Under)",
            cls.PLAYER_POINTS_REBOUNDS_ALTERNATE: "Alternate Points + Rebounds (Over/Under)",
            cls.PLAYER_REBOUNDS_ASSISTS_ALTERNATE: "Alternate Rebounds + Assists (Over/Under)",
            cls.PLAYER_POINTS_REBOUNDS_ASSISTS_ALTERNATE: "Alternate Points + Rebounds + Assists (Over/Under)"
        }
        return descriptions.get(market_key, f"Unknown Market: {market_key}")

class NBAOddsAnalyzer:
    # ...existing code from nba_odds_analyzer.py NBAOddsAnalyzer...
    def __init__(self, api_key: Optional[str] = None, bookmaker_filter: Optional[str] = None):
        key_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'odds_api_keys_database.txt')
        self.key_rotator = APIKeyRotator(key_file)
        self.api_key = api_key or os.getenv('ODDS_API_KEY') or self.key_rotator.get()
        self.base_url = "https://api.the-odds-api.com/v4"
        self.sport_key = "basketball_nba"
        self.regions = "us"
        self.bookmaker_filter = bookmaker_filter
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'NBA-Odds-Analyzer/1.0.0'})
        self.requests_used = 0
        self.requests_remaining = None

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        url = f"{self.base_url}/{endpoint}"
        for _ in range(len(self.key_rotator.keys)):
            params['apiKey'] = self.api_key
            try:
                response = self.session.get(url, params=params, timeout=30)
                if 'x-requests-used' in response.headers:
                    self.requests_used = int(response.headers['x-requests-used'])
                if 'x-requests-remaining' in response.headers:
                    self.requests_remaining = int(response.headers['x-requests-remaining'])
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401 and 'OUT_OF_USAGE_CREDITS' in response.text:
                    print(f"API key quota reached for {self.api_key}, rotating to next key...")
                    self.api_key = self.key_rotator.rotate()
                    continue
                else:
                    print(f"Error making request to {url}: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"Response status: {e.response.status_code}")
                        print(f"Response text: {e.response.text}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error making request to {url}: {e}")
                return None
        print("All API keys exhausted or invalid.")
        return None

    def get_nba_games(self) -> List[GameInfo]:
        """Fetches NBA games using the /events endpoint (no odds, just event info)."""
        endpoint = f"sports/{self.sport_key}/events"
        params = {}
        data = self._make_request(endpoint, params)
        if not data:
            return []
        games = []
        for game in data:
            games.append(GameInfo(
                game_id=game["id"],
                home_team=game["home_team"],
                away_team=game["away_team"],
                start_time=game["commence_time"]
            ))
        return games

    def get_player_props(self, game_id: str, markets: List[str]) -> List[PlayerProp]:
        """Fetches player props for a given game and markets using the /events/{eventId}/odds endpoint. Only FanDuel and only 'Over' bets."""
        endpoint = f"sports/{self.sport_key}/events/{game_id}/odds"
        params = {
            "regions": self.regions,
            "markets": ",".join(markets),
            "bookmakers": "fanduel",  # Only request FanDuel odds from the API
        }
        data = self._make_request(endpoint, params)
        if not data or "bookmakers" not in data:
            return []
        props = []
        for bookmaker in data.get("bookmakers", []):
            if bookmaker["key"] != "fanduel":
                continue
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    if outcome.get("name", "").lower() != "over":
                        continue
                    props.append(PlayerProp(
                        player_name=outcome.get("description", ""),
                        market_key=market.get("key", ""),
                        market_description=NBAMarketKeys.get_market_description(market.get("key", "")),
                        bookmaker=bookmaker.get("title", ""),
                        outcome=outcome.get("name", ""),
                        price=outcome.get("price", 0.0),
                        point_value=outcome.get("point", 0.0),
                        description=outcome.get("description", "")
                    ))
        return props

    def find_best_odds(self, props: List[PlayerProp]) -> List[dict]:
        """Finds the best odds for each player/market/outcome combination."""
        best = {}
        for prop in props:
            key = (prop.player_name, prop.market_key, prop.outcome)
            if key not in best or prop.price > best[key].price:
                best[key] = prop
        return [
            {
                "player_name": p.player_name,
                "market_key": p.market_key,
                "market_description": p.market_description,
                "outcome": p.outcome,
                "price": p.price,
                "point_value": p.point_value,
                "best_bookmaker": p.bookmaker,
                "description": p.description
            }
            for p in best.values()
        ]

    def save_props_to_csv(self, props: List[PlayerProp], filename: str):
        import pandas as pd
        if not props:
            return
        df = pd.DataFrame([p.__dict__ for p in props])
        df.to_csv(filename, index=False)

    def save_best_odds_to_csv(self, props: List[PlayerProp], filename: str):
        best = self.find_best_odds(props)
        import pandas as pd
        if not best:
            return
        df = pd.DataFrame(best)
        df.to_csv(filename, index=False)
