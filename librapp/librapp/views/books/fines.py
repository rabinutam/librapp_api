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
        - retrieve
        - list
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
        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def create(self, request):
        '''Creates a Book check in entry

        **Usage**
        ::
            POST http://foo.com/books/fines/

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
            # Check fine
            if b_loans:
                for loan in b_loans:
                    try:
                        fine = models.Fine.objects.get(loan_id=loan.id)
                        if fine.fine_amt and not fine.paid:
                            msg = 'Unpaid fines. Cannot borrow any books at this time'
                            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
                    except models.Fine.DoesNotExist:
                        pass # no problem

            # Check borrow limit (max 3 books)
            # Active loan count, ie no date_in set yet
            loan_count = models.BookLoan.objects.filter(card_no=card_no, date_in=None).count()
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


    def update(self, request, pk=None):
        '''Updates book loan fine

        **Usage**
        ::
            PUT http://foo.com/books/fines/<book loan ID>/

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
                ]
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            b_loan = models.BookLoan.objects.get(id=pk)

            # Available copies increases by 1 upon checkin
            book_copy = b_loan.book
            book_copy.no_of_copies += 1
            book_copy.save()

            # Save date in
            b_loan.date_in = datetime.now()
            b_loan.save()

            return Response(b_loan.values())
        except:
            msg = 'Could not update Loan Entry'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
