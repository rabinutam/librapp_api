'''unittests for organization

run as:
    $ python manage.py test
'''

from rest_framework.test import APITestCase
from funedapp import models
from funedapp.lib.db_setup_helper import DBSetupHelper


class SearchTest(APITestCase):

    def setUp(self):
        dbhelper = DBSetupHelper()
        self.path = '/search/'

    def auth(self):
        # TODO after django auth setup for organizations API
        return

    def test_list_success(self):
        response = self.client.get(self.path)
        print response
        # response.data or json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('books' in response.data,
                msg='books not in response')

    def test_retrieve_success(self):
        url = '{0}{1}/'.format(self.path, self.org_data1['name'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # response.data or json.loads(response.content)
        self.assertEqual(response.data['name'], self.org_data1['name'])
