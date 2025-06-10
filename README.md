# Flask Workout Program Manager with Google Sheets

This web application allows administrators to assign Google Sheets (representing workout programs) to users. Users can view their assigned programs and provide feedback directly to the Google Sheet.

## Features

- User registration and login system.
- Admin role for managing users and sheet assignments.
- Admin dashboard to list users and Google Sheets from the admin's Google Drive.
- Assignment of specific Google Sheets to users.
- User dashboard to display the workout program from the assigned Google Sheet.
- Functionality for users to write feedback for each exercise back to their Google Sheet.
- Backend built with Flask.
- Frontend using Jinja2 templating and Bootstrap.
- Google Drive and Sheets API integration via a service account.

## Setup Instructions

### Prerequisites

- Python 3.7+
- pip (Python package installer)
- Git

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Google Service Account

1.  **Google Cloud Project:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
2.  **Enable APIs:**
    *   In your project, navigate to "APIs & Services" > "Library".
    *   Search for and enable the "Google Drive API".
    *   Search for and enable the "Google Sheets API".
3.  **Create a Service Account:**
    *   Navigate to "APIs & Services" > "Credentials".
    *   Click "+ CREATE CREDENTIALS" and select "Service account".
    *   Fill in the service account details.
    *   Grant appropriate roles. For simplicity during development, "Editor" on the project can work, but for production, create a custom role with minimal permissions for Drive and Sheets.
    *   Click "DONE".
4.  **Create Service Account Key:**
    *   Find your newly created service account in the list. Click on it.
    *   Go to the "KEYS" tab.
    *   Click "ADD KEY" > "Create new key".
    *   Select "JSON" as the key type and click "CREATE".
    *   A JSON file will be downloaded. Rename this file to `service_account.json`.
5.  **Place Credentials File:**
    *   Create an `instance` folder in the root of the project directory if it doesn't already exist: `mkdir -p instance`
    *   Move the downloaded and renamed `service_account.json` file into this `instance` folder.
6.  **Share Google Drive Resources:**
    *   The service account needs access to the Google Sheets it will manage.
    *   Open Google Drive and share the specific Google Sheets (or the folder containing them) with the service account's email address (e.g., `your-service-account-name@your-project-id.iam.gserviceaccount.com`). Grant "Editor" permissions if the app needs to write feedback.

### 5. Initialize Database

The database tables are created automatically when the application first runs (specifically, when `create_app()` is called). The application uses SQLite by default for development (`instance/app.sqlite`).

### 6. Create an Admin User

1.  Register a new user through the web application's registration page.
2.  Open your terminal in the project root (with the virtual environment activated).
3.  Set the Flask application environment variable:
    ```bash
    export FLASK_APP=run.py  # On Windows: set FLASK_APP=run.py
    ```
4.  Run the following command to promote the user to admin (replace `<username>` with the actual username you registered):
    ```bash
    flask make-admin <username>
    ```

### 7. Run the Development Server

```bash
python run.py
```
Or, using the Flask CLI:
```bash
flask run
```
The application should be accessible at `http://127.0.0.1:5000/`.

## Running Tests

To run the automated tests:

```bash
pytest
```
This will also generate a coverage report in the `htmlcov/` directory and print a summary to the terminal.

## Deployment Considerations

For production deployment, consider the following:

### WSGI Server

Flask's built-in development server is not suitable for production. Use a production-grade WSGI server like Gunicorn or uWSGI.

Example with Gunicorn (assuming `run.py` creates the app instance named `app`):
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 "run:app"
```
(Note: `run:app` refers to the `app` Flask application object inside the `run.py` file. If your app object is created differently, adjust accordingly e.g. `"app:create_app()"` if using application factory pattern with Gunicorn directly).

### Environment Variables

For security and flexibility, manage configurations using environment variables:
-   `SECRET_KEY`: For Flask session management.
-   `SQLALCHEMY_DATABASE_URI`: To connect to a production database.
-   `GOOGLE_APPLICATION_CREDENTIALS`: Standard Google Cloud env var to point to your `service_account.json` file, especially if not placing it in the instance folder directly.

### Database

While SQLite is fine for development, use a more robust database like PostgreSQL or MySQL for production. Update `SQLALCHEMY_DATABASE_URI` accordingly.

### Docker (Optional)

Containerizing the application with Docker can simplify deployment and scaling. A basic `Dockerfile` is provided as a starting point.

---
*This README was generated as part of an automated development process.*
