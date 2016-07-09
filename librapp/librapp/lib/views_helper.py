import datetime
from librapp import models

class ViewsHelper(object):

    @staticmethod
    def get_loan_data(loan, fine_type='both'):
        book_copy = loan.book
        date_in = loan.date_in
        if date_in is not None:
            date_in = date_in.isoformat()
        loan_data = {
            'isbn': book_copy.isbn.isbn,
            'lib_branch_id': book_copy.lib_branch.id,
            'card_no': loan.card_no.card_no,
            'date_out': loan.date_out.isoformat(),
            'date_in': date_in,
            'due_date': loan.due_date.isoformat(),
            }

        # TODO should not update db with GET, temp soln
        # If overdue, Update Fines
        now = datetime.datetime.now()
        naive_due_date = loan.due_date.replace(tzinfo=None) # TODO temp fix
        timediff = now - naive_due_date
        if timediff.days > 0:
            daily_fine = 0.25 # $0.25/day
            fine_amt = timediff.days * daily_fine
            fine_row = {'loan_id': loan.id}
            try:
                fine_obj = models.Fine.object.get(**fine_row)
                fine_obj.fine_amt = fine_amt
                fine_obj.save()
            except:
                fine_row['fine_amt'] = fine_amt
                models.Fine.object.create(**fine_row)

        try:
            fine_filter = {'loan_id': loan.id}
            if fine_type.lower() == 'paid':
                fine_filter = {'paid': True}
            elif fine_type.lower() == 'unpaid':
                fine_filter = {'paid': False}
            fine = models.Fine.object.get(**fine_filter)
            loan_data['fine'] = {
                    'amount': fine.fine_amt,
                    'paid': fine.paid
                    }
        except:
            loan_data['fine'] = {
                    'amount': 0,
                    'paid': 'NA'
                    }
        return loan_data
