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


class BooksLoansViewSet(viewsets.ViewSet):
    '''API Endpoint to access book loans

    **API Endpoint**
    ::
        http://foo.com/books/loans/

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
        '''Responses with a list of book loans

        **Usage**
        ::
            GET http://foo.com/books/loans/

        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        card_no            integer     No         borrower card_no
        lib_branch_id      integer     No         library branch id
        active             bool        No         true: get active loans only
        overdue            bool        No         true: get overdue loans only (subset of active)
        ================== =========== ========== =============================

        **Sample Request**
        ::
            GET http://foo.com/books/loans/?card_no=1

        **Sample Response**
        ::
            {}
        '''

        fields = [
                RequestField(name='card_no', required=False, query_param=True, types=(int, str, unicode), checks=[]),
                RequestField(name='lib_branch_id', required=False, query_param=True, types=(int,), checks=[]),
                RequestField(name='active', required=False, query_param=True, types=(bool,), checks=[]),
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

            active = request.query_params.get('active', '')
            if active.lower() in ['true', '1']:
                loan_filter['date_in'] = None

            overdue = request.query_params.get('overdue', '')
            if overdue.lower() in ['true', '1']:
                loan_filter['date_in'] = None
                loan_filter['due_date__lt'] = datetime.now()

            b_loans = models.BookLoan.objects.filter(**loan_filter)

            lib_branch_id = request.query_params.get('lib_branch_id')
            result = []
            for loan in b_loans:
                if lib_branch_id is not None:
                    lib_branch_id = int(lib_branch_id)
                    if lib_branch_id == loan.book.lib_branch.id:
                        result.append(self.vh.get_loan_data(loan))
                else:
                    result.append(self.vh.get_loan_data(loan))
            return Response({'books_loans': result})
        except:
            msg = 'Error getting book loan data for card_no: {0}.'.format(card_no)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        '''Method Not Allowed'''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def create(self, request):
        '''Creates a Book check in entry

        **Usage**
        ::
            POST http://foo.com/books/loans/

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
                RequestField(name='lib_branch_id', required=True, types=(int,), checks=[]),
                RequestField(name='isbn', required=True, types=(str, unicode), checks=[]),
                RequestField(name='card_no', required=True, types=(int,), checks=[]),
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

            # book copy in that library
            book_copy = models.BookCopy.objects.get(isbn=isbn, lib_branch_id=lib_branch_id)

            # Check if active loan for the book_copy (book in the library) already exists
            try:
                existing_loan = models.BookLoan.objects.get(card_no=card_no, book_id=book_copy.id)
                if existing_loan.date_in is None:
                    msg = 'Cannot loan the same book twice'
                    return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
            except models.BookLoan.DoesNotExist:
                pass
            except:
                raise

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
                    'book_id': book_copy.id,
                    'card_no_id': card_no,
                    'due_date': datetime.now() + timedelta(14)
                    }
            book_loan_obj = models.BookLoan.objects.create(**book_loan_row)

            # update available copies
            book_copy.no_of_copies -= 1
            book_copy.save()
            response_data = {
                    'id': book_loan_obj.id,
                    'book_copy_id': book_loan_obj.book_id,
                    'card_no': book_loan_obj.card_no.card_no,
                    'isbn': book_loan_obj.book.isbn.isbn,
                    }
            return Response(response_data)
        except:
            msg = 'Could not create Loan Entry'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None):
        '''Updates book loan from checkout to checkin for the book loan ID

        **Usage**
        ::
            PUT http://foo.com/books/loans/<book loan ID>/

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        ================== =========== ========== =============================

        **Sample Request**
        ::
            {}

        **Sample Response**
        ::
            {}
        '''

        fields = [
                RequestField(name='pk', required=True, is_pk=True, types=(int,), checks=[]),
                ]
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields, pk=pk)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            book_loan_obj = models.BookLoan.objects.get(id=pk)

            # Check: no check in twice
            if book_loan_obj.date_in is not None:
                msg = 'Book is already checked in.'
                return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

            # Available copies increases by 1 upon checkin
            book_copy = book_loan_obj.book
            book_copy.no_of_copies += 1
            book_copy.save()

            # Save date in
            book_loan_obj.date_in = datetime.now()
            book_loan_obj.save()

            response_data = {
                    'id': book_loan_obj.id,
                    'book_copy_id': book_loan_obj.book_id,
                    'card_no': book_loan_obj.card_no.card_no,
                    'isbn': book_loan_obj.book.isbn.isbn,
                    }
            return Response(response_data)
        except:
            msg = 'Could not update Loan Entry'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
