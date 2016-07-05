import logging
from librapp import models

class RBAC(object):
    '''Role Based Access Control
    role : options = member, admin
    user : user db obj
    '''

    def get_user_membership(self, user):
        user_mem = models.Membership.objects.filter(user_id=user.id)
        return user_mem

    def get_user_organizations(self, user):
        user_mem = self.get_user_membership(user)
        user_orgs = [_.organization for _ in user_mem]
        return user_orgs

    def is_organization_admin(self, user, organization_id):
        # in membershup (user, organization) taken together are unique
        try:
            user_mem = models.Membership.objects.get(user_id=user.id, organization_id=organization_id)
            if user_mem.role != 'admin':
                return False
        except:
            return False
        return True
