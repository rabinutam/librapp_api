'''
!! Usage Warning:
    Use this script for initial setup only, or
    to restore corrupt database
    Using it at other times can create errors in data relationship

Usage Option 1:
    $ cd librapp/bin
    $ python populate_init_db_data.py

Usage Option 2:
    $ python manage.py shell
    >>> from librapp.bin.populate_init_db_data import setup_init_db
    >>> setup_init_db()
'''

import django
import os
import sys

# path to BASE_DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INIT_DATA_PATH = os.path.join(BASE_DIR, 'librapp', 'bin', 'InitData')
sys.path.append(BASE_DIR)

# librapp settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "librapp.settings")
django.setup()

# do this after settings
from librapp.lib.db_setup_helper import DBSetupHelper
from librapp.lib.file_helper import FileHelper
from librapp import models

dbhelper = DBSetupHelper()
fh = FileHelper()

def clean_borrower():
    models.Borrower.objects.all().delete()

def populate_borrower():
    data_file_path = os.path.join(INIT_DATA_PATH, 'borrowers.csv')
    data = fh.read(file_path=data_file_path, sep=',')
    for datai in data:
        try:
            row = {
                'card_no': int(datai[0][2:]),
                'ssn': datai[1].replace('-', ''),
                'fname': datai[2],
                'lname': datai[3],
                'email': datai[4],
                'address': '{0} {1} {2}'.format(datai[5], datai[6], datai[7]),
                'phone': datai[8],
                }
            models.Borrower.objects.create(**row)
        except Exception as e:
            print e

def clean_library_branch():
    models.LibraryBranch.objects.all().delete()

def populate_library_branch():
    data_file_path = os.path.join(INIT_DATA_PATH, 'library_branch.csv')
    data = fh.read(file_path=data_file_path, sep='\t') # empty sep
    for datai in data:
        try:
            row = {
                'id': int(datai[0]),
                'branch_name': datai[1],
                'address': datai[2],
                }
            models.LibraryBranch.objects.create(**row)
        except Exception as e:
            print e

def clean_book():
    # Clean, sequence is important, otherwise violates referential integrity
    models.Book.objects.all().delete()
    models.Author.objects.all().delete()
    models.BookAuthors.objects.all().delete()

def populate_book():
    data_file_path = os.path.join(INIT_DATA_PATH, 'books.csv')
    data = fh.read(file_path=data_file_path, sep='\t') # empty sep
    for datai in data:
        try:
            book_row = {
                'isbn': datai[0],
                'title': datai[2],
                'cover': datai[4],
                }
            authors = datai[3].split(',')
            authors = [_.strip().lower().title() for _ in authors]
            book = models.Book.objects.create(**book_row)
            for author_name in authors:
                author = models.Author.objects.get_or_create(name=author_name)[0]
                book_author_row = {
                        'isbn': book,
                        'author': author
                        }
                models.BookAuthors.objects.create(**book_author_row)
        except Exception as e:
            print e

def clean_book_copy():
    models.BookCopy.objects.all().delete()

def populate_book_copy():
    data_file_path = os.path.join(INIT_DATA_PATH, 'book_copies.csv')
    data = fh.read(file_path=data_file_path, sep='\t') # empty sep
    for datai in data:
        try:
            row = {
                'isbn': models.Book.objects.get(isbn=datai[0]),
                'lib_branch': models.LibraryBranch.objects.get(id=datai[1]),
                'no_of_copies': datai[2]
                }
            models.BookCopy.objects.create(**row)
        except Exception as e:
            print e


def setup_init_db():
    try:
        # Clean, sequence is important, otherwise violates referential integrity
        print 'Cleaning database'
        clean_book()
        clean_borrower()
        clean_library_branch()
        clean_book_copy()

        # Book, Author
        print 'Populating Book, Author'
        populate_book()
        # Borrower
        print 'Populating Borrower'
        populate_borrower()
        # Library Branch
        print 'Populating Library Branch'
        populate_library_branch()
        # Book Copies
        print 'Populating Book Copy'
        populate_book_copy()
        print 'Done'
    except Exception as e:
        print 'Error'
        print e


if __name__ == '__main__':
    setup_init_db()
