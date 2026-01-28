# Hexecutioners - Student Engagement Platform

## Overview
A Flask-based web application designed to increase student retention during wait times before class sessions. Features mini-games, profile management, and document upload functionality.

## Features
- **User Authentication**: Secure login and signup with password hashing
- **Mini Games**: 3 engaging games (Number Guess, Memory Match, Quick Trivia)
- **Score Tracking**: Track best scores for each game
- **User Profile**: Complete profile with user details
- **Document Upload**: Upload and manage documents (Profile Picture, Signature, Aadhar Card, 12th Marksheet)
- **Dashboard**: Central hub with game links and score display

## Tech Stack
- **Backend**: Flask 3.0.0
- **Database**: SQLite3
- **Frontend**: HTML, CSS, JavaScript
- **Security**: Werkzeug for password hashing

## Installation

### Prerequisites
- Python 3.14+
- pip

### Setup
1. Clone the repository
2. Navigate to the project directory
3. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and go to `http://localhost:5000`

## Project Structure
```
Hexecutioners/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── users.db              # SQLite database
├── templates/            # HTML templates
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── games.html
│   ├── number_guess.html
│   ├── memory.html
│   └── trivia.html
├── uploads/              # User document uploads
└── .venv/               # Virtual environment
```

## Games

### 1. Number Guess Game
- Guess a secret number between 1-100
- 10 attempts limit
- Score based on attempts used
- Instant feedback (too high/too low)

### 2. Memory Match Game
- Match emoji pairs from 16 cards
- Track moves and time taken
- Score based on speed and efficiency
- 8 matches required to win

### 3. Quick Trivia
- 5 general knowledge questions
- Multiple choice answers
- 20 points per correct answer
- Accuracy tracking

## Database Schema

### Users Table
- id: Primary key
- username: Unique username
- email: Unique email
- password: Hashed password

### Game Scores Table
- id: Primary key
- user_id: Foreign key to users
- game_name: Name of the game
- score: Score achieved
- created_at: Timestamp

### Documents Table
- id: Primary key
- user_id: Foreign key to users
- document_type: Type of document
- file_path: Path to uploaded file
- uploaded_at: Timestamp

## API Endpoints

### Authentication
- `POST /signup` - Create new account
- `POST /login` - Login to account
- `GET /logout` - Logout

### Dashboard & Profile
- `GET /` - Home redirect
- `GET /dashboard` - Main dashboard
- `GET /profile` - User profile page
- `POST /upload-document` - Upload document
- `GET /download-document/<doc_id>` - Download document

### Games
- `GET /games` - Games hub
- `GET /game/number-guess` - Number guess game
- `GET /game/memory` - Memory match game
- `GET /game/trivia` - Trivia game
- `POST /api/save-score` - Save game score

## File Upload Specifications
- **Allowed Formats**: JPG, JPEG, PNG, PDF
- **Max File Size**: 16MB
- **Supported Documents**:
  - Profile Picture
  - Signature
  - Aadhar Card
  - 12th Marksheet

## Future Enhancements
- Leaderboard system
- Achievement badges
- Daily challenges
- Learning modules
- Career pathway recommendations
- Social features (friend connections, challenges)

## Contributing
Feel free to submit issues and enhancement requests!

## License
This project is open source and available under the MIT License.

## Author
Hexecutioners Team

## Support
For support, please create an issue in the repository.
