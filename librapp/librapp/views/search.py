import traceback
from itertools import chain
from rest_framework import viewsets, status
from rest_framework.response import Response

from librapp import models
from librapp.lib.rbac import RBAC
from librapp.lib.request_field import RequestField
from librapp.lib.request_validator import RequestValidation, ValidationError
from librapp.lib.views_helper import ViewsHelper
from librapp.utils.date_utils import DateUtils


class SearchViewSet(viewsets.ViewSet):
    '''API Endpoint to search books and availability

    **API Endpoint**
    ::
        http://foo.com/search/

    **Methods:**
        - list

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
        '''Responds with list of search events matches. Searches against ISBN, Title, Author.

        **Usage**
        ::
            Search Books:
                GET http://foo.com/search/?q=<search string>/

        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        q                  string      Yes        Search string, min length: 4
        lib_branch_id      integer     No         library branch id
        ================== =========== ========== =============================

        **Sample Request**
        ::
            GET http://foo.com/search/?q=spring/

        **Sample Response**
        ::
            {
                "books": [
                    {
                    },
                    {
                    }
                ]
            }
        '''

        fields = [
                RequestField(
                    name='q',
                    query_param=True,
                    required=True,
                    types=(str, unicode),
                    checks=['check_search_string']),
                RequestField(
                    name='lib_branch_id',
                    query_param=True,
                    required=False,
                    types=(int, long),
                    checks=[]),
                ]
        #checks = ['login']
        checks = []

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        query = request.query_params.get('q')
        lib_branch_id = request.query_params.get('lib_branch_id', 0)

        try:
            # Searches against ISBN, Title, Author's name.
            books = models.Book.objects.filter(isbn=query)
            if not books:
                # Filter Can have only one __icontains
                book_filter = {'title__icontains': query}
                books1 = models.Book.objects.filter(**book_filter)
                author_filter = {'name__icontains': query}
                authors = models.Author.objects.filter(**author_filter)
                if authors:
                    author_ids = [_.id for _ in authors]
                    author_book = models.BookAuthors.objects.filter(author_id__in=author_ids)
                    books2 = [_.isbn for _ in author_book]
                    books = list(chain(books1, books2))
            books_data = self._get_books_data(books, lib_branch_id=lib_branch_id)
            result = {
                'books': books_data,
                'count': len(books_data)
                }
            return Response(result)
        except:
            raise
            msg = 'Error getting Books.'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

    def _get_books_data(self, db_objs, lib_branch_id=0):
        books_data = []
        for book in db_objs:
            booki = {
                'isbn': book.isbn,
                'title': book.title,
                'cover': book.cover
                }
            book_author = models.BookAuthors.objects.filter(isbn=book.isbn)
            booki['authors'] = [_.author.name for _ in book_author]
            books_data.append(booki)
            copy_filter = {'isbn': book.isbn}
            if lib_branch_id:
                copy_filter['lib_branch_id'] = lib_branch_id
            book_copy = models.BookCopy.objects.filter(**copy_filter).values()
            booki['availability'] = book_copy
        return books_data
