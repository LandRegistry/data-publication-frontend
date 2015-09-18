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

    def test_get_personal_page_directly_success(self):
        response = self.app.get('/personal', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Private individual' in content
        assert 'Company' in content

    def test_get_personal_page_as_private_individual_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.get('/personal')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'First name(s)/Given name(s)' in content
        assert 'Company name' not in content

    def test_get_personal_page_as_company_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.get('/personal')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'First name(s)/Given name(s)' in content
        assert 'Company name' in content

    def test_get_address_page_as_company_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.get('/address')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Company address details' in content

    def test_get_address_page_as_private_individual_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.get('/address')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Address details' in content

    def test_address_page_all_fields_blank(self):
        response = self.app.post('/address/validation')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Address line 1 is required' in content
        assert 'Country is required' in content

    def test_address_page_field_over_character_limit(self):
        params = {'address_line_1': 'A house name',
                  'address_line_2': ''.join(['a']*61),
                  'country': 'United Kingdom'}
        response = self.app.post('/address/validation', data=params)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Field cannot be longer than 60 characters.' in content

    def test_address_page_all_fields_valid(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        params = {'address_line_1': 'A house name',
                  'country': 'United Kingdom'}
        response = self.app.post('/address/validation', data=params, follow_redirects=True)
        content = response.data.decode()
        print(content)
        assert response.status_code == 200
        assert 'Enter your contact details' in content

    def test_get_contact_page_directly_success(self):
        response = self.app.get('/tel', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Private individual' in content
        assert 'Company' in content

    def test_get_contact_page_as_private_individual_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.get('/tel')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Landline telephone number' in content
        assert 'Mobile telephone number' in content
        assert 'E-mail' in content

    def test_get_contact_page_as_company_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.get('/tel')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Landline telephone number' in content
        assert 'Mobile telephone number' in content
        assert 'E-mail' in content

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
