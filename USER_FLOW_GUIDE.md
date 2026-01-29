# User Flow - New Implementation

## Home Page Flow (http://127.0.0.1:5000)

### **Landing Page** ✅
When user visits the home page, they see:

```
┌─────────────────────────────────────┐
│     🚀 Welcome to Hexecutioners    │
│                                    │
│  Empower your future through our   │
│  skill development program         │
│                                    │
│  ┌──────────────────────────────┐  │
│  │  I'm a New User      [→]     │  │
│  └──────────────────────────────┘  │
│                                    │
│  ┌──────────────────────────────┐  │
│  │ I Already Have an Account [→]│  │
│  └──────────────────────────────┘  │
│                                    │
│ Join thousands of students...      │
│                                    │
│ Language: [English ▼]              │
└─────────────────────────────────────┘
```

---

## **Path 1: New User → Pre-Assessment → Signup**

### Step 1: Click "I'm a New User"
- Routes to: `/pre-assessment`
- Shows: Full assessment form with 19 questions
- ML Model: Evaluates dropout risk

### Step 2: Complete Assessment
- Form submits data to: `/submit-pre-assessment`
- ML Model processes and returns: dropout_percentage
- Shows results screen with:
  - ✅ Dropout percentage (0-100%)
  - ✅ Eligibility status
  - ✅ "Proceed to Signup" button (if eligible)

### Step 3: Click "Proceed to Signup"
- Routes to: `/signup`
- Shows: Signup form
  - Username (NEW - unique validation)
  - Email (unique validation)
  - Password
  - Confirm Password

### Step 4: Signup
- **Validates**:
  - Passwords match
  - Username is unique (NOW FIXED ✅)
  - Email is unique (NOW FIXED ✅)
- **If valid**: Creates user account → redirects to login
- **If invalid**: Shows error message

---

## **Path 2: Returning User → Login**

### Step 1: Click "I Already Have an Account"
- Routes to: `/login`
- Shows: Login form
  - Username or Email
  - Password
  - "Forgot Password?" link

### Step 2: Login
- Authenticates user
- Redirects to: `/dashboard`

---

## **Bug Fixes Applied** ✅

### 1. **Duplicate User Issue - FIXED**
**Before:**
```python
# Tried to insert first, then caught IntegrityError
try:
    conn.execute('INSERT INTO users ...')  # Could fail
except sqlite3.IntegrityError:
    # Then showed error
```

**After:**
```python
# Check BEFORE attempting insert
existing_user = conn.execute(
    'SELECT id FROM users WHERE username = ? OR email = ?', 
    (username, email)
).fetchone()

if existing_user:
    # Show error immediately
    return render_template('signup.html', error='User exists')
```

### 2. **Home Page Navigation - FIXED**
**Before:**
- Home page redirected to `/pre-assessment`
- Couldn't choose between new/returning user
- No way to access login page

**After:**
- Home page shows welcome page with buttons
- "New User" → Pre-assessment flow
- "Returning User" → Login flow

---

## **Testing the New Flow**

### Test New User:
1. Go to: http://127.0.0.1:5000
2. Click "I'm a New User"
3. Complete pre-assessment (all 19 questions)
4. Click "Proceed to Signup"
5. Enter:
   - Username: `testuser1`
   - Email: `test@example.com`
   - Password: `password123`
   - Confirm: `password123`
6. ✅ Should create account successfully

### Test Duplicate Prevention:
1. Try to signup with same username
2. ✅ Should see error: "User already exists"

### Test Returning User:
1. Go to: http://127.0.0.1:5000
2. Click "I Already Have an Account"
3. Enter existing credentials
4. ✅ Should login successfully

---

## **Database Structure**

```
users table:
├── id (PK)
├── username (UNIQUE) ✓
├── email (UNIQUE) ✓
└── password

assessments table:
├── id (PK)
├── user_id (FK)
├── Age
├── Gender
├── ...19 model features...
└── completed_at
```

---

## **Multi-Language Support** 🌐

All pages support:
- English (EN)
- हिंदी (HI)
- ಕನ್ನಡ (KN)

Language preference is saved in localStorage and persists across pages.

---

## **File Changes Summary**

### New Files:
- `templates/welcome.html` - Landing page with new/returning user buttons

### Modified Files:
- `app.py` - Updated `/` route to show welcome page
- `app.py` - Fixed `/signup` to check duplicates before insert

### No Changes Needed:
- `pre_assessment.html` - Still works as-is
- `signup.html` - Still works as-is
- `login.html` - Still works as-is
