#!/usr/bin/env python3
"""
Bookmaker Filter Demonstration

This script demonstrates how to use the NBA Odds Analyzer with different bookmaker filters,
including FanDuel-only analysis.

Author: NBA Playoffs Analysis Tool
Version: 1.0.0
Last Updated: 2025-01-15
"""

from nba_odds_analyzer import NBAOddsAnalyzer, NBAMarketKeys


def demo_fanduel_only():
    """Demonstrate FanDuel-only analysis."""
    print("\n" + "="*60)
    print("FANDUEL ONLY ANALYSIS")
    print("="*60)
    
    try:
        # Initialize analyzer with FanDuel filter
        analyzer = NBAOddsAnalyzer(bookmaker_filter='fanduel')
        
        print(f"Bookmaker filter: {analyzer.bookmaker_filter}")
        
        # Get NBA games
        games = analyzer.get_nba_games()
        if not games:
            print("No NBA games found.")
            return
        
        print(f"\nFound {len(games)} NBA games")
        
        # Analyze first game with standard markets
        game = games[0]
        print(f"\nAnalyzing: {game.away_team} @ {game.home_team}")
        
        markets = [NBAMarketKeys.PLAYER_POINTS, NBAMarketKeys.PLAYER_ASSISTS, NBAMarketKeys.PLAYER_REBOUNDS]
        analysis = analyzer.analyze_game_props(game.game_id, markets)
        
        if 'error' not in analysis:
            print(f"\nFanDuel Props Found: {analysis['total_props']}")
            print(f"Best odds combinations: {analysis['best_odds_count']}")
            
            # Show market breakdown
            for market, summary in analysis['market_summary'].items():
                market_name = NBAMarketKeys.get_market_description(market)
                print(f"\n{market_name}:")
                print(f"  Props: {summary['total_props']}")
                print(f"  Players: {summary['unique_players']}")
                print(f"  Bookmakers: {summary['bookmakers']} (should be 1 for FanDuel only)")
        
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error in FanDuel analysis: {e}")


def demo_all_bookmakers():
    """Demonstrate analysis with all bookmakers."""
    print("\n" + "="*60)
    print("ALL BOOKMAKERS ANALYSIS")
    print("="*60)
    
    try:
        # Initialize analyzer without filter (all bookmakers)
        analyzer = NBAOddsAnalyzer()
        
        print(f"Bookmaker filter: {analyzer.bookmaker_filter or 'None (all bookmakers)'}")
        
        # Get NBA games
        games = analyzer.get_nba_games()
        if not games:
            print("No NBA games found.")
            return
        
        print(f"\nFound {len(games)} NBA games")
        
        # Analyze first game with standard markets
        game = games[0]
        print(f"\nAnalyzing: {game.away_team} @ {game.home_team}")
        
        markets = [NBAMarketKeys.PLAYER_POINTS, NBAMarketKeys.PLAYER_ASSISTS, NBAMarketKeys.PLAYER_REBOUNDS]
        analysis = analyzer.analyze_game_props(game.game_id, markets)
        
        if 'error' not in analysis:
            print(f"\nTotal Props Found: {analysis['total_props']}")
            print(f"Best odds combinations: {analysis['best_odds_count']}")
            
            # Show market breakdown
            for market, summary in analysis['market_summary'].items():
                market_name = NBAMarketKeys.get_market_description(market)
                print(f"\n{market_name}:")
                print(f"  Props: {summary['total_props']}")
                print(f"  Players: {summary['unique_players']}")
                print(f"  Bookmakers: {summary['bookmakers']}")
        
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error in all bookmakers analysis: {e}")


def demo_draftkings_only():
    """Demonstrate DraftKings-only analysis."""
    print("\n" + "="*60)
    print("DRAFTKINGS ONLY ANALYSIS")
    print("="*60)
    
    try:
        # Initialize analyzer with DraftKings filter
        analyzer = NBAOddsAnalyzer(bookmaker_filter='draftkings')
        
        print(f"Bookmaker filter: {analyzer.bookmaker_filter}")
        
        # Get NBA games
        games = analyzer.get_nba_games()
        if not games:
            print("No NBA games found.")
            return
        
        print(f"\nFound {len(games)} NBA games")
        
        # Analyze first game with standard markets
        game = games[0]
        print(f"\nAnalyzing: {game.away_team} @ {game.home_team}")
        
        markets = [NBAMarketKeys.PLAYER_POINTS, NBAMarketKeys.PLAYER_ASSISTS, NBAMarketKeys.PLAYER_REBOUNDS]
        analysis = analyzer.analyze_game_props(game.game_id, markets)
        
        if 'error' not in analysis:
            print(f"\nDraftKings Props Found: {analysis['total_props']}")
            print(f"Best odds combinations: {analysis['best_odds_count']}")
            
            # Show market breakdown
            for market, summary in analysis['market_summary'].items():
                market_name = NBAMarketKeys.get_market_description(market)
                print(f"\n{market_name}:")
                print(f"  Props: {summary['total_props']}")
                print(f"  Players: {summary['unique_players']}")
                print(f"  Bookmakers: {summary['bookmakers']} (should be 1 for DraftKings only)")
        
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error in DraftKings analysis: {e}")


def main():
    """Run all bookmaker filter demonstrations."""
    print("NBA Odds Analyzer - Bookmaker Filter Demonstration")
    print("=" * 60)
    
    # Demo FanDuel only (as requested)
    demo_fanduel_only()
    
    # Demo all bookmakers for comparison
    demo_all_bookmakers()
    
    # Demo another specific bookmaker
    demo_draftkings_only()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETED")
    print("="*60)
    print("\nKey takeaways:")
    print("- FanDuel filter shows only FanDuel odds (bookmakers count = 1)")
    print("- All bookmakers shows odds from multiple sportsbooks")
    print("- You can filter for any specific bookmaker (e.g., 'draftkings', 'betmgm', etc.)")
    print("- Filtering reduces API calls and focuses analysis on preferred sportsbook")


if __name__ == "__main__":
    main()