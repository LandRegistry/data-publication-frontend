import pytest
from service.server import app
from tests.fake_response import FakeResponse
from unittest import mock
import json
import requests
import datetime
from os import stat, remove
import shutil

recaptcha_pass = {"success": True}
recaptcha_fail = {"success": False}

multiple_files = {
    "File_List": [
        {
            "Name": "OV_FULL_2015_08.zip",
            "Size": 45000000,
            "Checksum": "\"64c7d38f9bb980717c86fa66cd888117\"",
            "URL": "https://s3.eu-central-1.amazonaws.com/data.landregistry.gov.uk/overseas-ownership/OV_FULL_2015_08.zip?X-Amz-SignedHeaders=host&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ABCDEFGHIJKLMNOPQRSTU%2F20150918%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20150918T133013Z&X-Amz-Expires=30&X-Amz-Signature=227f10aeb13c61c987fddd75b2292fc76a29dcbe306a7dbe610c4624344393d3"
        },
        {
            "Name": "OV_UPDATE_2015_08.zip",
            "Size": 2500000,
            "Checksum": "\"7e461444e9d2d959eb035c2528d9848a\"",
            "URL": "https://s3.eu-central-1.amazonaws.com/data.landregistry.gov.uk/overseas-ownership/OV_UPDATE_2015_08.zip?X-Amz-SignedHeaders=host&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ABCDEFGHIJKLMNOPQRSTU%2F20150918%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20150918T133013Z&X-Amz-Expires=30&X-Amz-Signature=227f10aeb13c61c987fddd75b2292fc76a29dcbe306a7dbe610c4624344393d3"
        }
    ],
    "Link_Duration": 60
}
no_files = {
    "File_List": [],
    "Link_Duration": 60
}

valid_pi_session_details = {
    'ip_address': '10.0.2.2',
    'session_id': 'e9e40eb4-b0a8-44c2-aa3f-9daaf375fbe1',
    'user_type': 'Private individual',
    'title': 'Dr',
    'first_name': 'first name',
    'last_name': 'last name',
    'day': 1,
    'month': 1,
    'year': datetime.date.today().year,
    'company_name': 'company name',
    'address_line_1': 'address line 1',
    'country': 'United Kingdom',
    'detected_country': 'United Kingdom',
    'landline': '0123456789',
    'email': 'person@email.com',
    'terms_accepted': True
}


URL_PREFIX = app.config['URL_PREFIX']


class TestNavigation:
    def setup_method(self, method):
        self.app = app.test_client()

    def test_get_index_page_success(self):
        response = self.app.get(URL_PREFIX + '/')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_recaptcha_page_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['tel_screen'] = 'Complete'
        response = self.app.get(URL_PREFIX + '/recaptcha')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'reCAPTCHA Check' in content

    def test_get_usertype_page_success(self):
        response = self.app.get(URL_PREFIX + '/usertype')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_personal_page_directly_success(self):
        response = self.app.get(URL_PREFIX + '/personal', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Private individual' in content
        assert 'Company' in content

    def test_get_personal_page_as_private_individual_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.get(URL_PREFIX + '/personal')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'First name(s)/Given name(s)' in content
        assert 'Company name' not in content

    def test_get_personal_page_as_company_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.get(URL_PREFIX + '/personal')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'First name(s)/Given name(s)' in content
        assert 'Company name' in content

    def test_get_address_page_as_company_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
                sess['personal_screen'] = 'Complete'
        response = self.app.get(URL_PREFIX + '/address')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Company address details' in content

    def test_get_personal_page_pi_success(self):
        response = self.app.post(URL_PREFIX + '/usertype/validation', data=dict(
            user_type='Private individual'), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Company Name' not in content
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_personal_page_company_success(self):
        response = self.app.post(URL_PREFIX + '/usertype/validation', data=dict(
            user_type='Company'), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Company name' in content
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_personal_page_no_selection_success(self):
        response = self.app.post(URL_PREFIX + '/usertype/validation', data=dict(
            user_type=''), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Select user type' in content
        assert 'Not a valid choice' in content
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_address_page_as_private_individual_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
                sess['personal_screen'] = 'Complete'
        response = self.app.get(URL_PREFIX + '/address')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Address details' in content

    def test_personal_page_all_fields_valid(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            day='22',
            month='11',
            year='1963'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Address line 1' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_all_fields_valid_including_company(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            company_name='UNIT',
            title='Dr',
            first_name='John',
            last_name='Smith',
            day='22',
            month='11',
            year='1963'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Address line 1' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_company_name_empty(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            company_name='',
            title='Dr',
            first_name='John',
            last_name='Smith',
            day='22',
            month='11',
            year='1963'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Company name is required' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_all_fields_empty(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Dr',
            first_name='',
            last_name='',
            day='',
            month='',
            year=''
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert ' is required' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_all_fields_other_title_valid(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Other',
            other_title='Brigadier Sir',
            first_name='Alistair Gordon',
            last_name='Lethbridge-Stewart',
            day='22',
            month='11',
            year='1963'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Address line 1' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_other_title_not_specified(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Other',
            other_title='',
            first_name='John',
            last_name='Smith',
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
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
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
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            day='22',
            month='11',
            year='3063'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Year must be between ' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_invalid_date_numbers_outside_range(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            day='32',
            month='13',
            year='1963'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Day must be between 1 and 31' in content
        assert 'Month must be between 1 and 12' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_invalid_date_numbers_in_range(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='Smith',
            day='29',
            month='2',
            year='1983'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Date is not valid' in content
        assert 'Overseas Ownership Dataset' in content

    def test_personal_page_long_field(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/personal/validation', data=dict(
            title='Dr',
            first_name='John',
            last_name='abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890',
            day='22',
            month='11',
            year='1063'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Field cannot be longer than 60 characters.' in content
        assert 'Overseas Ownership Dataset' in content

    def test_address_page_all_fields_blank(self):
        response = self.app.post(URL_PREFIX + '/address/validation')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Address line 1 is required' in content
        assert 'Country is required' in content

    def test_address_page_field_over_character_limit(self):
        params = {'address_line_1': 'A house name',
                  'address_line_2': ''.join(['a'] * 61),
                  'country': 'United Kingdom'}
        response = self.app.post(URL_PREFIX + '/address/validation', data=params)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Field cannot be longer than 60 characters.' in content

    def test_address_page_all_fields_valid(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        params = {'address_line_1': 'A house name',
                  'country': 'United Kingdom'}
        response = self.app.post(URL_PREFIX + '/address/validation', data=params, follow_redirects=True)
        content = response.data.decode()
        print(content)
        assert response.status_code == 200
        assert 'Enter your contact details' in content

    def test_get_contact_page_directly_success(self):
        response = self.app.get(URL_PREFIX + '/tel', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Private individual' in content
        assert 'Company' in content

    def test_get_contact_page_as_private_individual_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
                sess['address_screen'] = 'Complete'
        response = self.app.get(URL_PREFIX + '/tel')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Landline telephone number' in content
        assert 'Mobile telephone number' in content
        assert 'E-mail' in content

    def test_get_contact_page_as_company_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
                sess['address_screen'] = 'Complete'
        response = self.app.get(URL_PREFIX + '/tel')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Landline telephone number' in content
        assert 'Mobile telephone number' in content
        assert 'E-mail' in content

    def test_validate_contact_page_all_company_fields_valid(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.post(URL_PREFIX + '/tel/validation', data=dict(
            landline='01725221163',
            mobile='07895223141',
            email='1963@hotmail.com'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "reCAPTCHA Check" in content

    def test_validate_contact_page_company_no_landline(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Company'
        response = self.app.post(URL_PREFIX + '/tel/validation', data=dict(
            landline='',
            mobile='07895123445',
            email='1963@hotmail.com'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "Telephone (Landline) is required" in content

    def test_validate_contact_page_pi_landline_only(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/tel/validation', data=dict(
            landline='01725221163',
            mobile='',
            email='1963@hotmail.com'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "reCAPTCHA Check" in content

    def test_validate_contact_page_pi_mobile_only(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/tel/validation', data=dict(
            landline='',
            mobile='07895332244',
            email='1963@hotmail.com'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "reCAPTCHA Check" in content

    def test_validate_contact_page_pi_no_number(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/tel/validation', data=dict(
            landline='',
            mobile='',
            email='1963@hotmail.com'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "Landline or Mobile" in content

    def test_validate_contact_page_pi_no_email(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/tel/validation', data=dict(
            landline='01917675432',
            mobile='07896543213',
            email=''
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "E-mail is required" in content

    def test_validate_contact_page_pi_invalid_email(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/tel/validation', data=dict(
            landline='01917675432',
            mobile='07896543213',
            email='mickeymouseclubhouse.disney.com'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "Invalid e-mail address format" in content

    def test_validate_contact_page_pi_field_too_long(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_type'] = 'Private individual'
        response = self.app.post(URL_PREFIX + '/tel/validation', data=dict(
            landline='01917675432',
            mobile='07896543213',
            email='abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890@disney.com'
        ), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "Field cannot be longer than 60 characters." in content

    #    def test_validate_recaptcha_pass(self):
    #        response = self.app.post(URL_PREFIX + '/recaptcha/validation', data=dict(
    #            recaptcha_form = 'ReCaptchaForm'
    #            ), follow_redirects=True)
    #        content = response.data.decode()
    #        assert response.status_code == 200
    #        assert "Terms and conditions" in content

    def test_validate_recaptcha_fail(self):
        response = self.app.post(URL_PREFIX + '/recaptcha/validation', data=dict(
            recaptcha_result='fail'), follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert "reCAPTCHA Check" in content

    def test_get_terms_page_success(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['recaptcha_result'] = 'pass'
        response = self.app.get(URL_PREFIX + '/terms')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Terms and conditions' in content

    def test_get_printable_terms_page_success(self):
        response = self.app.get(URL_PREFIX + '/printable_terms')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Terms and conditions' in content

    def test_get_decline_terms_page(self):
        decline_terms_session_details = valid_pi_session_details
        decline_terms_session_details['terms_accepted'] = False
        with self.app as c:
            with c.session_transaction() as sess:
                for key, val in decline_terms_session_details.items():
                    sess[key] = val
        response = self.app.get(URL_PREFIX + '/decline_terms', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content
        assert 'Terms and conditions' not in content

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(multiple_files))))
    def test_get_datasets_success_multiple_files(self, mock_backend_reponse):
        with self.app as c:
            with c.session_transaction() as sess:
                for key, val in valid_pi_session_details.items():
                    sess[key] = val
        response = self.app.post(URL_PREFIX + '/data')
        app.config['LOGGING'] = False
        content = response.data.decode()
        assert response.status_code == 200
        assert "Overseas Dataset (" in content

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(no_files))))
    def test_get_datasets_success_no_files(self, mock_backend_reponse):
        with self.app as c:
            with c.session_transaction() as sess:
                for key, val in valid_pi_session_details.items():
                    sess[key] = val
        response = self.app.post(URL_PREFIX + '/data')
        content = response.data.decode()
        assert response.status_code == 200
        assert "Datasets" in content

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(multiple_files))))
    def test_log_file_is_written_to(self, mock_backend_reponse):
        shutil.copy(app.config['AUDIT_LOG_FILE'], "{}.backup".format(app.config['AUDIT_LOG_FILE']))
        open(app.config['AUDIT_LOG_FILE'], 'w+').close()
        size_before = stat(app.config['AUDIT_LOG_FILE']).st_size
        app.config['LOGGING'] = True
        with self.app as c:
            with c.session_transaction() as sess:
                for key, val in valid_pi_session_details.items():
                    sess[key] = val
        response = self.app.post(URL_PREFIX + '/data')
        app.config['LOGGING'] = False
        size_after = stat(app.config['AUDIT_LOG_FILE']).st_size
        shutil.copy("{}.backup".format(app.config['AUDIT_LOG_FILE']), app.config['AUDIT_LOG_FILE'])
        remove("{}.backup".format(app.config['AUDIT_LOG_FILE']))
        content = response.data.decode()
        assert response.status_code == 200
        assert "Overseas Dataset (" in content
        assert size_after > size_before

    @mock.patch('requests.get', return_value=FakeResponse(str.encode(json.dumps(multiple_files))))
    def test_get_datasets_fail_using_get(self, mock_backend_reponse):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['recaptcha_result'] = 'fail'
                sess['tel_screen'] = 'Complete'
        response = self.app.get(URL_PREFIX + '/data', follow_redirects=True)
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Land Registry Data' in content
        assert 'reCAPTCHA Check' in content

    def test_hide_url_download_link(self):
        filename = 'OV_FULL_2015_08.zip'
        amazon_date = '20150918T133013Z'
        link_duration = '900'
        credentials = 'ABCDEFGHIJKLMNOPQRST%252F20150918%252Feu-central-1%252Fs3%252Faws4_request'
        signature = '227f10aeb13c61c987fddd75b2292fc76a29dcbe306a7dbe610c4624344393d3'
        url = '/data/download/{}/{}/{}/{}/{}'.format(filename, amazon_date,
                                                     link_duration, credentials,
                                                     signature)
        with self.app as c:
            with c.session_transaction() as sess:
                for key, val in valid_pi_session_details.items():
                    sess[key] = val
        response = self.app.get(URL_PREFIX + url)
        content = response.data.decode()
        assert response.status_code == 302
        assert "https://s3.eu-central-1.amazonaws.com/data.landregistry.gov.uk/" \
               "overseas-ownership/OV_FULL_2015_08.zip?X-Amz-SignedHeaders=host&amp;" \
               "X-Amz-Algorithm=AWS4-HMAC-SHA256&amp;X-Amz-Date=20150918T133013Z&amp;" \
               "X-Amz-Expires=900&amp;" \
               "X-Amz-Credential=ABCDEFGHIJKLMNOPQRST%2F20150918%2Feu-central-1%2Fs3%2F" \
               "aws4_request&amp;" \
               "X-Amz-Signature=227f10aeb13c61c987fddd75b2292fc76a29dcbe306a7dbe610c4624344393d3" \
               in content

    def test_get_cookies_page_success(self):
        response = self.app.get(URL_PREFIX + '/cookies')
        content = response.data.decode()
        assert response.status_code == 200
        assert 'Cookies' in content


if __name__ == '__main__':
    pytest.main()
