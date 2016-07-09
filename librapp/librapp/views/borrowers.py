import traceback
from django.db import IntegrityError as DBIntegrityError
from rest_framework import viewsets, status
from rest_framework.response import Response

from librapp import models
from librapp.lib.rbac import RBAC
from librapp.lib.request_field import RequestField
from librapp.lib.request_validator import RequestValidation, ValidationError


class BorrowersViewSet(viewsets.ViewSet):
    '''API Endpoint to access borrowers

    **API Endpoint**
    ::
        http://foo.com/borrowers/

    **Methods:**
        - list
        - retrieve : not allowed
        - create
        - update
        - delete

    **HTTP Code:**
        - 200 OK
        - 400 Bad Request
        - 401 Unauthorized
        - 403 Forbidden
        - 405 Method Not Allowed
    '''

    rbac = RBAC()

    @staticmethod
    def _get_response_data(db_obj=None):
        response_data = {
                }
        return response_data


    def list(self, request):
        '''Method Not Allowed'''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def xlist(self, request):
        '''Responses with a list of borrowers

        **Usage**
        ::
            GET http://foo.com/borrowers

        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        ================== =========== ========== =============================

        **Sample Request**
        ::
            GET http://foo.com/borrowers

        **Sample Response**
        ::
            {"borrowers": []}
        '''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        fields = [
                RequestField(
                    name='',
                    required=True,
                    query_param=True,
                    types=(int, long),
                    checks=[]),
                ]
        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        req_filter = {'organization_id': request.query_params['organization_id']}
        state = request.query_params.get('state')
        if state:
            req_filter['state'] = state

        try:
            result = []
            return Response({'borrowers': result})
        except:
            msg = 'Error getting Borrowers'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        '''Method Not Allowed
        '''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def create(self, request):
        '''Creates a Borrower.

        **Usage**
        ::
            POST http://foo.com/borrowers/

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        first_name         string      Yes        Borrowers First name
        last_name          string      Yes        Borrowers Last name
        ssn                string      Yes        Borrowers ssn
        address            string      Yes        Borrowers address
        phone              string      No         Borrowers phone
        email              string      No         Borrowers email
        ================== =========== ========== =============================

        **Sample Request body**
        ::
            {
                "first_name": "Robi",
                "last_name": "Bobi",
                "ssn": "123456789",
                "address": "123 showmethe way"
            }

        **Sample Response**
        ::
            {
            }
        '''

        fields = [
                RequestField(name='first_name', required=True, types=(str, unicode), checks=[]),
                RequestField(name='last_name', required=True, types=(str, unicode), checks=[]),
                RequestField(name='ssn', required=True, types=(str, unicode), checks=['ssn_does_not_exist']),
                RequestField(name='address', required=True, types=(str, unicode), checks=[]),
                RequestField(name='phone', required=False, types=(str, unicode), checks=[]),
                RequestField(name='email', required=False, types=(str, unicode), checks=['is_valid_email']),
                ]
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            row = {
                    'fname': request.data['first_name'],
                    'lname': request.data['last_name'],
                    'ssn': request.data['ssn'],
                    'address': request.data['address'],
                    }
            phone = request.data.get('phone')
            if phone is not None:
                row['phone'] = phone
            email = request.data.get('email')
            if email is not None:
                row['email'] = email
            borrower = models.Borrower.objects.create(**row)
            response_data = {
                    'card_no': borrower.card_no,
                    'fname': borrower.fname,
                    'lname': borrower.lname
                    }
            return Response(response_data)
        except:
            msg = 'Could not create new Borrower'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        '''Method Not Allowed'''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def xupdate(self, request, pk=None):
        '''Update

        **Usage**
        ::
            PUT http://foo.com/borrowers/<id>/

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        ================== =========== ========== =============================

        **Sample Request body**
        ::
            {
            }

        **Sample Response**
        ::
            {
            }
        '''
        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        fields = [
                RequestField(
                    name='',
                    required=True,
                    types=(str, unicode),
                    checks=['is_valid_state']),
                ]
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            req = models.Borrower.objects.get(id=pk)
            response_hash = self._get_response_data(db_obj=req)
            return Response(response_hash)
        except models.Borrower.DoesNotExist:
            msg = 'Borrower: {0} does not exist'.format(pk)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
        except:
            msg = 'Could not update Borrower'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        '''Method Not Allowed
        '''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def xdestroy(self, request, pk=None):
        '''Deletes memberships request for the given ID.
        Only Org Admin can delete Org's Membership Requests.

        **Usage**
            DELETE "http://foo.com/borrowers/<id>/"

        **Sample Request**
        ::
            DELETE "http://foo.com/borrowers/6"

        **Sample Response**
        ::
            OK
        '''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            req = models.Borrower.objects.get(id=pk)
            # TODO delete dependencies (cascade to Loan and Fine)
            req.delete()
            return Response()
        except models.Borrower.DoesNotExist:
            msg = 'Borrower: {0} does not exist'.format(pk)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
        except:
            msg = 'Error deleting Borrower: {0}'.format(pk)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
