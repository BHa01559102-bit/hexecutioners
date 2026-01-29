#!/usr/bin/env python
"""Test script to verify form data structure matches model expectations"""

from ml_model import get_dropout_percentage

# Test candidate data - EXACTLY as per your requirements
new_candidate = {
    "Age": 21,
    "Gender": "male",
    "Family_members": "less than 6",
    "Daily_chores_completion": "sometimes",
    "Group_activities_participation": "interested",
    "Sports_or_team_games": 4,
    "Comfort_talking": 3,
    "Past_program_participation": "no",
    "reason_for_joining": "yes",
    "Family_support": "fully supportive",
    "Commit_daily": "yes",
    "Comfortable_travelling": "yes",
    "Earning_members_in_family": "2",
    "Highest_education_in_family": "high school or equivalent",
    "Severe_health_condition_in_family": "no",
    "Comfortable_using_technology": "yes",
    "Work_experience": "no",
    "Physical_health_condition_affect_participation": "no",
    "Trust_in_program": "strong"
}

print("\n" + "="*100)
print("TEST DATA - EXACT FORMAT FOR MODEL")
print("="*100)
print("\nInput Data Structure:")
for key, value in new_candidate.items():
    print(f"  {key}: {value} (type: {type(value).__name__})")

print("\n" + "="*100)
print("SENDING TO MODEL...")
print("="*100)

dropout_percentage = get_dropout_percentage(new_candidate)

print("\n" + "="*100)
print(f"RESULT: {dropout_percentage}% dropout risk")
print("="*100 + "\n")
