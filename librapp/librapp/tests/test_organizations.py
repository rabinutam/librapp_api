'''unittests for organization

run as:
    $ python manage.py test
'''

from rest_framework.test import APITestCase
from funedapp import models
from funedapp.lib.db_setup_helper import DBSetupHelper


class OrganizationsTest(APITestCase):

    def setUp(self):
        dbhelper = DBSetupHelper()
        self.path = '/organizations/'

	edu1_data = {
		'name': 'The University of Texas at Dallas',
		'edu_type': 'university',
		'address': '800 W Campbell Rd',
		'city': 'Richardson',
		'state': 'TX',
		'zipcode': '75080',
		'country': 'USA',
		'website': 'www.utdallas.edu'
		}
	edu1 = dbhelper.create_edu_institution(entry=edu1_data)

        self.org_data1 = {
                'name': 'test-organization1',
                'edu_institution': edu1,
                'website': 'org1.com'
                }
        self.org_data2 = {
                'name': 'test-organization2',
                'edu_institution': edu1,
                'website': 'org1.com'
                }
        orgs_data = [self.org_data1, self.org_data2]
	orgs = dbhelper.create_organizations(entries=orgs_data)

    def auth(self):
        # TODO after django auth setup for organizations API
        return

    def test_list_success(self):
        response = self.client.get(self.path)
        print response
        # response.data or json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('organizations' in response.data,
                msg='organizations not in response')

    def test_retrieve_success(self):
        url = '{0}{1}/'.format(self.path, self.org_data1['name'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # response.data or json.loads(response.content)
        self.assertEqual(response.data['name'], self.org_data1['name'])
