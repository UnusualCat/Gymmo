from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.decorators import admin_required
from app.models import User
from app.google_services import list_drive_files # Assuming service account is set up
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
@admin_required
def ensure_admin():
    # This function is called before any view function in this blueprint.
    # Ensures the user is logged in and is an admin.
    pass

@admin_bp.route('/dashboard')
def dashboard():
    users = []
    google_sheets_result = []
    try:
        # Fetch non-admin users
        users = User.query.filter_by(is_admin=False).all()

        # Fetch Google Sheets from the admin's Drive via service account
        # Ensure service_account.json is in the instance folder and configured
        # The list_drive_files function in google_services.py already logs errors
        google_sheets_result = list_drive_files(page_size=100) # Fetch up to 100 sheets

        if google_sheets_result is None: # Indicates a problem with service/credentials
             flash('Could not initialize Google Services. Check logs and service account setup.', 'danger')
             google_sheets_result = [] # Ensure it's an iterable for the template
        elif not google_sheets_result: # Empty list means no files found or accessible
             flash('No Google Sheets found in the Admin Google Drive, or the service account does not have access to any. Ensure sheets are shared with the service account email.', 'info')


    except Exception as e:
        current_app.logger.error(f"Error in admin dashboard: {str(e)}")
        flash(f'An unexpected error occurred while loading the dashboard: {str(e)}', 'danger')
        # Ensure users and google_sheets_result are empty lists in case of error before they were populated
        users = users if 'users' in locals() and users is not None else []
        google_sheets_result = google_sheets_result if 'google_sheets_result' in locals() and google_sheets_result is not None else []

    return render_template('admin/dashboard.html', title='Admin Dashboard', users=users, google_sheets=google_sheets_result)

@admin_bp.route('/assign_sheet/<int:user_id>', methods=['POST'])
def assign_sheet(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot assign sheet to an admin user.', 'warning')
        return redirect(url_for('admin.dashboard'))

    sheet_id = request.form.get('sheet_id')

    user.google_sheet_id = sheet_id if sheet_id else None # Store sheet_id or None if unassigning

    db.session.commit()

    if sheet_id:
        # It would be better to also fetch the sheet name here to display in the flash message
        # For now, just use the ID.
        flash(f'Sheet ID {sheet_id} assigned to user {user.username}.', 'success')
    else:
        flash(f'Sheet unassigned for user {user.username}.', 'success')

    return redirect(url_for('admin.dashboard'))
