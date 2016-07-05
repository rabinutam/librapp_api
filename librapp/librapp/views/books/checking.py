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


class CheckingViewSet(viewsets.ViewSet):
    '''API Endpoint to access events

    **API Endpoint**
    ::
        http://foo.com/books/checking/

    **Methods:**
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

    dutils = DateUtils()
    rbac = RBAC()
    vh = ViewsHelper()


    def list(self, request):
        '''Responses with a list of 

        **Usage**
        ::
            GET http://foo.com/books/checking/

        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        organization_id    integer     No         organization ID
        my_events          bool        No         lists User's RSVPed events
        ================== =========== ========== =============================

        **Sample Request**
        ::
            GET http://foo.com/books/checking/

        **Sample Response**
        ::
            {}
        '''
        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        fields = []
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            data = []
            return Response({'data': data})
        except:
            msg = 'Error getting data.'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def create(self, request):
        '''Creates a Book check in entry

        **Usage**
        ::
            POST http://foo.com/books/checking/

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        lib_branch_id      integer     Yes        library branch id
        isbn               string      Yes        book isbn
        card_no            integer     Yes        borrower card_no
        ================== =========== ========== =============================

        **Sample Request**
        ::
            {
                "lib_branch_id": 1,
                "isbn": "0151009376",
                "card_no": 1
            }

        **Sample Response**
        ::
            {}
        '''

        fields = [
                RequestField(name='lib_branch_id', required=True, types=(int), checks=[]),
                RequestField(name='isbn', required=True, types=(str, unicode), checks=[]),
                RequestField(name='card_no', required=True, types=(int), checks=[]),
                ]
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            # data
            lib_branch_id = request.data.get('lib_branch_id')
            isbn = request.data.get('isbn')
            card_no = request.data.get('card_no')

            book_copy = models.BookCopy.objects.get(isbn=isbn, lib_branch_id=lib_branch_id)

            b_loans = models.BookLoan.objects.filter(card_no=card_no)
            loan_count = b_loans.count()

            # Check fine
            if loan_count:
                for loan in b_loans:
                    try:
                        fine = models.Fine.objects.get(loan_id=loan.id)
                        if fine.fine_amt and not fine.paid:
                            msg = 'Unpaid fines. Cannot borrow any books at this time'
                            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
                    except models.Fine.DoesNotExist:
                        pass # no problem

            # Check borrow limit (max 3 books)
            if loan_count >= 3:
                msg = 'Cannot borrow more that 3 books at a time'
                return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

            # Check if available
            if book_copy.no_of_copies == 0:
                msg = 'Book is not available'
                return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

            # create a new record in book loan table
            book_loan_row = {
                    'book': book_copy.id,
                    'card_no': card_no,
                    'due_date': datetime.now() + timedelta(14)
                    }
            book_loan_obj = models.BookLoan.objects.create(**book_loan_row)

            # update available copies
            book_copy.no_of_copies -= 1
            book_copy.save()
            return Response(book_loan_obj.values())
        except:
            msg = 'Could not create Loan Entry'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
