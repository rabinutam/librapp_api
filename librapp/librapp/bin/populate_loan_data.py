'''
!! Usage Warning:
    Use this script for initial setup only, or
    to restore corrupt database
    Using it at other times can create errors in data relationship

Usage Option 1:
    $ cd librapp/bin
    $ python populate_loan_data.py

Usage Option 2:
    $ python manage.py shell
    >>> from librapp.bin.populate_loan_data import populate_data
    >>> populate_data()
'''

import django
import os
import sys
from datetime import datetime, timedelta

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


def populate_book_loan(book_count=300):
    # 200 books
    books = models.Book.objects.all()[:book_count].values()
    isbns = [_['isbn'] for _ in books]
    for i in xrange(len(isbns)):
        try:
            branchi = i%5 + 1 # 5 branches
            card_noi = i%book_count + 1
            days_ago = i%30
            date_out = datetime.now() - timedelta(days_ago)
            due_date = datetime.now() - timedelta(days_ago-14)
            book_copyi = models.BookCopy.objects.get(isbn_id=isbns[i], lib_branch_id=branchi)
            loani = {
                    "book_id": book_copyi.id,
                    "card_no_id": card_noi,
                    "date_out": date_out, # will not work because of auto_now_add=True
                    "due_date": due_date
                    }
            models.BookLoan.objects.create(**loani)
        except Exception as e:
            print e


def populate_data():
    try:
        raise Exception('Turn this exception off to run')
        # BookLoan, fines will be auto calculated
        print 'Populating Books Loans'
        populate_book_loan()
        print 'Done'
    except Exception as e:
        print 'Error'
        print e


if __name__ == '__main__':
    populate_data()
