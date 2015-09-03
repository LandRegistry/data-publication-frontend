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
        assert 'Land Registry Data' in content
        assert 'Overseas Ownership Dataset' in content

    def test_get_datasets(self):
        response = self.app.get('/data')
        content = response.data.decode()
        assert response.status_code == 200
        assert "Overseas Dataset (August 2015)"

if __name__ == '__main__':
    pytest.main()
