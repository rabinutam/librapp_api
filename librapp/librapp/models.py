'''
Refer:
    https://docs.djangoproject.com/en/1.9/ref/models/fields/
'''

from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    isbn = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=200)
    cover = models.URLField()

class Author(models.Model):
    # id is assigned by default
    name = models.CharField(max_length=100)

class BookAuthors(models.Model):
    isbn = models.ForeignKey(Book)
    author = models.ForeignKey(Author)

class LibraryBranch(models.Model):
    # id is assigned by default
    branch_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

class BookCopy(models.Model):
    # id = book_id is assigned by default
    isbn = models.ForeignKey(Book)
    lib_branch = models.ForeignKey(LibraryBranch)
    no_of_copies = models.IntegerField(default=0)

class Borrower(models.Model):
    #card_no = models.AutoField(primary_key=True)
    card_no = models.IntegerField(primary_key=True)
    ssn = models.CharField(max_length=9, unique=True)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True)
    email = models.EmailField(max_length=100, null=True)

class BookLoan(models.Model):
    # id = loan_id is assigned by default
    book = models.ForeignKey(BookCopy)
    card_no = models.ForeignKey(Borrower)
    date_out = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField() # 14 days from date_out
    date_in = models.DateTimeField(null=True)

class Fine(models.Model):
    # id is assigned by default
    loan = models.ForeignKey(BookLoan, unique=True) # one fine entry per loan
    fine_amt = models.DecimalField(max_digits=6, decimal_places=2)
    paid = models.BooleanField(default=False)
