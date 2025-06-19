#!/usr/bin/env python3
"""
NBA Odds Analyzer - Example Usage

This script demonstrates how to use the NBA Odds Analyzer with different
market keys and analysis scenarios.

Author: NBA Playoffs Analysis Tool
Version: 1.0.0
Last Updated: 2025-01-15
"""

import sys
import json
from datetime import datetime
from nba_odds_analyzer import NBAOddsAnalyzer, NBAMarketKeys


def example_basic_analysis():
    """Example: Basic analysis using standard markets (FanDuel only)."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Analysis with Standard Markets (FanDuel Only)")
    print("="*60)
    
    try:
        analyzer = NBAOddsAnalyzer(bookmaker_filter='fanduel')
        
        # Get NBA games
        games = analyzer.get_nba_games()
        if not games:
            print("No NBA games available for analysis.")
            return
        
        # Use standard markets
        markets = NBAMarketKeys.get_standard_markets()
        print(f"Analyzing markets: {', '.join(markets)}")
        
        # Analyze first game
        game = games[0]
        print(f"\nGame: {game.away_team} @ {game.home_team}")
        
        analysis = analyzer.analyze_game_props(game.game_id, markets)
        
        if 'error' not in analysis:
            print(f"Total props found: {analysis['total_props']}")
            print(f"Best odds combinations: {analysis['best_odds_count']}")
            
            # Show market breakdown
            for market, summary in analysis['market_summary'].items():
                market_name = NBAMarketKeys.get_market_description(market)
                print(f"  {market_name}: {summary['total_props']} props, {summary['unique_players']} players")
            
            # Save data to CSV
            print("\nSaving basic analysis data to CSV...")
            all_props = analysis['all_props']
            best_odds = analysis['best_odds']
            
            props_filename = analyzer.save_props_to_csv(all_props, "basic_analysis_props.csv")
            best_odds_filename = analyzer.save_best_odds_to_csv(best_odds, "basic_analysis_best_odds.csv")
        
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error in basic analysis: {e}")


def example_alternate_markets():
    """Example: Analysis using alternate markets (FanDuel only)."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Analysis with Alternate Markets (FanDuel Only)")
    print("="*60)
    
    try:
        analyzer = NBAOddsAnalyzer(bookmaker_filter='fanduel')
        
        # Get NBA games
        games = analyzer.get_nba_games()
        if not games:
            print("No NBA games available for analysis.")
            return
        
        # Use alternate markets
        markets = [
            NBAMarketKeys.PLAYER_POINTS_ALTERNATE,
            NBAMarketKeys.PLAYER_REBOUNDS_ALTERNATE,
            NBAMarketKeys.PLAYER_ASSISTS_ALTERNATE,
            NBAMarketKeys.PLAYER_THREES_ALTERNATE
        ]
        
        print(f"Analyzing alternate markets: {', '.join(markets)}")
        
        # Analyze first game
        game = games[0]
        print(f"\nGame: {game.away_team} @ {game.home_team}")
        
        analysis = analyzer.analyze_game_props(game.game_id, markets)
        
        if 'error' not in analysis:
            print(f"Total alternate props found: {analysis['total_props']}")
            
            # Show some sample props
            if analysis['all_props']:
                print("\nSample Alternate Props:")
                for prop in analysis['all_props'][:10]:  # Show first 10
                    print(f"  {prop.player_name} - {prop.market_name}")
                    print(f"    {prop.outcome} {prop.point}: {prop.price:+d} ({prop.bookmaker})")
        
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error in alternate markets analysis: {e}")


def example_combination_props():
    """Example: Analysis using combination prop markets (FanDuel only)."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Analysis with Combination Props (FanDuel Only)")
    print("="*60)
    
    try:
        analyzer = NBAOddsAnalyzer(bookmaker_filter='fanduel')
        
        # Get NBA games
        games = analyzer.get_nba_games()
        if not games:
            print("No NBA games available for analysis.")
            return
        
        # Use combination markets
        markets = [
            NBAMarketKeys.PLAYER_POINTS_ASSISTS_ALTERNATE,
            NBAMarketKeys.PLAYER_POINTS_REBOUNDS_ALTERNATE,
            NBAMarketKeys.PLAYER_REBOUNDS_ASSISTS_ALTERNATE,
            NBAMarketKeys.PLAYER_POINTS_REBOUNDS_ASSISTS_ALTERNATE
        ]
        
        print(f"Analyzing combination markets: {', '.join(markets)}")
        
        # Analyze first game
        game = games[0]
        print(f"\nGame: {game.away_team} @ {game.home_team}")
        
        analysis = analyzer.analyze_game_props(game.game_id, markets)
        
        if 'error' not in analysis:
            print(f"Total combination props found: {analysis['total_props']}")
            
            # Show market breakdown
            for market, summary in analysis['market_summary'].items():
                market_name = NBAMarketKeys.get_market_description(market)
                print(f"  {market_name}:")
                print(f"    Props: {summary['total_props']}")
                print(f"    Players: {summary['unique_players']}")
                print(f"    Bookmakers: {summary['bookmakers']}")
        
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error in combination props analysis: {e}")


def example_comprehensive_analysis():
    """Example: Comprehensive analysis using all available markets (FanDuel only)."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Comprehensive Analysis (All Markets) (FanDuel Only)")
    print("="*60)
    
    try:
        analyzer = NBAOddsAnalyzer(bookmaker_filter='fanduel')
        
        # Get NBA games
        games = analyzer.get_nba_games()
        if not games:
            print("No NBA games available for analysis.")
            return
        
        # Use all available markets
        markets = NBAMarketKeys.get_all_markets()
        print(f"Analyzing ALL {len(markets)} available markets")
        
        # Analyze first game
        game = games[0]
        print(f"\nGame: {game.away_team} @ {game.home_team}")
        
        analysis = analyzer.analyze_game_props(game.game_id, markets)
        
        if 'error' not in analysis:
            print(f"\nComprehensive Analysis Results:")
            print(f"Total props found: {analysis['total_props']}")
            print(f"Best odds combinations: {analysis['best_odds_count']}")
            
            print("\nDetailed Market Breakdown:")
            for market, summary in analysis['market_summary'].items():
                market_name = NBAMarketKeys.get_market_description(market)
                print(f"  {market_name}:")
                print(f"    Props: {summary['total_props']}")
                print(f"    Players: {summary['unique_players']}")
                print(f"    Bookmakers: {summary['bookmakers']}")
            
            # Find best value props (highest odds)
            if analysis['all_props']:
                sorted_props = sorted(analysis['all_props'], key=lambda x: x.price, reverse=True)
                print("\nTop 5 Highest Odds Props:")
                for prop in sorted_props[:5]:
                    print(f"  {prop.player_name} - {prop.market_name}")
                    print(f"    {prop.outcome} {prop.point}: {prop.price:+d} ({prop.bookmaker})")
            
            # Save comprehensive data to CSV
            print("\nSaving comprehensive analysis data to CSV...")
            all_props = analysis['all_props']
            best_odds = analysis['best_odds']
            
            props_filename = analyzer.save_props_to_csv(all_props, "comprehensive_analysis_props.csv")
            best_odds_filename = analyzer.save_best_odds_to_csv(best_odds, "comprehensive_analysis_best_odds.csv")
        
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error in comprehensive analysis: {e}")


def example_specific_player_focus():
    """Example: Focus on specific players across all markets (FanDuel only)."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Player-Focused Analysis (FanDuel Only)")
    print("="*60)
    
    try:
        analyzer = NBAOddsAnalyzer(bookmaker_filter='fanduel')
        
        # Get NBA games
        games = analyzer.get_nba_games()
        if not games:
            print("No NBA games available for analysis.")
            return
        
        # Use standard markets for player focus
        markets = NBAMarketKeys.get_standard_markets()
        
        # Analyze first game
        game = games[0]
        print(f"Game: {game.away_team} @ {game.home_team}")
        
        props = analyzer.get_player_props(game.game_id, markets)
        
        if props:
            # Group props by player
            player_props = {}
            for prop in props:
                if prop.player_name not in player_props:
                    player_props[prop.player_name] = []
                player_props[prop.player_name].append(prop)
            
            print(f"\nFound props for {len(player_props)} players")
            
            # Show detailed breakdown for first few players
            for i, (player, player_prop_list) in enumerate(list(player_props.items())[:3]):
                print(f"\n{i+1}. {player}:")
                
                # Group by market
                market_groups = {}
                for prop in player_prop_list:
                    if prop.market_key not in market_groups:
                        market_groups[prop.market_key] = []
                    market_groups[prop.market_key].append(prop)
                
                for market, market_props in market_groups.items():
                    market_name = NBAMarketKeys.get_market_description(market)
                    print(f"   {market_name}:")
                    
                    # Find best odds for Over/Under
                    over_props = [p for p in market_props if p.outcome == 'Over']
                    under_props = [p for p in market_props if p.outcome == 'Under']
                    
                    if over_props:
                        best_over = max(over_props, key=lambda x: x.price)
                        print(f"     Best Over {best_over.point}: {best_over.price:+d} ({best_over.bookmaker})")
                    
                    if under_props:
                        best_under = max(under_props, key=lambda x: x.price)
                        print(f"     Best Under {best_under.point}: {best_under.price:+d} ({best_under.bookmaker})")
            
            # Save player-focused data to CSV
            print("\nSaving player-focused analysis data to CSV...")
            props_filename = analyzer.save_props_to_csv(props, "player_focused_analysis.csv")
            
            # Also save data for the first player as an example
            if player_props:
                first_player = list(player_props.keys())[0]
                first_player_props = player_props[first_player]
                player_filename = f"{first_player.replace(' ', '_').lower()}_props.csv"
                analyzer.save_props_to_csv(first_player_props, player_filename)
                print(f"Individual player data saved for: {first_player}")
        
        analyzer.print_usage_stats()
        
    except Exception as e:
        print(f"Error in player-focused analysis: {e}")


def show_available_markets():
    """Display all available NBA market keys."""
    print("\n" + "="*60)
    print("AVAILABLE NBA MARKET KEYS")
    print("="*60)
    
    print("\nStandard Markets:")
    for market in NBAMarketKeys.get_standard_markets():
        description = NBAMarketKeys.get_market_description(market)
        print(f"  {market:<30} - {description}")
    
    print("\nAlternate Markets:")
    alternate_markets = [
        NBAMarketKeys.PLAYER_POINTS_ALTERNATE,
        NBAMarketKeys.PLAYER_REBOUNDS_ALTERNATE,
        NBAMarketKeys.PLAYER_ASSISTS_ALTERNATE,
        NBAMarketKeys.PLAYER_BLOCKS_ALTERNATE,
        NBAMarketKeys.PLAYER_STEALS_ALTERNATE,
        NBAMarketKeys.PLAYER_TURNOVERS_ALTERNATE,
        NBAMarketKeys.PLAYER_THREES_ALTERNATE
    ]
    
    for market in alternate_markets:
        description = NBAMarketKeys.get_market_description(market)
        print(f"  {market:<35} - {description}")
    
    print("\nCombination Markets:")
    combination_markets = [
        NBAMarketKeys.PLAYER_POINTS_ASSISTS_ALTERNATE,
        NBAMarketKeys.PLAYER_POINTS_REBOUNDS_ALTERNATE,
        NBAMarketKeys.PLAYER_REBOUNDS_ASSISTS_ALTERNATE,
        NBAMarketKeys.PLAYER_POINTS_REBOUNDS_ASSISTS_ALTERNATE
    ]
    
    for market in combination_markets:
        description = NBAMarketKeys.get_market_description(market)
        print(f"  {market:<40} - {description}")
    
    print(f"\nTotal Available Markets: {len(NBAMarketKeys.get_all_markets())}")


def main():
    """Run all example scenarios."""
    print("NBA Odds Analyzer - Example Usage Scenarios")
    print("=" * 60)
    
    # Show available markets first
    show_available_markets()
    
    # Run example scenarios
    try:
        example_basic_analysis()
        example_alternate_markets()
        example_combination_props()
        example_specific_player_focus()
        # example_comprehensive_analysis()  # Commented out to save API calls
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()