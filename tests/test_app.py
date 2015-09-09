import pytest

from service.server import app
from tests.fake_response import FakeResponse
from unittest import mock
import json

import requests

multiple_files = {
    "File_List": [
        {
            "Name": "OV_FULL_2015_08.zip",
            "Size": 45000000,
            "Checksum": "\"64c7d38f9bb980717c86fa66cd888117\"",
            "URL": "https://s3.eu-central-1.amazonaws.com/..."
        },
        {
            "Name": "OV_UPDATE_2015_08.zip",
            "Size": 2500000,
            "Checksum": "\"7e461444e9d2d959eb035c2528d9848a\"",
            "URL": "https://s3.eu-central-1.amazonaws.com/..."
        }
    ],
    "Link_Duration": 60
}
no_files = {
    "File_List": [],
    "Link_Duration": 60
}

class TestNavigation:

    def setup_method(self, method):
        self.app = app.test_client()

    def test_get_index_page_success(self):
        response = self.app.get('/')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_terms_page_success(self):
        response = self.app.get('/terms')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Terms and conditions' in content

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(multiple_files))))
    def test_get_datasets_success_multiple_files(self, mock_backend_reponse):
        response = self.app.post('/data')
        content = response.data.decode()
        assert response.status_code == 200
        assert "Overseas Dataset (August 2015)" in content
        assert "Overseas Dataset (August 2015 update)" in content

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(no_files))))
    def test_get_datasets_success_no_files(self, mock_backend_reponse):
        response = self.app.post('/data')
        content = response.data.decode()
        assert response.status_code == 200
        assert "Full Datasets" in content
        assert "Change-Only Updates" in content

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(multiple_files))))
    def test_get_datasets_fail_using_get(self, mock_backend_reponse):
        response = self.app.get('/data', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Terms and conditions' in content


if __name__ == '__main__':
    pytest.main()
