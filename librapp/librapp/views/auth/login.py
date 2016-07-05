from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, status
from rest_framework.response import Response

from librapp import models
from librapp.lib.token_helper import TokenHelper
from librapp.lib.request_field import RequestField
from librapp.lib.request_validator import RequestValidation, ValidationError


class LoginViewSet(viewsets.ViewSet):
    '''API Endpoint to login, logout

    **API Endpoint**
    ::
        http://foo.com/auth/login/

    **Methods:**
        - list : not allowed
        - retrieve : not allowed
        - create
        - update : not allowed
        - delete

    **HTTP Code:**
        - 200 OK
        - 400 Bad Request
        - 401 Unauthorized
        - 403 Forbidden
        - 405 Method Not Allowed
    '''

    th = TokenHelper()

    def create(self, request):
        '''Logs in and responds with Auth Token. Use that token in the subsequent requests header.
        Also include csrf token in the header.

        **Usage**
        ::
            POST http://foo.com/auth/login/
        
        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        username           string      No         funed user's username eg: abc123@utdallas.edu
        password           string      No         password
        ================== =========== ========== =============================

        **Sample Request**
        ::
            {
                "username": "abc123@utdallas.edu",
                "password": "StrongP@s$word22"
            }

        **Sample Response**
        ::
            {
                "X-Auth-Token": "blahblahblahblah"
            }
        '''

        fields = [
                RequestField(
                    name='username',
                    required=True,
                    types=(str, unicode),
                    checks=['does_username_exist']),
                RequestField(
                    name='password',
                    required=True,
                    types=(str, unicode),
                    #checks=['is_valid_password']),
                    checks=[]),
                ]

        try:
            RequestValidation(request=request, checks=[], fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            msg = 'Incorrect password for username: {0}'.format(username)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            login(request, user)
            token = self.th.generate_token(user)
            # good to response with auth-token, and expect x-Auth-Token on header
            response = {'X-Auth-Token': token}
            return Response(response)
        except:
            raise
            msg = 'Could not login username: {0}'.format(username)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        '''logout: actually no need to log out

        **Usage**
        ::
            DELETE http://foo.com/auth/login/username/

        **Sample Response**
        ::
            {"logout": true}
        '''
        logout(request)
        return Response({'logout': True})
