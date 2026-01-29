# Hexecutioners - Pre-Login Assessment & ML Dropout Prediction

## New System Flow

### User Journey (Non-Authenticated)

1. **User visits website** → Redirected to `/pre-assessment`
2. **Pre-Assessment Form** → User fills comprehensive 20-field assessment form (MANDATORY - no skip option)
3. **ML Model Analysis** → Dropout percentage calculated based on assessment responses
4. **Signup Decision** → Based on ML model result:
   - **Dropout Risk ≤ 80%**: User can proceed to signup → Create account → Login → Dashboard
   - **Dropout Risk > 80%**: Signup disabled → Cannot create account → Must go back to assessment

### User Journey (Authenticated)

1. **User logs in** → Check if post-login assessment exists
2. **If no post-login assessment** → Redirect to `/assessment`
3. **If post-login assessment exists** → Redirect to `/dashboard`

---

## Key Changes Made

### 1. **New ML Model** (`ml_model.py`)
- **File**: `ml_model.py`
- **Core Functions**:
  - `get_dropout_percentage(assessment_data)` - Returns dropout percentage (0-100)
  - `can_user_signup(dropout_percentage)` - Returns boolean: True if ≤80%, False if >80%
  
- **Risk Factors** (Heuristic-based scoring):
  - **High Impact Factors** (15 pts each):
    - Family Health Condition
    - Family Support Level
    - Daily Commitment Capability
  - **Medium Impact Factors**:
    - Clear Reason for Joining (12 pts)
    - Travel Comfort (10 pts)
  - **Low Impact Factors**:
    - Technology Comfort (8 pts)
    - Communication Rating (6 pts)
    - Sports/Physical Comfort (4 pts)
    - Group Activities Interest (5 pts)
    - Education Level (8 pts)

- **Dropout Score Calculation**:
  - Total available points: 100
  - Risk factors subtracted from 100
  - Result: Dropout percentage

### 2. **Pre-Login Assessment Template** (`templates/pre_assessment.html`)
- **Mandatory Form** (No skip option)
- **20 Questions** across 5 sections:
  - Personal Information (Age, 12th Standard, Gender)
  - Family Information (Family size, earning members, education, health, support)
  - Behavioral & Social Skills (Daily chores, group activities, sports/communication comfort, technology comfort)
  - Program Participation & Commitment (Past participation, clear reason, daily commitment, travel comfort)
  - Health & Work Experience (Work experience, physical health condition, program benefit belief)

- **Features**:
  - Progress bar showing form completion
  - Rating scales (1-5) for comfort level questions
  - Radio buttons for yes/no questions
  - Dropdown selections for categorical data
  - Real-time validation
  - Loading indicator during ML analysis

- **Result Display**:
  - Dropout percentage prominently displayed
  - Color-coded results (Green for ≤80%, Red for >80%)
  - Conditional action buttons (Signup or Disabled message)

### 3. **Updated Flask Routes** (`app.py`)

#### New Routes:
- **`GET /pre-assessment`** - Displays pre-login assessment form
- **`POST /submit-pre-login-assessment`** - Processes assessment, runs ML model, returns dropout percentage

#### Modified Routes:
- **`GET /`** - Now redirects to `/pre-assessment` instead of `/login`
- **`GET /signup`** - Now requires pre-assessment completion and checks signup eligibility
- **`POST /signup`** - Saves pre-assessment data to database when user creates account

#### Session Management:
```python
session['pre_assessment_data']  # Stores assessment responses
session['dropout_percentage']   # Stores calculated dropout percentage
session['can_signup']           # Boolean: True/False for signup eligibility
```

### 4. **Updated Signup Template** (`templates/signup.html`)
- Changed footer link from "Login here" to "Back to Assessment"
- Displays error message if `can_signup` is False
- Prompts user to contact support if signup is disabled

### 5. **Updated Requirements** (`requirements.txt`)
- Flask==3.1.2 (upgraded from 3.0.0 for Python 3.14 compatibility)
- Werkzeug==3.1.5 (upgraded from 3.0.0)
- scikit-learn==1.3.2 (for future ML model training)
- joblib==1.3.2 (for model persistence)
- numpy==1.24.3 (ML dependencies)

---

## New Flow Diagram

```
User Visits Website
        ↓
    /pre-assessment (pre_assessment.html)
        ↓
   Fill Form (Mandatory)
        ↓
/submit-pre-login-assessment (ML Model Analysis)
        ↓
   ┌─────────────────────────────────────┐
   │   Calculate Dropout Percentage      │
   │   (0-100)                           │
   └─────────────────────────────────────┘
        ↓
   ┌─────────────────────────────────────┐
   │  Is Dropout % <= 80% ?              │
   └─────────────────────────────────────┘
        ↙                           ↘
      YES                            NO
       ↓                              ↓
   /signup               [Signup Disabled]
   (Enabled)            [Go Back to Form]
       ↓
   Create Account
       ↓
   /login
       ↓
   Dashboard
```

---

## Database Changes

### Pre-Assessment Data Storage

When user signs up after completing pre-assessment:
- Assessment data is stored in `assessments` table with `user_id`
- Post-login assessment (if required) uses same table but checked by checking existing record

### Tables Used:
- **users** - User credentials
- **assessments** - Both pre-login and post-login assessment responses
- **game_scores** - Game performance tracking
- **documents** - Document uploads (Aadhar, Marksheet)

---

## Testing the New Flow

### Test Case 1: User with Good Profile (Dropout < 80%)
1. Go to http://localhost:5000
2. Fill assessment form with favorable responses
3. Submit → Should see "Good Match for Our Program"
4. Click "Proceed to Signup"
5. Create account successfully

### Test Case 2: User with High Risk Profile (Dropout > 80%)
1. Go to http://localhost:5000
2. Fill assessment form with unfavorable responses (e.g., no commitment, no support, etc.)
3. Submit → Should see "High Dropout Risk Detected"
4. Signup button should be disabled
5. User must go back to assessment or contact support

---

## Dropout Percentage Thresholds

- **0-30%**: Excellent profile - Strong commitment indicators
- **31-60%**: Good profile - Some risk factors but manageable
- **61-80%**: Moderate risk - Multiple risk factors present
- **81-100%**: High risk - Significant dropout indicators

---

## Future Enhancements

1. **ML Model Training**: Replace heuristic scoring with trained model
   - Collect real assessment + dropout outcome data
   - Train RandomForestClassifier on historical data
   - Replace heuristic functions with model predictions

2. **Dynamic Thresholds**: Adjust 80% threshold based on program metrics

3. **Risk Mitigation Strategies**: Suggest interventions for high-risk users
   - Mentorship programs
   - Additional support resources
   - Adjusted commitments

4. **Post-Assessment Analytics**: Dashboard for program administrators

---

## Code Examples

### Getting Dropout Percentage
```python
from ml_model import get_dropout_percentage, can_user_signup

assessment_data = {
    'age': '21-23',
    'passed12th': 'yes',
    'gender': 'male',
    'familyMembers': 'less-than-6',
    # ... other fields
}

dropout_percentage = get_dropout_percentage(assessment_data)  # Returns: 45
can_signup = can_user_signup(dropout_percentage)  # Returns: True
```

### Session Management
```python
# Store assessment in session
session['pre_assessment_data'] = assessment_data
session['dropout_percentage'] = 45
session['can_signup'] = True

# Retrieve during signup
if session.get('can_signup'):
    # Allow signup
    # Store assessment_data in database with new user
```

---

## Files Modified

1. ✅ `app.py` - Added new routes and modified signup flow
2. ✅ `ml_model.py` - Created ML prediction model
3. ✅ `templates/pre_assessment.html` - Created new mandatory assessment form
4. ✅ `templates/signup.html` - Updated footer link
5. ✅ `requirements.txt` - Updated dependencies

---

## Important Notes

- **No Skip Option**: Pre-assessment is mandatory before signup
- **Session-Based**: Dropout percentage stored in session, cleared after signup
- **Heuristic-Based**: Currently using weighted risk factors (can be replaced with trained ML model)
- **Threshold: 80%**: Users with dropout risk >80% cannot signup
- **Post-Login Assessment**: Still available after login for users who didn't complete it initially
