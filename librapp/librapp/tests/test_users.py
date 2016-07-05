from rest_framework.test import APITestCase
from funedapp import models

class UsersTest(APITestCase):

    def setUp(self):
        self.path = '/users/'

        self.user1 = {
            'first_name': 'unit-test-firstname1',
            'last_name':'unit-test-lastname1',
            'email':'unit-test-emails1@utdallas.edu',
            'password':'unit-test-password1'
		}
        self._setup_user(row=self.user1)

    def __setup_user(self,row=None):

        try:
            models.User.objects.get(email=row['email'])
        except models.User.DoesNotExist:
            models.User.objects.create(**row)

    def test_update_user_success(self):

        """
        Ensure we can create new user
        :return:
        """
        url = '{0}/'.format(self.path, self.user1['password'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], models.User.get['id'])