import datetime
from librapp import models

class ViewsHelper(object):

    @staticmethod
    def get_loan_data(loan, fine_type='both'):
        book_copy = loan.book
        loan_data = {
                'isbn': book_copy.isbn.isbn,
                'lib_branch_id': book_copy.lib_branch.id,
                'card_no': loan.card_no,
                'date_out': loan.date_out,
                'date_in': loan.date_in,
                'due_date': loan.due_date,
                }
        try:
            fine_filter = {'loan_id': loan.id}
            if fine_type.lower() == 'paid':
                fine_filter = {'paid': True}
            elif fine_type.lower() == 'unpaid':
                fine_filter = {'paid': False}
            fine = models.Fine.object.get(**fine_filter)
            loan_data['fine'] = {
                    'amount': fine.amt,
                    'paid': fine.paid
                    }
        except:
            loan_data['fine'] = {
                    'amount': 0,
                    'paid': 'NA'
                    }
        return loan_data
