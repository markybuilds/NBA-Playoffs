# Data models for NBA Odds Analyzer

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GameInfo:
    game_id: str
    home_team: str
    away_team: str
    start_time: str

@dataclass
class PlayerProp:
    player_name: str
    market_key: str
    market_description: str
    bookmaker: str
    outcome: str
    price: float
    point_value: float
    description: str
    # Add more fields as needed
