# Frontend Data Logging - Testing Guide

## Overview
The application now logs detailed information at three stages:
1. **Raw Frontend Data** - What the form submits
2. **Mapped Model Features** - After form fields are mapped to model features
3. **Final DataFrame** - The exact dataframe sent to LightGBM model

---

## Testing Steps

### 1. Access the Pre-Assessment Form
- Open your browser and go to: **http://127.0.0.1:5000/pre-assessment**

### 2. Fill Out the Form
Fill in all fields with test data (example):
- **Name**: John Doe
- **Contact Number**: 9876543210
- **Email**: john@example.com
- **Address**: 123 Test Street
- **How did you know**: Friend/Family
- **Age**: 21
- **Gender**: Male
- **Passed 12th**: Yes
- **Family Members**: less than 6
- **Earning Members**: 2
- **Highest Education**: high school or equivalent
- **Family Health**: No
- **Family Support**: fully supportive
- **Daily Chores**: sometimes
- **Group Activities**: interested
- **Sports Rating**: 4
- **Communication Rating**: 3
- **Technology Comfort**: yes
- **Past Program**: no
- **Reason for Joining**: yes
- **Daily Commitment**: yes
- **Travel Comfort**: yes
- **Work Experience**: no
- **Health Condition**: no
- **Trust in Program**: strong

### 3. Submit the Form
Click the "Submit" button on the form.

### 4. Check Terminal Output
Look at the Flask app terminal for three detailed output sections:

#### **SECTION 1: Frontend Data**
```
====================================================================================================
FRONTEND DATA RECEIVED - RAW JSON:
====================================================================================================
{
  "full_name": "John Doe",
  "contact_number": "9876543210",
  "email": "john@example.com",
  ... (all form fields in exact frontend format)
}
====================================================================================================
```

#### **SECTION 2: ML Model - Raw Data**
```
====================================================================================================
ML MODEL - RAW ASSESSMENT DATA RECEIVED FROM FRONTEND:
====================================================================================================
  full_name: John Doe (type: str)
  contact_number: 9876543210 (type: str)
  ... (each field with its type)
====================================================================================================
```

#### **SECTION 3: ML Model - Mapped Features**
```
====================================================================================================
ML MODEL - DATA AFTER MAPPING TO MODEL FEATURES:
====================================================================================================
  Age: 21 (type: int)
  Gender: male (type: str)
  Family_members: less than 6 (type: str)
  ... (19 model features with correct types)
====================================================================================================
```

#### **SECTION 4: DataFrame Sent to Model**
```
====================================================================================================
DATAFRAME SENT TO MODEL:
====================================================================================================
   Age Gender Family_members Daily_chores_completion  ...
0   21   male    less than 6               sometimes  ...

DataFrame Shape: (1, 19)
DataTypes:
Age                        int64
Gender                   category
Family_members           category
... (all 19 features)
====================================================================================================
```

---

## What Each Section Shows

### Frontend Data Section
- **Shows**: Raw JSON exactly as sent by the HTML form
- **Used for**: Verifying the form is collecting correct data
- **Check**: Are all expected fields present? Are values correct?

### Raw Assessment Data Section
- **Shows**: Data received by ml_model.py before processing
- **Used for**: Seeing if the form data reaches the model unchanged
- **Check**: Are types correct? Are any values missing or malformed?

### Mapped Features Section
- **Shows**: Data after field name mapping (e.g., `age` → `Age`)
- **Used for**: Ensuring form fields are correctly mapped to model features
- **Check**: Do all 19 model features have values? Are types correct?

### DataFrame Section
- **Shows**: Exact dataframe sent to LightGBM model
- **Used for**: Verifying categories are correctly set and types are proper
- **Check**: Are all values properly categorized? Are numeric columns int/float?

---

## Data Flow Diagram

```
HTML Form (pre_assessment.html)
        ↓
Frontend JavaScript collects data
        ↓
POST /submit-pre-assessment
        ↓
[LOGS SECTION 1: Frontend Data] ← See raw JSON here
        ↓
app.py passes to get_dropout_percentage()
        ↓
ml_model.py receives data
        ↓
[LOGS SECTION 2: Raw Assessment Data] ← See unprocessed data here
        ↓
_prepare_data_for_prediction() maps fields
        ↓
[LOGS SECTION 3: Mapped Features] ← See mapped data here
        ↓
_prepare_single_row() creates DataFrame
        ↓
[LOGS SECTION 4: DataFrame] ← See final DataFrame here
        ↓
LightGBM model.predict_proba()
        ↓
Dropout percentage calculated
        ↓
Result sent back to frontend
```

---

## Key Field Mappings

| Frontend Form Field | Model Feature | Type | Expected Values |
|-------------------|---|---|---|
| age | Age | int | 18-25 |
| gender | Gender | str/cat | female, male, other |
| family_members | Family_members | str/cat | 10 or more, less than 4, less than 6, less than 9 |
| daily_chores | Daily_chores_completion | str/cat | always, never, sometimes |
| group_activities | Group_activities_participation | str/cat | interested, neutral, not interested |
| sports_rating | Sports_or_team_games | int/cat | 1, 2, 3, 4, 5 |
| communication_rating | Comfort_talking | int/cat | 1, 2, 3, 4, 5 |
| past_program | Past_program_participation | str/cat | no, yes |
| reason_for_joining | reason_for_joining | str/cat | maybe, no, yes |
| family_support | Family_support | str/cat | fully supportive, not supportive, somewhat supportive |
| daily_commitment | Commit_daily | str/cat | maybe, no, yes |
| travel_comfort | Comfortable_travelling | str/cat | maybe, no, yes |
| earning_members | Earning_members_in_family | str/cat | 1, 2, 3 or more |
| highest_education | Highest_education_in_family | str/cat | college and higher, high school or equivalent, no formal education |
| family_health | Severe_health_condition_in_family | str/cat | no, yes |
| technology_comfort | Comfortable_using_technology | str/cat | no, somewhat, yes |
| work_experience | Work_experience | str/cat | no, yes |
| health_condition | Physical_health_condition_affect_participation | str/cat | I have a minor condition..., no, yes |
| trust_in_program | Trust_in_program | str/cat | neutral, strong, weak |

---

## Troubleshooting

### If you see NaN values in the DataFrame
- Check if the value matches the expected categories exactly
- Values are case-sensitive
- Extra spaces may cause NaN values

### If a field is missing from the DataFrame
- Check if the form is collecting that field
- Verify the field name in the form matches the mapping in ml_model.py

### If the model returns an error
- Check the Mapped Features section to see if all 19 features are present
- Ensure no numeric strings are being treated as categories

---

## Quick Reference: Terminal Output Sections

To find the logging output, search for these markers in the Flask terminal:

1. `FRONTEND DATA RECEIVED - RAW JSON:`
2. `ML MODEL - RAW ASSESSMENT DATA RECEIVED FROM FRONTEND:`
3. `ML MODEL - DATA AFTER MAPPING TO MODEL FEATURES:`
4. `DATAFRAME SENT TO MODEL:`

Each section is clearly marked with `====` separators for easy identification.
