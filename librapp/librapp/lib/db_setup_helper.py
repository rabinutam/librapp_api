'''
Use this class to populate database

**Usage**
dbhelper = DBSetupHelper()
dbhelper.create_user(entry={...})
and so on
'''

from librapp import models


class DBSetupHelper(object):

	def create_user(self, entry=None):
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
			user = models.User.objects.get(username=entry['username'])
		except models.User.DoesNotExist:
			# use create_user to enable password encryption (hash and salt), and not just create
			user = models.User.objects.create_user(**entry)
		return user

	def create_users(self, entries=None):
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

	def create_organization(self, entry=None):
		'''
		**Parameters**
		============ ======== ===========
		Name         Type     Required
		============ ======== ===========
		entry        dict     Yes
		============ ======== ===========
		'''
		if not entry:
			print 'org data for db is missing'
			return
		try:
			# organization, institution combination is unique
			org = models.Organization.objects.get(name=entry['name'], edu_institution_id=entry['edu_institution'].id)
		except models.Organization.DoesNotExist:
			org = models.Organization.objects.create(**entry)
		return org

	def create_organizations(self, entries=None):
		''' entries is list of dict
		'''
		if not entries:
			print 'data entries for db are missing'
			return
		orgs = []
		for entry in entries:
			org = self.create_organization(entry=entry)
			orgs.append(org)
		return orgs

	def delete_organizations(self):
		models.Organization.objects.all().delete()

	def create_edu_institution(self, entry=None):
		if not entry:
			print 'edu institution data for db is missing'
			return
		try:
			# assume education institution name is unique
			edu = models.EduInstitution.objects.get(name=entry['name'])
		except models.EduInstitution.DoesNotExist:
			edu = models.EduInstitution.objects.create(**entry)
		return edu

	def delete_edu_institutions(self):
		models.EduInstitution.objects.all().delete()

	def create_membership(self, entry=None):
		if not entry:
			print 'membership data for db is missing'
			return
		mem = models.Membership.objects.get_or_create(**entry)
		return mem

	def create_memberships(self, entries=None):
		''' entries is list of dict
		'''
		if not entries:
			print 'data entries for db are missing'
			return
		coll = []
		for entry in entries:
			item = self.create_membership(entry=entry)
			coll.append(item)
		return coll

	def delete_admin_roles(self):
		models.Membership.objects.filter(role='admin').delete()
