"""
Dropout Prediction Model using LightGBM
Predicts the likelihood of a student dropping out based on their assessment responses
"""

import joblib
import pandas as pd
import os
from pathlib import Path

class DropoutPredictor:
    """ML model for predicting student dropout probability using LightGBM"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.cat_cols = None
        self.num_cols = None
        self.category_levels = None
        self._load_model()
    
    def _load_model(self):
        """Load the LightGBM model bundle"""
        bundle_path = Path('dropout_lgbm_bundle (1).pkl')
        
        if bundle_path.exists():
            try:
                bundle = joblib.load(str(bundle_path))
                self.model = bundle.get("model")
                self.feature_columns = bundle.get("feature_columns")
                self.cat_cols = bundle.get("cat_cols")
                self.num_cols = bundle.get("num_cols")
                self.category_levels = bundle.get("category_levels")
                print("[OK] LightGBM model loaded successfully")
            except Exception as e:
                print(f"Error loading LightGBM model: {e}")
                self.model = None
        else:
            print(f"[WARN] Model bundle not found at {bundle_path}")
            self.model = None
    
    def _prepare_data_for_prediction(self, assessment_data):
        """
        Prepare assessment data for model prediction
        Maps form data to model's expected format
        
        Expects data to come with model feature names directly:
        - Age (int): 18-25
        - Gender (str): female, male, other
        - Family_members (str): 10 or more, less than 4, less than 6, less than 9
        - Daily_chores_completion (str): always, never, sometimes
        - Group_activities_participation (str): interested, neutral, not interested
        - Sports_or_team_games (int): 1, 2, 3, 4, 5
        - Comfort_talking (int): 1, 2, 3, 4, 5
        - Past_program_participation (str): no, yes
        - reason_for_joining (str): maybe, no, yes
        - Family_support (str): fully supportive, not supportive, somewhat supportive
        - Commit_daily (str): maybe, no, yes
        - Comfortable_travelling (str): maybe, no, yes
        - Earning_members_in_family (str): 1, 2, 3 or more
        - Highest_education_in_family (str): college and higher, high school or equivalent, no formal education
        - Severe_health_condition_in_family (str): no, yes
        - Comfortable_using_technology (str): no, somewhat, yes
        - Work_experience (str): no, yes
        - Physical_health_condition_affect_participation (str): I have a minor condition..., no, yes
        - Trust_in_program (str): neutral, strong, weak
        """
        # Expected model feature columns
        model_features = [
            'Age',
            'Gender',
            'Family_members',
            'Daily_chores_completion',
            'Group_activities_participation',
            'Sports_or_team_games',
            'Comfort_talking',
            'Past_program_participation',
            'reason_for_joining',
            'Family_support',
            'Commit_daily',
            'Comfortable_travelling',
            'Earning_members_in_family',
            'Highest_education_in_family',
            'Severe_health_condition_in_family',
            'Comfortable_using_technology',
            'Work_experience',
            'Physical_health_condition_affect_participation',
            'Trust_in_program'
        ]
        
        # Create row dict with values directly from assessment data
        # Data is expected to already have model feature names
        row_dict = {}
        for feature in model_features:
            value = assessment_data.get(feature)
            if value is not None:
                # Age is numeric, keep as int
                if feature == 'Age':
                    row_dict[feature] = int(value) if isinstance(value, str) else value
                # Sports and Comfort_talking are numeric categories
                elif feature in ['Sports_or_team_games', 'Comfort_talking']:
                    row_dict[feature] = int(value) if isinstance(value, str) else value
                # Earning_members_in_family should be string
                elif feature == 'Earning_members_in_family':
                    row_dict[feature] = str(value).strip()
                # All other categorical fields are strings
                else:
                    row_dict[feature] = str(value).strip()
        
        return row_dict
    
    def _prepare_single_row(self, row_dict):
        """
        Create single-row dataframe in the correct column order
        with proper data types and categories
        """
        try:
            # Create dataframe with all feature columns in correct order
            X_new = pd.DataFrame([row_dict], columns=self.feature_columns)
            
            print(f"\nDEBUG: Initial row_dict keys: {row_dict.keys()}")
            print(f"DEBUG: Feature columns expected: {self.feature_columns}")
            print(f"DEBUG: Numeric columns: {self.num_cols}")
            print(f"DEBUG: Categorical columns: {self.cat_cols}")
            
            # Ensure numeric cols are numeric
            for c in self.num_cols:
                if c in X_new.columns:
                    X_new[c] = pd.to_numeric(X_new[c], errors="coerce")
            
            # Ensure categorical cols have the SAME categories as training
            for c in self.cat_cols:
                if c in X_new.columns:
                    current_value = X_new[c].iloc[0]
                    expected_categories = self.category_levels.get(c, [])
                    
                    # For numeric categories (like 1, 2, 3, 4, 5), ensure value is an int
                    if isinstance(expected_categories, list) and len(expected_categories) > 0:
                        if isinstance(expected_categories[0], int):
                            X_new[c] = pd.to_numeric(X_new[c], errors="coerce")
                            current_value = X_new[c].iloc[0]
                    
                    print(f"DEBUG: Column '{c}' - Current value: {current_value} (type: {type(current_value).__name__}), Expected categories: {expected_categories}")
                    
                    X_new[c] = X_new[c].astype("category")
                    X_new[c] = X_new[c].cat.set_categories(expected_categories)
            
            return X_new
        except Exception as e:
            print(f"Error preparing data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def predict_dropout_percentage(self, assessment_data):
        """
        Predict dropout percentage based on assessment responses
        Returns: dropout_percentage (0-100)
        """
        
        try:
            # Log raw input data
            print("\n" + "="*100)
            print("ML MODEL - RAW ASSESSMENT DATA RECEIVED FROM FRONTEND:")
            print("="*100)
            for key, value in assessment_data.items():
                print(f"  {key}: {value} (type: {type(value).__name__})")
            print("="*100 + "\n")
            
            # Prepare data
            row_dict = self._prepare_data_for_prediction(assessment_data)
            
            print("\n" + "="*100)
            print("ML MODEL - DATA AFTER MAPPING TO MODEL FEATURES:")
            print("="*100)
            for key, value in row_dict.items():
                print(f"  {key}: {value} (type: {type(value).__name__})")
            print("="*100 + "\n")
            
            X_new = self._prepare_single_row(row_dict)
            
            print("\n" + "="*100)
            print("DATAFRAME SENT TO MODEL:")
            print("="*100)
            pd.set_option("display.max_columns", None)
            pd.set_option("display.width", None)
            print(X_new)
            print("\nDataFrame Shape:", X_new.shape)
            print("DataTypes:")
            print(X_new.dtypes)
            print("="*100 + "\n")
            
            # Get probability of dropout (class 1)
            dropout_prob = self.model.predict_proba(X_new)[:, 1][0]
            dropout_percentage = int(dropout_prob * 100)
            
            print(f"ML Model Prediction: {dropout_percentage}% dropout risk")
            return dropout_percentage
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            import traceback
            traceback.print_exc()
            return 50  # Default middle value on error
           
    
   
    def can_signup(self, dropout_percentage, threshold=100):
        """
        Determine if user can signup based on dropout percentage
        Returns False if dropout_percentage > threshold (default 70%)
        """
        return dropout_percentage <= threshold


# Initialize global predictor instance
predictor = DropoutPredictor()


def get_dropout_percentage(assessment_data):
    """Public function to get dropout percentage"""
    return predictor.predict_dropout_percentage(assessment_data)


def can_user_signup(dropout_percentage, threshold=70):
    """Public function to check if user can signup (>70% = not eligible)"""
    return predictor.can_signup(dropout_percentage, threshold)
