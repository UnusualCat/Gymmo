# Start with a Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Ensure the instance folder exists (though service_account.json should ideally be mounted or managed via secrets)
RUN mkdir -p instance

# Environment variables (can be overridden at runtime)
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
# For Gunicorn
ENV APP_MODULE="run:app"

# Expose the port the app runs on (Gunicorn will use 8000 by default if not specified in CMD)
EXPOSE 5000
# If using Gunicorn and binding to 8000, expose 8000 instead/additionally:
# EXPOSE 8000

# Command to run the application using Gunicorn (example)
# Adjust workers as needed.
# The path to service_account.json needs to be handled, e.g., by mounting it as a volume
# or setting GOOGLE_APPLICATION_CREDENTIALS env var if the file is in a known location.
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "run:app"]

# If you prefer Flask's dev server (NOT for production):
# CMD ["flask", "run", "--host=0.0.0.0"]
