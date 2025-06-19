#!/usr/bin/env python3
"""
NBA Odds Analyzer

This module fetches and analyzes NBA player prop odds from The Odds API
to help identify valuable betting opportunities based on statistical analysis.

Author: NBA Playoffs Analysis Tool
Version: 1.0.0
Last Updated: 2025-01-15
"""

import os
import sys
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timezone

import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class PlayerProp:
    """Data class for player prop betting information."""
    player_name: str
    market_key: str
    market_name: str
    bookmaker: str
    outcome: str  # "Over" or "Under"
    price: int  # American odds format
    point: Optional[float] = None  # The line/threshold
    description: Optional[str] = None


@dataclass
class GameInfo:
    """Data class for NBA game information."""
    game_id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: str
    bookmakers_count: int


class NBAMarketKeys:
    """NBA Player Props Market Keys for The Odds API."""
    
    # Standard Player Props
    PLAYER_POINTS = "player_points"
    PLAYER_REBOUNDS = "player_rebounds"
    PLAYER_ASSISTS = "player_assists"
    PLAYER_THREES = "player_threes"
    PLAYER_STEALS = "player_steals"
    PLAYER_BLOCKS = "player_blocks"
    PLAYER_TURNOVERS = "player_turnovers"
    
    # Alternate Player Props (X+ lines and alternate markets)
    PLAYER_POINTS_ALTERNATE = "player_points_alternate"
    PLAYER_REBOUNDS_ALTERNATE = "player_rebounds_alternate"
    PLAYER_ASSISTS_ALTERNATE = "player_assists_alternate"
    PLAYER_BLOCKS_ALTERNATE = "player_blocks_alternate"
    PLAYER_STEALS_ALTERNATE = "player_steals_alternate"
    PLAYER_TURNOVERS_ALTERNATE = "player_turnovers_alternate"
    PLAYER_THREES_ALTERNATE = "player_threes_alternate"
    
    # Combination Props
    PLAYER_POINTS_ASSISTS_ALTERNATE = "player_points_assists_alternate"
    PLAYER_POINTS_REBOUNDS_ALTERNATE = "player_points_rebounds_alternate"
    PLAYER_REBOUNDS_ASSISTS_ALTERNATE = "player_rebounds_assists_alternate"
    PLAYER_POINTS_REBOUNDS_ASSISTS_ALTERNATE = "player_points_rebounds_assists_alternate"
    
    @classmethod
    def get_all_markets(cls) -> List[str]:
        """Return all available NBA player prop market keys."""
        return [
            cls.PLAYER_POINTS,
            cls.PLAYER_REBOUNDS,
            cls.PLAYER_ASSISTS,
            cls.PLAYER_THREES,
            cls.PLAYER_STEALS,
            cls.PLAYER_BLOCKS,
            cls.PLAYER_TURNOVERS,
            cls.PLAYER_POINTS_ALTERNATE,
            cls.PLAYER_REBOUNDS_ALTERNATE,
            cls.PLAYER_ASSISTS_ALTERNATE,
            cls.PLAYER_BLOCKS_ALTERNATE,
            cls.PLAYER_STEALS_ALTERNATE,
            cls.PLAYER_TURNOVERS_ALTERNATE,
            cls.PLAYER_THREES_ALTERNATE,
            cls.PLAYER_POINTS_ASSISTS_ALTERNATE,
            cls.PLAYER_POINTS_REBOUNDS_ALTERNATE,
            cls.PLAYER_REBOUNDS_ASSISTS_ALTERNATE,
            cls.PLAYER_POINTS_REBOUNDS_ASSISTS_ALTERNATE
        ]
    
    @classmethod
    def get_standard_markets(cls) -> List[str]:
        """Return standard (non-alternate) NBA player prop market keys."""
        return [
            cls.PLAYER_POINTS,
            cls.PLAYER_REBOUNDS,
            cls.PLAYER_ASSISTS,
            cls.PLAYER_THREES,
            cls.PLAYER_STEALS,
            cls.PLAYER_BLOCKS,
            cls.PLAYER_TURNOVERS
        ]
    
    @classmethod
    def get_market_description(cls, market_key: str) -> str:
        """Get human-readable description for market key."""
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
    """Main class for fetching and analyzing NBA player prop odds."""
    
    def __init__(self, api_key: Optional[str] = None, bookmaker_filter: Optional[str] = None):
        """Initialize the NBA Odds Analyzer.
        
        Args:
            api_key: The Odds API key. If None, will try to load from environment.
            bookmaker_filter: Specific bookmaker to filter for (e.g., 'fanduel'). If None, includes all bookmakers.
        """
        self.api_key = api_key or os.getenv('ODDS_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set ODDS_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://api.the-odds-api.com/v4"
        self.sport_key = "basketball_nba"
        self.regions = "us"  # Focus on US bookmakers for NBA
        self.bookmaker_filter = bookmaker_filter  # Store bookmaker filter
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NBA-Odds-Analyzer/1.0.0'
        })
        
        # API usage tracking
        self.requests_used = 0
        self.requests_remaining = None
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make a request to The Odds API with error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data or None if error
        """
        url = f"{self.base_url}/{endpoint}"
        params['apiKey'] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            # Update usage tracking from headers
            if 'x-requests-used' in response.headers:
                self.requests_used = int(response.headers['x-requests-used'])
            if 'x-requests-remaining' in response.headers:
                self.requests_remaining = int(response.headers['x-requests-remaining'])
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return None
    
    def get_nba_games(self) -> List[GameInfo]:
        """Fetch current NBA games with available odds.
        
        Returns:
            List of GameInfo objects
        """
        params = {
            'regions': self.regions,
            'markets': 'h2h',  # Just get basic info first
            'oddsFormat': 'american'
        }
        
        data = self._make_request(f"sports/{self.sport_key}/odds", params)
        if not data:
            return []
        
        games = []
        for game in data:
            game_info = GameInfo(
                game_id=game['id'],
                sport_key=game['sport_key'],
                home_team=game['home_team'],
                away_team=game['away_team'],
                commence_time=game['commence_time'],
                bookmakers_count=len(game.get('bookmakers', []))
            )
            games.append(game_info)
        
        return games
    
    def get_player_props(self, game_id: str, markets: List[str] = None) -> List[PlayerProp]:
        """Fetch player prop odds for a specific game.
        
        Args:
            game_id: The game ID from get_nba_games()
            markets: List of market keys to fetch. If None, uses standard markets.
            
        Returns:
            List of PlayerProp objects
        """
        if markets is None:
            markets = NBAMarketKeys.get_standard_markets()
        
        # Convert markets list to comma-separated string
        markets_param = ','.join(markets)
        
        params = {
            'regions': self.regions,
            'markets': markets_param,
            'oddsFormat': 'american'
        }
        
        data = self._make_request(f"sports/{self.sport_key}/events/{game_id}/odds", params)
        if not data:
            return []
        
        props = []
        
        # Parse bookmaker data
        for bookmaker in data.get('bookmakers', []):
            bookmaker_key = bookmaker['key']
            
            # Apply bookmaker filter if specified
            if self.bookmaker_filter and bookmaker_key != self.bookmaker_filter:
                continue
            
            for market in bookmaker.get('markets', []):
                market_key = market['key']
                market_name = NBAMarketKeys.get_market_description(market_key)
                
                for outcome in market.get('outcomes', []):
                    prop = PlayerProp(
                        player_name=outcome.get('description', 'Unknown Player'),
                        market_key=market_key,
                        market_name=market_name,
                        bookmaker=bookmaker_key,
                        outcome=outcome['name'],  # "Over" or "Under"
                        price=outcome['price'],
                        point=outcome.get('point'),
                        description=outcome.get('description')
                    )
                    props.append(prop)
        
        return props
    
    def find_best_odds(self, props: List[PlayerProp]) -> Dict[str, Dict[str, PlayerProp]]:
        """Find the best odds for each player prop.
        
        Args:
            props: List of PlayerProp objects
            
        Returns:
            Dictionary with structure: {player_market_key: {'Over': PlayerProp, 'Under': PlayerProp}}
        """
        best_odds = {}
        
        for prop in props:
            # Create unique key for player + market + point
            key = f"{prop.player_name}_{prop.market_key}_{prop.point}"
            
            if key not in best_odds:
                best_odds[key] = {}
            
            # Track best odds for Over and Under separately
            if prop.outcome not in best_odds[key]:
                best_odds[key][prop.outcome] = prop
            else:
                # Higher odds (more positive) are better
                current_best = best_odds[key][prop.outcome]
                if prop.price > current_best.price:
                    best_odds[key][prop.outcome] = prop
        
        return best_odds
    
    def analyze_game_props(self, game_id: str, markets: List[str] = None) -> Dict[str, Any]:
        """Comprehensive analysis of player props for a game.
        
        Args:
            game_id: The game ID
            markets: List of market keys to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        props = self.get_player_props(game_id, markets)
        if not props:
            return {'error': 'No props found for this game'}
        
        best_odds = self.find_best_odds(props)
        
        # Group by market type
        market_summary = {}
        for prop in props:
            market = prop.market_key
            if market not in market_summary:
                market_summary[market] = {
                    'total_props': 0,
                    'unique_players': set(),
                    'bookmakers': set()
                }
            
            market_summary[market]['total_props'] += 1
            market_summary[market]['unique_players'].add(prop.player_name)
            market_summary[market]['bookmakers'].add(prop.bookmaker)
        
        # Convert sets to counts for JSON serialization
        for market in market_summary:
            market_summary[market]['unique_players'] = len(market_summary[market]['unique_players'])
            market_summary[market]['bookmakers'] = len(market_summary[market]['bookmakers'])
        
        return {
            'total_props': len(props),
            'best_odds_count': len(best_odds),
            'market_summary': market_summary,
            'best_odds': best_odds,
            'all_props': props
        }
    
    def save_props_to_csv(self, props: List[PlayerProp], filename: str = None) -> str:
        """Save player props data to a CSV file.
        
        Args:
            props: List of PlayerProp objects to save
            filename: Optional custom filename. If None, generates timestamp-based name.
            
        Returns:
            The filename of the saved CSV file
        """
        if not props:
            print("No props data to save.")
            return None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nba_odds_data_{timestamp}.csv"
        
        # Convert props to DataFrame
        data = []
        for prop in props:
            data.append({
                'timestamp': datetime.now().isoformat(),
                'player_name': prop.player_name,
                'market_key': prop.market_key,
                'market_name': prop.market_name,
                'bookmaker': prop.bookmaker,
                'outcome': prop.outcome,
                'price': prop.price,
                'point': prop.point,
                'description': prop.description
            })
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        try:
            df.to_csv(filename, index=False)
            print(f"\nOdds data saved to: {filename}")
            print(f"Total records saved: {len(data)}")
            return filename
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return None
    
    def save_best_odds_to_csv(self, best_odds: Dict[str, Dict[str, PlayerProp]], filename: str = None) -> str:
        """Save best odds data to a CSV file.
        
        Args:
            best_odds: Dictionary of best odds from find_best_odds()
            filename: Optional custom filename. If None, generates timestamp-based name.
            
        Returns:
            The filename of the saved CSV file
        """
        if not best_odds:
            print("No best odds data to save.")
            return None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nba_best_odds_{timestamp}.csv"
        
        # Convert best odds to DataFrame
        data = []
        for key, odds_dict in best_odds.items():
            # Parse the key to extract player, market, and point
            parts = key.rsplit('_', 2)  # Split from right to handle player names with underscores
            if len(parts) >= 3:
                player_market = '_'.join(parts[:-2])
                market_key = parts[-2]
                point = parts[-1]
            else:
                player_market = key
                market_key = 'unknown'
                point = 'unknown'
            
            for outcome, prop in odds_dict.items():
                data.append({
                    'timestamp': datetime.now().isoformat(),
                    'player_name': prop.player_name,
                    'market_key': prop.market_key,
                    'market_name': prop.market_name,
                    'outcome': prop.outcome,
                    'best_price': prop.price,
                    'point': prop.point,
                    'best_bookmaker': prop.bookmaker,
                    'description': prop.description
                })
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        try:
            df.to_csv(filename, index=False)
            print(f"\nBest odds data saved to: {filename}")
            print(f"Total records saved: {len(data)}")
            return filename
        except Exception as e:
            print(f"Error saving best odds to CSV: {e}")
            return None
    
    def print_usage_stats(self):
        """Print current API usage statistics."""
        print("\n" + "="*50)
        print("API USAGE STATISTICS")
        print("="*50)
        print(f"Requests used: {self.requests_used}")
        if self.requests_remaining is not None:
            print(f"Requests remaining: {self.requests_remaining}")
        print("="*50)


def main():
    """Main function to demonstrate the NBA Odds Analyzer."""
    try:
        # Initialize analyzer with FanDuel filter
        analyzer = NBAOddsAnalyzer(bookmaker_filter='fanduel')
        
        print("NBA Player Props Odds Analyzer")
        print("=" * 40)
        print(f"Using API key: {analyzer.api_key[:8]}...")
        print(f"Target sport: {analyzer.sport_key}")
        print(f"Regions: {analyzer.regions}")
        if analyzer.bookmaker_filter:
            print(f"Bookmaker filter: {analyzer.bookmaker_filter}")
        else:
            print("Bookmaker filter: All bookmakers")
        
        # Get available NBA games
        print("\nFetching NBA games...")
        games = analyzer.get_nba_games()
        
        if not games:
            print("No NBA games found.")
            return
        
        print(f"Found {len(games)} NBA games with odds:")
        for i, game in enumerate(games, 1):
            game_time = datetime.fromisoformat(game.commence_time.replace('Z', '+00:00'))
            print(f"{i}. {game.away_team} @ {game.home_team}")
            print(f"   Time: {game_time.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"   Bookmakers: {game.bookmakers_count}")
            print(f"   Game ID: {game.game_id}")
        
        # Analyze props for the first game
        if games:
            print(f"\nAnalyzing player props for: {games[0].away_team} @ {games[0].home_team}")
            
            # Use standard markets for analysis
            markets = NBAMarketKeys.get_standard_markets()
            print(f"Markets to analyze: {', '.join(markets)}")
            
            analysis = analyzer.analyze_game_props(games[0].game_id, markets)
            
            if 'error' in analysis:
                print(f"Error: {analysis['error']}")
            else:
                print(f"\nAnalysis Results:")
                print(f"Total props found: {analysis['total_props']}")
                print(f"Best odds combinations: {analysis['best_odds_count']}")
                
                print("\nMarket Summary:")
                for market, summary in analysis['market_summary'].items():
                    market_name = NBAMarketKeys.get_market_description(market)
                    print(f"  {market_name}:")
                    print(f"    Props: {summary['total_props']}")
                    print(f"    Players: {summary['unique_players']}")
                    print(f"    Bookmakers: {summary['bookmakers']}")
                
                # Show sample best odds
                print("\nSample Best Odds (first 5):")
                best_odds_items = list(analysis['best_odds'].items())[:5]
                for key, odds in best_odds_items:
                    print(f"\n{key}:")
                    for outcome, prop in odds.items():
                        print(f"  {outcome}: {prop.price:+d} ({prop.bookmaker}) - Line: {prop.point}")
                
                # Save data to CSV file
                print("\n" + "="*50)
                print("SAVING DATA TO CSV FILE")
                print("="*50)
                
                # Save best odds data
                best_odds = analysis['best_odds']
                best_odds_filename = analyzer.save_best_odds_to_csv(best_odds)
                
                print("\nCSV file created successfully!")
                if best_odds_filename:
                    print(f"- Best odds data: {best_odds_filename}")
        
        # Print API usage
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()