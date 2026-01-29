#!/usr/bin/env python
"""Test script for ML model prediction with sample data - DEBUG VERSION"""

# Suppress Flask warnings
import sys
import os
os.environ['FLASK_ENV'] = 'development'

from ml_model import get_dropout_percentage

# Test candidate data - matches the exact format you provided
new_candidate = {
    'age': 21,
    'gender': 'male',
    'family_members': 'less than 6',
    'daily_chores': 'sometimes',
    'group_activities': 'interested',
    'sports_rating': 4,
    'communication_rating': 3,
    'past_program': 'no',
    'reason_for_joining': 'yes',
    'family_support': 'fully supportive',
    'daily_commitment': 'yes',
    'travel_comfort': 'yes',
    'earning_members': '2',
    'highest_education': 'high school or equivalent',
    'family_health': 'no',
    'technology_comfort': 'yes',
    'work_experience': 'no',
    'health_condition': 'no',
    'trust_in_program': 'strong'
}

print("\n" + "="*80)
print("ML MODEL TEST WITH SAMPLE CANDIDATE DATA - DEBUG VERSION")
print("="*80)
print("\nInput Data:")
for key, value in new_candidate.items():
    print(f"  {key}: {value}")

print("\n" + "-"*80)
dropout_percentage = get_dropout_percentage(new_candidate)
print("-"*80)

print(f"\n✓ FINAL RESULT: {dropout_percentage}% dropout risk")
if dropout_percentage <= 70:
    print("  Status: ✓ ELIGIBLE - Can proceed with signup")
else:
    print("  Status: ✗ NOT ELIGIBLE - Dropout risk too high")
print("="*80 + "\n")
