import pytest

from service.server import app
from unittest import mock

no_role = {"user_id": "sg1dp3000", "roles": ""}
correct_role = {"user_id": "sg1dp3000", "roles": "NSD"}
incorrect_role = {"user_id": "sg1dp3000", "roles": "ABC"}

class TestNavigation:

    def setup_method(self, method):
        self.app = app.test_client()

    def test_get_index_page(self):
        response = self.app.get('/')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry data' in content
        assert 'National Spatial Dataset' in content

    def test_view_ppd_page_with_incorrect_param_combo_without_role_code(self):
        response = self.app.get('/commercial/ppd', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 404
        assert '404: Not Found' in content

    def test_view_nsd_page_with_valid_param_combo_without_login(self):
        response = self.app.get('/commercial/nsd', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Login' in content
        assert 'Username' in content
        assert 'Password' in content

    @mock.patch('service.server.get_esecurity_header_values', return_value=no_role)
    def test_view_nsd_page_with_valid_param_combo_without_role_code(self, mock_header):
        response = self.app.get('/commercial/nsd', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'National Spatial Dataset' in content
        assert 'Set-up process' in content

    @mock.patch('service.server.get_esecurity_header_values', return_value=correct_role)
    def test_view_nsd_page_with_valid_param_combo_with_role_code(self, mock_header):
        response = self.app.get('/commercial/nsd', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'National Spatial Dataset' in content
        assert 'Download Dataset' in content

    @mock.patch('service.server.get_esecurity_header_values', return_value=incorrect_role)
    def test_view_nsd_page_with_valid_param_combo_with_incorrect_role_code(self, mock_header):
        response = self.app.get('/commercial/nsd', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'National Spatial Dataset' in content
        assert 'Set-up process' in content

    def test_view_nsd_page_with_incorrect_param_combo_without_role_code(self):
        response = self.app.get('/open/nsd', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 404
        assert '404: Not Found' in content

    def test_view_nsd_page_with_invalid_param_combo_without_role_code(self):
        response = self.app.get('/made-up-data-type/nsd', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 404
        assert '404: Not Found' in content

    @mock.patch('service.server.check_valid_dataset_type')
    def test_view_nsd_page_when_unknown_error_occurs(self, mock_check):
        mock_check.side_effect = Exception('test exception')
        response = self.app.get('/commercial/nsd', follow_redirects=True)
        assert response.status_code == 500

    def test_download_nsd_dataset_with_valid_param_combo_without_role_code(self):
        response = self.app.get('/commercial/nsd/NSD-Dataset-1.zip')
        assert response.status_code == 200
        assert open('service/static/Datasets/NSD-Dataset-1.zip', 'rb').read() == response.data

    def test_download_nsd_dataset_with_incorrect_param_combo_without_role_code(self):
        response = self.app.get('/open/nsd/NSD-Dataset-1.zip', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 404
        assert '404: Not Found' in content

    def test_download_nsd_dataset_with_invalid_param_combo_without_role_code(self):
        response = self.app.get('/made-up-data-type/nsd/NSD-Dataset-1.zip', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 404
        assert '404: Not Found' in content

if __name__ == '__main__':
    pytest.main()
