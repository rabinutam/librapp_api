import traceback
from rest_framework import viewsets, status
from rest_framework.response import Response

from librapp import models
from librapp.lib.rbac import RBAC
from librapp.lib.request_field import RequestField
from librapp.lib.request_validator import RequestValidation,ValidationError


class UserViewSet(viewsets.ViewSet):
    '''API Endpoint to access users

    **API Endpoint**
    ::
        http://foo.com/users/

    **Methods:**
        - create
        - update
        - list

    **HTTP Code:**
        - 200 OK
        - 400 Bad Request
        - 401 Unauthorized
        - 403 Forbidden
        - 405 Method Not Allowed
    '''

    rbac = RBAC()

    def list(self,request):
        '''Responses with a list of users.

        **Usage**
        ::
            All Users:
                GET "http://foo.com/users/"
            Users by orgranization Id:
                GET "http://foo.com/users?organization_id=<ID>"

        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        organization_id    integer     No         organization ID
        ================== =========== ========== =============================

        **Sample Request**
        ::
            GET http://foo.com/users?organization_id=4

        **Sample Response**
        ::
            {
                "users": [
                        {
                            "id": 5,
                            "first_name": "first1",
                            "last_name": "last1",
                            "email": "email123@utdallas.edu"
                        }
                    ]
            }
        '''

        fields = [
                    RequestField(name='organization_id',query_param=True,types=(int, long),checks=['does_organization_exist']),
                ]
        checks = ['login']

        try:
            RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        org_id = request.query_params.get('organization_id')

        try:
            users_filter = {}
            if org_id:
                users_filter['organization_id'] = org_id
            members = models.Membership.objects.filter(**users_filter)
            users = [mem.user for mem in members]
            users_result = []
            for user in users:
                result = {
                    'id': user.id,
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'email':user.email
                }
                users_result.append(result)
            return Response({'users': users_result})
        except Exception as error:
            msg = 'Error on getting users list for the org'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def create(self,request):
        '''Registers/Creates an User. No Login required to register/create user.

        **Usage**
        ::
            POST http://foo.com/users/

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        first_name         string      Yes        user first name
        last_name          string      Yes        user last name
        email              string      Yes        user email
        password           string      Yes        user password
        ================== =========== ========== =============================

        **Sample Request**
        ::
            {
                "first_name": "sasi91",
                "last_name": "sasi91",
                "email": "sasi91@utdallas.edu"
                "password": "areally$trongpw!2"
            }

        **Sample Response**
        ::
            {
                "id": 14,
                "email": "sasi91@utdallas.edu"
                "first_name": "sasi91",
                "last_name": "sasi91",
            }
        '''

        fields = [
                RequestField(name='first_name', required=True, types=(str, unicode), checks=[]),
                RequestField(name='last_name', required=True, types=(str, unicode), checks=[]),
                RequestField(name='email', required=True, types=(str, unicode), checks=['is_valid_utd_email']),
                RequestField(name='password', required=True, types=(str, unicode), checks=['check_password'])
                ]
        # Do not add login, as there is no login before registration
        try:
            RequestValidation(request=request, checks=[], fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password'),

        try:
            try:
                user = models.User.objects.get(username=email)
                msg = 'User already exists'
                return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
            except models.User.DoesNotExist:
                user = models.User.objects.create_user(
                        username=email, email=email, password=password, first_name=first_name, last_name=last_name)
                result = {
                    'id': user.id,
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'email':user.email
                }
                return Response(result)
        except:
            msg = 'Could not Create User'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None):
        '''Updates an User for the given username.

        **Usage**
        ::
            PUT "http://foo.com/users/<id>/"

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        first_name         string      Yes*       new user first name
        last_name          string      Yes*       new user last name
        password           string      Yes*       new user password
        ================== =========== ========== =============================
        * = At least one is required, otherwise nothing to update

        **Sample Response**
        ::
            {
                "id": 14,
                "email": "sasi91@utdallas.edu"
                "first_name": "sasi91",
                "last_name": "sasi91",
            }
        '''

        fields = [
                RequestField(name='first_name', types=(str, unicode), checks=[]),
                RequestField(name='last_name', types=(str, unicode), checks=[]),
                RequestField(name='password', types=(str, unicode), checks=['check_password'])
                ]
        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        user = vres.user # current User

        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')

        try:
            db_user = models.User.objects.get(id=pk)
            if user.username != db_user.username:
                msg = 'Cannot Update User. Current User: {0} is not same as User: {1} to update.'.format(user.username, db_user.username)
                return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

            if password:
                db_user.set_password(password)
            if first_name:
                db_user.first_name = first_name
            if last_name:
                db_user.last_name = last_name
            db_user.save()

            result = {
                'id': user.id,
                'first_name':user.first_name,
                'last_name':user.last_name,
                'email':user.email
            }
            return Response(result)
        except models.User.DoesNotExist:
            msg = 'User doesnt exist'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
        except:
            msg = 'Error in updating user info'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
