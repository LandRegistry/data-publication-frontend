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

    def test_get_usertype_page_success(self):
        response = self.app.get('/usertype')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_personal_page_success(self):
        response = self.app.get('/personal')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_personal_page_pi_success(self):
        response = self.app.post('/usertype/validation', data=dict(
            user_type='Private individual'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Company Name' not in content
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_personal_page_company_success(self):
        response = self.app.post('/usertype/validation', data=dict(
            user_type='Company'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Company Name' in content
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_personal_page_no_selection_success(self):
        response = self.app.post('/usertype/validation', data=dict(
            user_type=''
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Select user type' in content
        assert 'Not a valid choice' in content
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_address_page_success(self):
        response = self.app.get('/address')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_all_fields_valid(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post('/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            username='The Doctor',
            day='22',
            month='11',
            year='1963'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Address Line 1' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_all_fields_valid_including_company(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.post('/personal/validation', data=dict(
            company_name='UNIT',
            title='Dr',
            first_name='John',
            last_name='Smith',
            username='The Doctor',
            day='22',
            month='11',
            year='1963'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Address Line 1' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_company_name_empty(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.post('/personal/validation', data=dict(
            company_name='',
            title='Dr',
            first_name='John',
            last_name='Smith',
            username='The Doctor',
            day='22',
            month='11',
            year='1963'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Company Name is required' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_all_fields_empty(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post('/personal/validation', data=dict(
            title='Dr',
            first_name='',
            last_name='',
            username='',
            day='',
            month='',
            year=''
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Username is required' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_all_fields_other_title_valid(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post('/personal/validation', data=dict(
            title='Other',
            other_title='Brigadier Sir',
            first_name='Alistair Gordon',
            last_name='Lethbridge-Stewart',
            username='The Brig',
            day='22',
            month='11',
            year='1963'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Address Line 1' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_other_title_not_specified(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post('/personal/validation', data=dict(
            title='Other',
            other_title='',
            first_name='John',
            last_name='Smith',
            username='The Doctor',
            day='22',
            month='11',
            year='1963'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert ' title is required' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_old_date(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post('/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            username='The Doctor',
            day='22',
            month='11',
            year='1063'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Year must be between ' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_future_date(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post('/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            username='The Doctor',
            day='22',
            month='11',
            year='3063'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Year must be between ' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_invalid_date(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post('/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            username='The Doctor',
            day='32',
            month='13',
            year='1963'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Year must be between ' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_long_field(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post('/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            username='abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890',
            day='22',
            month='11',
            year='1063'
            ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Field cannot be longer than 60 characters.' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_contact_page_success(self):
        response = self.app.get('/tel')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(multiple_files))))
    def test_get_datasets_success_multiple_files(self, mock_backend_reponse):
        response = self.app.get('/data')
        content = response.data.decode()
        assert response.status_code == 200
        assert "Overseas Dataset (August 2015)" in content
        assert "Overseas Dataset (August 2015 update)" in content

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(no_files))))
    def test_get_datasets_success_no_files(self, mock_backend_reponse):
        response = self.app.get('/data')
        content = response.data.decode()
        assert response.status_code == 200
        assert "Full Datasets" in content
        assert "Change-Only Updates" in content

if __name__ == '__main__':
    pytest.main()
