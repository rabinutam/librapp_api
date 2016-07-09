import traceback
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.response import Response

from librapp import models
from librapp.lib.rbac import RBAC
from librapp.lib.request_field import RequestField
from librapp.lib.request_validator import RequestValidation, ValidationError
from librapp.lib.views_helper import ViewsHelper
from librapp.utils.date_utils import DateUtils


class FinesViewSet(viewsets.ViewSet):
    '''API Endpoint to access book fines

    **API Endpoint**
    ::
        http://foo.com/books/fines/

    **Methods:**
        - list
        - update

    **HTTP Code:**
        - 200 OK
        - 400 Bad Request
        - 401 Unauthorized
        - 403 Forbidden
        - 405 Method Not Allowed
    '''

    dutils = DateUtils()
    rbac = RBAC()
    vh = ViewsHelper()


    def list(self, request):
        '''Responses with a list of book fines

        **Usage**
        ::
            GET http://foo.com/books/fines/

        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        card_no            integer     No         borrower card_no
        lib_branch_id      integer     No         library branch id
        fine_type          string      No         Options: paid, unpaid, both (default)
        ================== =========== ========== =============================

        **Sample Request**
        ::
            GET http://foo.com/books/fines/?card_no=1

        **Sample Response**
        ::
            {}
        '''

        fields = [
                RequestField(name='card_no', required=False, query_param=True, types=(int, str, unicode), checks=[]),
                RequestField(name='lib_branch_id', required=False, query_param=True, types=(int,), checks=[]),
                RequestField(name='fine_type', required=False, query_param=True, types=(str, unicode), checks=[]),
                ]
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            loan_filter = {}
            card_no = request.query_params.get('card_no')
            if card_no is not None:
                loan_filter['card_no'] = int(card_no)

            b_loans = models.BookLoan.objects.filter(**loan_filter)

            lib_branch_id = request.query_params.get('lib_branch_id')
            fine_type = request.query_params.get('fine_type', 'both')
            result = []
            for loan in b_loans:
                if lib_branch_id is not None:
                    lib_branch_id = int(lib_branch_id)
                    if lib_branch_id == loan.book.lib_branch.id:
                        result.append(self.vh.get_loan_data(loan, fine_type=fine_type))
                else:
                    result.append(self.vh.get_loan_data(loan, fine_type=fine_type))
            return Response(result)
        except:
            msg = 'Error getting book loan data for card_no: {0}.'.format(card_no)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        '''Method Not Allowed.
        '''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def create(self, request):
        '''Method Not Allowed. Fines are created by system.
        '''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def update(self, request, pk=None):
        '''Updates book loan fine

        **Usage**
        ::
            PUT http://foo.com/books/fines/<fines ID>/

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        paid_amt           float       Yes        Amt paid towards fine
        ================== =========== ========== =============================

        **Sample Request**
        ::
            {
            }

        **Sample Response**
        ::
            {}
        '''

        fields = [
                RequestField(name='pk', required=True, is_pk=True, types=(int,), checks=[]),
                RequestField(name='paid_amt', required=True, is_pk=True, types=(int, float), checks=['is_valid_amount']),
                ]
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            fine = models.Fine.objects.get(id=pk)
            new_fine = fine.fine_amt - paid_amd
            change = 0
            if new_fine < 0:
                change = paid_amt - fine.fine_amt
                new_fine = 0
            if new_fine == 0:
                fine.paid = True
            fine.fine_amt = new_fine
            fine.save()

            resp_data = fine.values()
            resp_data['change'] = change
            return Response(resp_data)
        except:
            msg = 'Could not update Loan Entry'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
