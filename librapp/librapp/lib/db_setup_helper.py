'''
Use this class to populate database

**Usage**
dbhelper = DBSetupHelper()
dbhelper.create_user(entry={...})
and so on
'''

from librapp import models


class DBSetupHelper(object):

	def create_book(self, entry=None):
		'''
		**Parameters**
		============ ======== ===========
		Name         Type     Required
		============ ======== ===========
		entry        dict     Yes
		============ ======== ===========
		'''
		if not entry:
			print 'user data for db is missing'
			return
		try:
			# username = email is unique
			book = models.Books.objects.get(isbn=entry['isbn'])
		except models.User.DoesNotExist:
			# use create_user to enable password encryption (hash and salt), and not just create
			book = models.User.objects.create_user(**entry)
		return user

	def create_books(self, entries=None):
		''' entries is list of dict
		'''
		if not entries:
			print 'data entries for db are missing'
			return
		coll = []
		for entry in entries:
			item = self.create_user(entry=entry)
			coll.append(item)
		return coll
