import traceback
from django.db import IntegrityError as DBIntegrityError
from rest_framework import viewsets, status
from rest_framework.response import Response

from librapp import models
from librapp.lib.rbac import RBAC
from librapp.lib.request_field import RequestField
from librapp.lib.request_validator import RequestValidation, ValidationError


class MembershipRequestsViewSet(viewsets.ViewSet):
    '''API Endpoint to access membership requests

    **API Endpoint**
    ::
        http://foo.com/membership_requests/

    **Methods:**
        - list
        - retrieve : not allowed
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

    rbac = RBAC()

    def _get_response_data(self, db_obj=None):
        response_data = {
                'id': db_obj.id,
                'username': db_obj.user.username,
                'organization_id': db_obj.organization.id,
                'role': db_obj.role,
                'state': db_obj.state,
                'created': db_obj.created.isoformat(),
                'last_modified': db_obj.created.isoformat()
                }
        return response_data


    def list(self, request):
        '''Responses with a list of memberships request for the logged in org admin's org
        Only Org Admin can view Org's Membership Requests.

        **Usage**
        ::
            All Membership Requests for a organization:
                GET http://foo.com/membership_requests?organization_id=<id>
            Membership Requests for a organization for a state:
                GET http://foo.com/membership_requests?organization_id=<id>&state=<state>

        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        organization_id    integer     Yes        organization ID
        state              string      No         options: pending, approved, denied
        ================== =========== ========== =============================

        **Sample Request**
        ::
            GET http://foo.com/membership_requests?organization_id=8

        **Sample Response**
        ::
            {"membership_requests": []}

        **Sample Request**
        ::
            GET http://foo.com/membership_requests?organization_id=8&state=pending

        **Sample Response**
        ::
            {"membership_requests": [
                {
                    "id": 2,
                    "username": abc123123@utdallas.edu,
                    "organization_id": 8,
                    "role": "member",
                    "state": "pending",
                    "created": "2016-03-14M22:23:14.518298",
                    "last_modified": "2016-03-14M22:23:14.518298"
                },
                {
                    "id": 21,
                    "username": xyz120120@utdallas.edu,
                    "organization_id": 8,
                    "role": "member",
                    "state": "pending",
                    "created": "2016-03-15T12:23:14.518298",
                    "last_modified": "2016-03-15T12:23:14.518298"
                },
                ...
                ]
            }
        '''

        fields = [
                RequestField(
                    name='organization_id',
                    required=True,
                    query_param=True,
                    types=(int, long),
                    checks=['does_organization_exist', 'is_organization_admin']),
                RequestField(
                    name='state',
                    query_param=True,
                    types=(str, unicode),
                    checks=['is_valid_state']),
                ]
        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        req_filter = {'organization_id': request.query_params['organization_id']}
        state = request.query_params.get('state')
        if state:
            req_filter['state'] = state

        try:
            mreqs = models.MembershipRequest.objects.filter(**req_filter)
            result = []
            for req in mreqs:
                result.append(self._get_response_data(db_obj=req))
            return Response({'membership_requests': result})
        except:
            msg = 'Error getting Membership Requests'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        '''Method Not Allowed
        '''

        msg = 'Method Not Allowed'
        return Response({'msg': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def create(self, request):
        '''Creates a Membership Request.
        Any user who is not a member of Org, can request for Org's membership.

        **Usage**
        ::
            POST http://foo.com/membership_requests/

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        organization_id    integer     Yes        ID of Organization to be member of
        ================== =========== ========== =============================

        **Sample Request body**
        ::
            {
                "organization_id": 9
            }

        **Sample Response**
        ::
            {
                "id": 2,
                "username": abc123123@utdallas.edu,
                "organization_id": 8,
                "role": "member",
                "state": "pending",
                "created": "2016-03-14M22:23:14.518298",
                "last_modified": "2016-03-14M22:23:14.518298"
            }
        '''

        fields = [
                RequestField(name='organization_id', required=True, types=(int, long), checks=['does_organization_exist']),
                ]
        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        user = vres.user # current User
        organization_id = request.data['organization_id']

        mem_entry = {
                'user_id': user.id,
                'organization_id': organization_id,
                }
        count = models.Membership.objects.filter(**mem_entry).count()
        if count > 0: # count can be 0 or 1
            msg = 'User: {0} is already a member to Organization: {1}'.format(user.username, organization_id)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

        db_entry = {
                'user_id': user.id,
                'organization_id': organization_id,
                'state': 'pending'
                }

        try:
            req = models.MembershipRequest.objects.create(**db_entry)
            response_hash = self._get_response_data(db_obj=req)
            return Response(response_hash)
        except DBIntegrityError:
            msg = 'Membership Request to Organization: {0} from user: {1}, already exists.'.format(
                    organization_id, user.username)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
        except:
            msg = 'Could not create Membership Request to Organization: {0}'.format(organization_id)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None):
        '''Updates ie Approves or Denies a Membership Request.
        Only Org Admin can update Org's Membership Requests.

        **Usage**
        ::
            PUT http://foo.com/membership_requests/<id>/

        **Request body**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        state              string      Yes        options: approved, denied
        ================== =========== ========== =============================

        **Sample Request body**
        ::
            {
                "update": "approved"
            }

        **Sample Response**
        ::
            {
                "id": 2,
                "username": abc123123@utdallas.edu,
                "organization_id": 8,
                "role": "member",
                "state": "approved",
                "created": "2016-03-14M22:23:14.518298",
                "last_modified": "2016-03-15T20:23:14.518298"
            }
        '''

        fields = [
                RequestField(
                    name='state',
                    required=True,
                    types=(str, unicode),
                    checks=['is_valid_state']),
                ]
        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            req = models.MembershipRequest.objects.get(id=pk)

            is_organization_admin = self.rbac.is_organization_admin(vres.user, req.organization_id)
            if not is_organization_admin:
                msg = 'You must be an admin of the organization to approve or deny (ie update) its membership request'
                return Response({'msg': msg}, status=status.HTTP_403_FORBIDDEN)

            state = request.data['state']
            if state == 'approved':
                #add to Membership table
                db_entry = {
                    'user_id': req.user_id,
                    'organization_id': req.organization_id,
                    'role': req.role
                    }
                models.Membership.objects.create(**db_entry)

            # Finally
            req.state = state
            req.save()
            response_hash = self._get_response_data(db_obj=req)
            return Response(response_hash)
        except models.MembershipRequest.DoesNotExist:
            msg = 'Membership Request: {0} does not exist'.format(pk)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
        except:
            msg = 'Could not update Membership Request'
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        '''Deletes memberships request for the given ID.
        Only Org Admin can delete Org's Membership Requests.

        **Usage**
            DELETE "http://foo.com/membership_requests/<id>/"

        **Sample Request**
        ::
            DELETE "http://foo.com/membership_requests/6"

        **Sample Response**
        ::
            OK
        '''

        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            req = models.MembershipRequest.objects.get(id=pk)
            organization_id = req.organization_id
            is_organization_admin = self.rbac.is_organization_admin(vres.user, organization_id)
            if not is_organization_admin:
                msg = 'You must be an admin of the organization to delete its membership request'
                return Response({'msg': msg}, status=status.HTTP_403_FORBIDDEN)
            req.delete()
            return Response()
        except models.MembershipRequest.DoesNotExist:
            msg = 'Membership Request: {0} does not exist'.format(pk)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
        except:
            msg = 'Error deleting Membership Request: {0}'.format(pk)
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
