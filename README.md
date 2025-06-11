# Gymmo - Workout Program Management System

A web application for managing workout programs from Excel files stored in Google Drive.

## Features

- User authentication and authorization
- Admin dashboard for managing users and programs
- User dashboard for viewing assigned workout programs
- Google Drive integration for Excel file storage
- Automatic workout extraction from Excel files
- Program assignment to users

## Prerequisites

- Python 3.8+
- Google Cloud Platform account with Google Drive API enabled
- Service account credentials for Google Drive API

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd gymmo
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Drive API:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Google Drive API
   - Create a service account
   - Download the service account credentials JSON file
   - Place the credentials file in the project root as `credentials.json`

5. Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key-here
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
```

6. Initialize the database:
```bash
python backend/run.py
```

## Running the Application

1. Start the backend server:
```bash
python backend/run.py
```

2. The API will be available at `http://localhost:8000`
3. API documentation will be available at `http://localhost:8000/docs`

## Default Admin Account

- Email: admin@example.com
- Password: admin

**Important**: Change the default admin password after first login.

## API Endpoints

### Authentication
- POST `/api/v1/auth/login` - User login
- POST `/api/v1/auth/register` - User registration

### Users
- GET `/api/v1/users` - List users (admin only)
- POST `/api/v1/users` - Create user (admin only)
- GET `/api/v1/users/{id}` - Get user details
- PUT `/api/v1/users/{id}` - Update user
- DELETE `/api/v1/users/{id}` - Delete user (admin only)

### Programs
- GET `/api/v1/programs` - List programs
- POST `/api/v1/programs` - Create program (admin only)
- GET `/api/v1/programs/{id}` - Get program details
- PUT `/api/v1/programs/{id}` - Update program (admin only)
- DELETE `/api/v1/programs/{id}` - Delete program (admin only)
- POST `/api/v1/programs/{id}/process` - Process program's Excel file (admin only)
- POST `/api/v1/programs/{id}/users/{user_id}` - Add user to program (admin only)
- DELETE `/api/v1/programs/{id}/users/{user_id}` - Remove user from program (admin only)

### Workouts
- GET `/api/v1/workouts` - List workouts
- POST `/api/v1/workouts` - Create workout (admin only)
- GET `/api/v1/workouts/{id}` - Get workout details
- PUT `/api/v1/workouts/{id}` - Update workout (admin only)
- DELETE `/api/v1/workouts/{id}` - Delete workout (admin only)

## Excel File Format

The application expects Excel files with the following structure:
- Sheet name: "Programmi"
- Columns:
  - Esercizio
  - Video
  - Note
  - Serie
  - Ripetizioni
  - Recupero
  - Note Extra
  - Progressione

## License

This project is licensed under the MIT License - see the LICENSE file for details. 