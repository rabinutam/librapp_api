from rest_framework.test import APITestCase
from funedapp import models

class UsersTest(APITestCase):

    def setUp(self):
        self.path = '/users/'

    def test_update_user_success(self):
        """
        Ensure we can create new user
        :return:
        """
        url = '{0}/'.format(self.path, self.user1['password'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], models.User.get['id'])
