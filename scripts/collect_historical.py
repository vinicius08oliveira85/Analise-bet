#!/usr/bin/env python3
"""
Historical Data Collection Orchestrator
Collects and merges Champions League data from multiple sources.
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import yaml
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalDataCollector:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.raw_dir = Path(self.config['data']['raw_dir'])
        self.processed_dir = Path(self.config['data']['processed_dir'])
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_raw_data(self) -> dict:
        """Load all raw CSV files"""
        data = {}
        files = {
            'matches': 'matches.csv',
            'odds': 'odds.csv',
            'team_stats': 'team_stats.csv'
        }
        
        for key, filename in files.items():
            path = self.raw_dir / filename
            if path.exists():
                data[key] = pd.read_csv(path)
                logger.info(f"Loaded {key}: {len(data[key])} rows")
            else:
                logger.warning(f"File not found: {path}")
                data[key] = pd.DataFrame()
        
        return data
    
    def merge_match_odds(self, matches: pd.DataFrame, odds: pd.DataFrame) -> pd.DataFrame:
        """Merge matches with average odds across bookmakers"""
        # Average odds per match
        odds_avg = odds.groupby('match_id').agg({
            'home_odds': 'mean',
            'draw_odds': 'mean',
            'away_odds': 'mean',
            'over_25': 'mean',
            'over_35': 'mean',
            'btts_yes': 'mean',
            'btts_no': 'mean',
            'ah_home': 'mean',
            'ah_line': 'mean',
            'dc_1x': 'mean',
            'dc_x2': 'mean',
            'dc_12': 'mean',
            'corners_over': 'mean',
            'corners_line': 'mean'
        }).reset_index()
        
        # Add bookmaker count
        bookmaker_count = odds.groupby('match_id')['bookmaker'].nunique().reset_index()
        bookmaker_count.columns = ['match_id', 'bookmaker_count']
        odds_avg = odds_avg.merge(bookmaker_count, on='match_id')
        
        # Merge with matches
        merged = matches.merge(odds_avg, on='match_id', how='left')
        logger.info(f"Merged matches + odds: {len(merged)} matches")
        return merged
    
    def merge_team_stats(self, df: pd.DataFrame, team_stats: pd.DataFrame) -> pd.DataFrame:
        """Merge team stats for home and away teams"""
        # Home team stats
        home_stats = team_stats.copy()
        home_stats.columns = [f'home_{c}' if c not in ['team', 'season', 'matchday'] else c for c in home_stats.columns]
        home_stats = home_stats.rename(columns={'home_team': 'team'})
        
        # Away team stats
        away_stats = team_stats.copy()
        away_stats.columns = [f'away_{c}' if c not in ['team', 'season', 'matchday'] else c for c in away_stats.columns]
        away_stats = away_stats.rename(columns={'away_team': 'team'})
        
        # Merge
        df = df.merge(
            home_stats, 
            left_on=['home_team', 'season', 'matchday'], 
            right_on=['team', 'season', 'matchday'], 
            how='left'
        )
        df = df.merge(
            away_stats, 
            left_on=['away_team', 'season', 'matchday'], 
            right_on=['team', 'season', 'matchday'], 
            how='left'
        )
        
        logger.info(f"Merged team stats: {len(df)} matches")
        return df
    
    def calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived features for modeling"""
        # Result
        df['result'] = np.where(df['home_score'] > df['away_score'], 'H',
                       np.where(df['home_score'] < df['away_score'], 'A', 'D'))
        
        # Total goals
        df['total_goals'] = df['home_score'] + df['away_score']
        df['over_25_result'] = (df['total_goals'] > 2.5).astype(int)
        df['over_35_result'] = (df['total_goals'] > 3.5).astype(int)
        df['btts_result'] = ((df['home_score'] > 0) & (df['away_score'] > 0)).astype(int)
        
        # Goal difference
        df['goal_diff'] = df['home_score'] - df['away_score']
        
        # Implied probabilities from odds (removing vig)
        for col in ['home_odds', 'draw_odds', 'away_odds']:
            if col in df.columns:
                df[f'implied_{col}'] = 1 / df[col]
        
        # Normalize 1X2 implied probs
        total_implied = df['implied_home_odds'] + df['implied_draw_odds'] + df['implied_away_odds']
        df['fair_home_prob'] = df['implied_home_odds'] / total_implied
        df['fair_draw_prob'] = df['implied_draw_odds'] / total_implied
        df['fair_away_prob'] = df['implied_away_odds'] / total_implied
        
        # xG difference
        if 'home_xg' in df.columns and 'away_xg' in df.columns:
            df['xg_diff'] = df['home_xg'] - df['away_xg']
            df['total_xg'] = df['home_xg'] + df['away_xg']
        
        # Form features
        if 'home_form_last5' in df.columns:
            form_map = {'W': 3, 'D': 1, 'L': 0}
            df['home_form_points'] = df['home_form_last5'].apply(
                lambda x: sum(form_map.get(c, 0) for c in str(x)) if pd.notna(x) else 0
            )
            df['away_form_points'] = df['away_form_last5'].apply(
                lambda x: sum(form_map.get(c, 0) for c in str(x)) if pd.notna(x) else 0
            )
            df['form_diff'] = df['home_form_points'] - df['away_form_points']
        
        # xG form features
        if 'home_xg_for_avg' in df.columns:
            df['home_xg_diff'] = df['home_xg_for_avg'] - df['home_xg_against_avg']
            df['away_xg_diff'] = df['away_xg_for_avg'] - df['away_xg_against_avg']
            df['xg_strength_diff'] = df['home_xg_diff'] - df['away_xg_diff']
        
        logger.info(f"Calculated features: {len(df.columns)} columns")
        return df
    
    def generate_model_predictions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate simulated model predictions based on features"""
        np.random.seed(self.config['backtest']['random_seed'])
        
        models = list(self.config['models'].keys())
        predictions = []
        
        for _, match in df.iterrows():
            # Base probabilities from fair odds
            base_probs = {
                'home': match.get('fair_home_prob', 0.4),
                'draw': match.get('fair_draw_prob', 0.3),
                'away': match.get('fair_away_prob', 0.3)
            }
            
            # xG-based adjustment
            xg_diff = match.get('xg_diff', 0)
            xg_adjustment = np.tanh(xg_diff * 0.5) * 0.1  # Max 10% adjustment
            
            for model in models:
                weight = self.config['models'][model]['weight']
                
                # Add model-specific noise
                noise = np.random.normal(0, 0.03, 3)
                
                probs = np.array([base_probs['home'], base_probs['draw'], base_probs['away']])
                probs = probs + xg_adjustment * np.array([1, 0, -1]) + noise
                probs = np.maximum(probs, 0.01)
                probs = probs / probs.sum()
                
                # Over/Under probabilities based on total xG
                total_xg = match.get('total_xg', 2.5)
                over_25_prob = 1 / (1 + np.exp(-(total_xg - 2.5) * 2))
                over_35_prob = 1 / (1 + np.exp(-(total_xg - 3.5) * 2))
                btts_prob = 1 / (1 + np.exp(-(total_xg - 2.0) * 1.5))
                
                # Correct score (simplified)
                home_exp = max(0, round(match.get('home_xg', 1.5)))
                away_exp = max(0, round(match.get('away_xg', 1.0)))
                correct_score = f"{home_exp}-{away_exp}"
                
                predictions.append({
                    'match_id': match['match_id'],
                    'model': model,
                    'home_prob': probs[0],
                    'draw_prob': probs[1],
                    'away_prob': probs[2],
                    'over_25_prob': over_25_prob + np.random.normal(0, 0.02),
                    'over_35_prob': over_35_prob + np.random.normal(0, 0.02),
                    'btts_prob': btts_prob + np.random.normal(0, 0.02),
                    'correct_score': correct_score,
                    'timestamp': datetime.now().isoformat()
                })
        
        pred_df = pd.DataFrame(predictions)
        # Clip probabilities
        prob_cols = ['home_prob', 'draw_prob', 'away_prob', 'over_25_prob', 'over_35_prob', 'btts_prob']
        for col in prob_cols:
            pred_df[col] = pred_df[col].clip(0.01, 0.99)
        
        logger.info(f"Generated predictions: {len(pred_df)} rows for {len(models)} models")
        return pred_df
    
    def process(self, seasons: list = None):
        """Main processing pipeline"""
        if seasons is None:
            seasons = self.config['data']['seasons']
        
        logger.info(f"Processing seasons: {seasons}")
        
        # Load raw data
        raw_data = self.load_raw_data()
        
        # Filter by season
        matches = raw_data['matches']
        if 'season' in matches.columns:
            matches = matches[matches['season'].isin(seasons)].copy()
        
        # Merge odds
        df = self.merge_match_odds(matches, raw_data['odds'])
        
        # Merge team stats
        df = self.merge_team_stats(df, raw_data['team_stats'])
        
        # Calculate features
        df = self.calculate_features(df)
        
        # Generate model predictions
        predictions = self.generate_model_predictions(df)
        
        # Save processed data
        output_path = self.processed_dir / 'matches_processed.csv'
        df.to_csv(output_path, index=False)
        logger.info(f"Saved processed matches: {output_path}")
        
        pred_path = self.processed_dir / 'model_predictions.csv'
        predictions.to_csv(pred_path, index=False)
        logger.info(f"Saved model predictions: {pred_path}")
        
        # Save train/test splits
        train_seasons = self.config['backtest']['train_seasons']
        test_seasons = self.config['backtest']['test_seasons']
        
        train_df = df[df['season'].isin(train_seasons)]
        test_df = df[df['season'].isin(test_seasons)]
        
        train_df.to_csv(self.processed_dir / 'train.csv', index=False)
        test_df.to_csv(self.processed_dir / 'test.csv', index=False)
        
        train_pred = predictions[predictions['match_id'].isin(train_df['match_id'])]
        test_pred = predictions[predictions['match_id'].isin(test_df['match_id'])]
        
        train_pred.to_csv(self.processed_dir / 'train_predictions.csv', index=False)
        test_pred.to_csv(self.processed_dir / 'test_predictions.csv', index=False)
        
        logger.info(f"Train: {len(train_df)} matches, Test: {len(test_df)} matches")
        
        return df, predictions


def main():
    parser = argparse.ArgumentParser(description="Collect and process historical CL data")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--seasons", nargs="+", type=int, help="Seasons to process")
    args = parser.parse_args()
    
    collector = HistoricalDataCollector(args.config)
    collector.process(args.seasons)
    logger.info("Data collection complete!")


if __name__ == "__main__":
    main()