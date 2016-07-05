import logging
import traceback
from django.contrib.auth.models import User

from librapp.lib.token_helper import TokenHelper

class TokenAuthBackend(object):
    def authenticate(self, request):
        th = TokenHelper()
        try:
            token = th.get_token_from_request(request)
            if token is None:
                logging.warn('Auth token headers is missing')
                return None
            authenticated_user = th.validate_auth_token(token)
            return authenticated_user
        except:
            logging.error('Invalid token. Error: {0}'.format(traceback.format_exc()))
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logging.error('user id: {0} does not exist in database'.format(user_id))
            return None
