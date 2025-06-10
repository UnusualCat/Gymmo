import pytest
from unittest.mock import patch, MagicMock
from app.google_services import list_drive_files, read_sheet_data, write_sheet_data
from googleapiclient.errors import HttpError

# This fixture provides the app context needed for current_app.logger and current_app.instance_path
@pytest.fixture(autouse=True)
def app_context_fixture(app):
    with app.app_context():
        yield

def test_list_drive_files_success():
    mock_service = MagicMock()
    mock_files_resource = MagicMock()
    mock_list_execute = MagicMock()

    expected_files = [{'id': '123', 'name': 'Test Sheet', 'mimeType': 'application/vnd.google-apps.spreadsheet'}]
    mock_list_execute.execute.return_value = {'files': expected_files, 'nextPageToken': None}
    mock_files_resource.list.return_value = mock_list_execute
    mock_service.files.return_value = mock_files_resource

    with patch('app.google_services.get_drive_service', return_value=mock_service):
        files = list_drive_files()
        assert files == expected_files
        mock_files_resource.list.assert_called_once_with(
            pageSize=10, # Default page_size or whatever is set
            fields="nextPageToken, files(id, name, mimeType)",
            q="mimeType='application/vnd.google-apps.spreadsheet'"
        )

def test_list_drive_files_http_error():
    mock_service = MagicMock()
    mock_files_resource = MagicMock()
    # Simulate an HttpError
    # The actual HttpError constructor needs response and content: resp = httplib2.Response({'status': 404}); content = b''
    # For simplicity, we'll make execute raise it.
    mock_files_resource.list.side_effect = HttpError(MagicMock(status=403), b'Forbidden')
    mock_service.files.return_value = mock_files_resource

    with patch('app.google_services.get_drive_service', return_value=mock_service):
        files = list_drive_files()
        assert files == [] # Should return empty list on HttpError

def test_list_drive_files_no_service():
    with patch('app.google_services.get_drive_service', return_value=None):
        files = list_drive_files()
        assert files == [] # Should return empty list if service is None


def test_read_sheet_data_success():
    mock_service = MagicMock()
    mock_spreadsheets_resource = MagicMock()
    mock_values_resource = MagicMock()
    mock_get_execute = MagicMock()

    expected_values = [['R1C1', 'R1C2'], ['R2C1', 'R2C2']]
    mock_get_execute.execute.return_value = {'values': expected_values}
    mock_values_resource.get.return_value = mock_get_execute
    mock_spreadsheets_resource.values.return_value = mock_values_resource
    mock_service.spreadsheets.return_value = mock_spreadsheets_resource

    with patch('app.google_services.get_sheets_service', return_value=mock_service):
        data = read_sheet_data('sheet_id_123', 'Sheet1!A1:B2')
        assert data == expected_values
        mock_values_resource.get.assert_called_once_with(spreadsheetId='sheet_id_123', range='Sheet1!A1:B2')

def test_write_sheet_data_success():
    mock_service = MagicMock()
    mock_spreadsheets_resource = MagicMock()
    mock_values_resource = MagicMock()
    mock_update_execute = MagicMock()

    mock_update_execute.execute.return_value = {'updatedCells': 2}
    mock_values_resource.update.return_value = mock_update_execute
    mock_spreadsheets_resource.values.return_value = mock_values_resource
    mock_service.spreadsheets.return_value = mock_spreadsheets_resource

    values_to_write = [['new_val1'], ['new_val2']]

    with patch('app.google_services.get_sheets_service', return_value=mock_service):
        success = write_sheet_data('sheet_id_abc', 'Sheet1!A1', values_to_write)
        assert success is True
        mock_values_resource.update.assert_called_once_with(
            spreadsheetId='sheet_id_abc',
            range='Sheet1!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values_to_write}
        )
