from flask import Blueprint, render_template, current_app, flash, request, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.google_services import read_sheet_data, write_sheet_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    workout_data = None
    sheet_error = None

    if current_user.google_sheet_id:
        sheet_name_for_program = 'Foglio1'
        # Read up to column H to potentially get existing feedback.
        data_range_to_read = 'A1:H50' # Read up to H
        range_to_read = f"{sheet_name_for_program}!{data_range_to_read}"

        current_app.logger.info(f"User {current_user.username} has sheet {current_user.google_sheet_id}. Attempting to read range: {range_to_read}")

        try:
            workout_data = read_sheet_data(current_user.google_sheet_id, range_to_read)
            if workout_data is None:
                sheet_error = "Could not retrieve workout data. Assigned sheet might be inaccessible or service account issue."
                current_app.logger.error(f"read_sheet_data returned None for user {current_user.username}, sheet {current_user.google_sheet_id}")
            elif not workout_data:
                 sheet_error = "Workout data is empty or the specified range in the sheet has no content."
                 current_app.logger.info(f"No data found in sheet {current_user.google_sheet_id}, range {range_to_read} for user {current_user.username}")

        except Exception as e:
            current_app.logger.error(f"Error reading sheet for user {current_user.username}, sheet_id {current_user.google_sheet_id}: {e}")
            sheet_error = f"An unexpected error occurred while fetching your workout program: {str(e)}"
            workout_data = None
    else:
        current_app.logger.info(f"User {current_user.username} has no assigned Google Sheet.")

    return render_template('index.html', title='Home', workout_data=workout_data, sheet_error=sheet_error)

@main_bp.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    if not current_user.google_sheet_id:
        flash('You do not have an assigned sheet to submit feedback to.', 'warning')
        return redirect(url_for('main.index'))

    sheet_row_number = request.form.get('sheet_row_number', type=int)
    feedback_text = request.form.get('feedback_text', '').strip()

    if not sheet_row_number or sheet_row_number < 1 : # Basic validation
        flash('Invalid row number for feedback.', 'danger')
        return redirect(url_for('main.index'))

    # Allow submitting empty string to clear feedback.
    # if not feedback_text:
    #     flash('Feedback text cannot be empty if you wish to save.', 'warning')
    #     return redirect(url_for('main.index'))

    # ASSUMPTION: Feedback goes to Column H of 'Foglio1'
    sheet_name_for_feedback = 'Foglio1'
    feedback_column = 'H' # Target column for feedback
    target_cell = f'{sheet_name_for_feedback}!{feedback_column}{sheet_row_number}'

    values_to_write = [[feedback_text]] # Data must be list of lists

    current_app.logger.info(f"User {current_user.username} submitting feedback '{feedback_text}' to sheet {current_user.google_sheet_id}, cell {target_cell}")

    try:
        success = write_sheet_data(current_user.google_sheet_id, target_cell, values_to_write)
        if success:
            flash(f'Feedback for row {sheet_row_number} saved successfully to {target_cell}!', 'success')
        else:
            flash('Failed to save feedback. The sheet might be inaccessible or an API error occurred.', 'danger')
    except Exception as e:
        current_app.logger.error(f"Error writing feedback for user {current_user.username} to sheet {current_user.google_sheet_id}, cell {target_cell}: {e}")
        flash(f'An unexpected error occurred while saving feedback: {str(e)}', 'danger')

    return redirect(url_for('main.index'))


@main_bp.route('/admin_test_page') # Keep admin test route
@login_required
@admin_required
def admin_only_route():
    return "Welcome, Admin! This is an admin-only page."
