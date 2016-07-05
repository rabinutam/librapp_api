import logging
import time
from django.contrib.auth.models import User
from encryption_helper import EncryptionHelper

class TokenHelper(object):

    eh = EncryptionHelper()

    def generate_token(self, user=None):
        token_parts = [str(time.time()), str(user.id), user.username, user.first_name]
        token_text = '|*|'.join(token_parts)
        token_text = '{0}|*|'.format(token_text)
        token = self.eh.encrypt(token_text)
        return token

    def get_token_from_request(self, request):
        '''get token from request Header
        '''

        if 'X-Auth-Token' in request.META:
            return request.META['X-Auth-Token']
        elif 'X-AUTH-TOKEN' in request.META:
            return request.META['X-AUTH-TOKEN']
        elif 'HTTP_X_Auth_Token' in request.META:
            return request.META['HTTP_X_Auth_Token']
        elif 'HTTP_X_AUTH_TOKEN' in request.META:
            return request.META['HTTP_X_AUTH_TOKEN']
        return None

    def validate_auth_token(self, token):
        '''Validate token in request Header
        '''

        create_time, user_id, username, first_name = self._get_items_in_token(token)

        expired = self._has_token_expired(create_time)
        if expired:
            return None

        user = self._get_user(user_id)
        if user is None or not user.is_active:
            return None
        return user

    def _get_items_in_token(self, token):
        plaintext = self.eh.decrypt(token)
        items = plaintext.split('|*|')
        create_time, user_id, username, first_name = items[0], items[1], items[2], items[3]
        return create_time, user_id, username, first_name

    def _has_token_expired(self, create_time):
        '''Token expires after 24 hours
        '''
        current_time = time.time()
        create_time = float(create_time)
        token_life = 1 * 24 * 60 * 60 # 1 day
        if (current_time - create_time > token_life):
            logging.warning('auth token expired')
            return True
        return False

    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logging.error('user id: {0} does not exist in database'.format(user_id))
            return None
