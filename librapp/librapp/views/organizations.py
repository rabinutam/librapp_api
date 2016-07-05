import logging
import traceback

from rest_framework import viewsets, status
from rest_framework.response import Response

from librapp import models
from librapp.lib.rbac import RBAC
from librapp.lib.request_field import RequestField
from librapp.lib.request_validator import RequestValidation, ValidationError


class OrganizationsViewSet(viewsets.ViewSet):
    '''API Enpoint to access Organizations

    **API Endpoint**
    ::
        http://foo.com/organizations/

    **Methods:**
        - list
        - retrieve
        - create : not allowed
        - update : not allowed
        - delete : not allowed

    **HTTP Code:**
        - 200 OK
        - 400 Bad Request
        - 401 Unauthorized
        - 403 Forbidden
        - 405 Method Not Allowed
    '''

    rbac = RBAC()

    def _get_response_data(self, org):
        response_data = {
                'id': org.id,
                'name': org.name,
                'created': org.created.isoformat(),
                'last_modified': org.last_modified.isoformat(),
                'edu_institution': org.edu_institution.name,
                'website': org.website,
                'logo_url': org.logo_url,
                'description': org.description,
                'contact_name': org.contact_name,
                'contact_number': org.contact_number,
                'contact_email': org.contact_email
                }
        return response_data

    def list(self, request):
        '''Responses with a list of organizations.

        **Usage**
        ::
            All Organizations:
                GET "http://foo.com/organizations/"
            Organizations for current User (ie currently logged in User)
                GET "http://foo.com/organizations?my_organizations=true"

        **Query Parameters**

        ================== =========== ========== =============================
        name               Type        Required   Description
        ================== =========== ========== =============================
        my_organizations   boolean     No         current user's organizations
        ================== =========== ========== =============================

        **Sample Request**
        ::
            GET "http://foo.com/organizations/"

        **Sample Response**
        ::
            {"organizations": [
                {
                    "id": 6,
                    "name": "Engineering in Medicine and Biology",
                    "website": "http://www.example.com/",
                    "created": "2016-02-03T05:38:39+00:00",
                    "last_modified": "2016-02-03T05:38:39+00:00",
                    "edu_institution_id": 1,
                    "logo_url": "https://s3-us-west-2.amazonaws.com/funed/images/abc.jpg",
                    "description": "alpha beta ..."
                },
                {
                    "id": 12,
                    "name": "IEEE Industry Application Society",
                    "website": "https://www.facebook.com/IASutd/",
                    "created": "2016-02-03T05:38:39Z",
                    "last_modified": "2016-02-03T05:38:39Z",
                    "edu_institution_id": 1,
                    "logo_url": "https://s3-us-west-2.amazonaws.com/funed/images/xyz.jpg",
                    "description": "alpha beta ..."
                }
            ]}

        **Sample Request**
        ::
            GET "http://foo.com/organizations?my_organizations=true"

        **Sample Response**
        ::
            {"organizations": [
                {
                    "id": 6,
                    "name": "Engineering in Medicine and Biology",
                    "website": "http://www.example.com/",
                    "last_modified": "2016-02-03T05:38:39+00:00",
                    "edu_institution": "The University of Texas at Dallas",
                    "created": "2016-02-03T05:38:39+00:00"
                }
            ]}
        '''

        fields = [
                RequestField(
                    name='my_organizations',
                    query_param=True,
                    types=(bool,),
                    checks=[]),
                ]
        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks, fields=fields)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            my_organizations = request.query_params.get('my_organizations')
            if my_organizations=='true':
                user_orgs = self.rbac.get_user_organizations(vres.user)
                user_orgs = [self._get_response_data(org) for org in user_orgs]
                return Response({'organizations': user_orgs})
            orgs = models.Organization.objects.all().values()
            return Response({'organizations': orgs})
        except:
            msg = 'Error getting Organizations'
            logging.error('{0}. Error: {1}'.format(msg, traceback.format_exc()))
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        '''Responses with details of the selected organization.

        **Usage**
        ::
            GET "http://foo.com/organizations/<id>/"

        **Sample Request**
        ::
            GET "http://foo.com/organizations/6/"

        **Sample Response**
        ::
            {
                "id": 6,
                "name": "Engineering in Medicine and Biology",
                "website": "http://www.biomedutd.com/",
                "last_modified": "2016-02-03T05:38:39+00:00",
                "edu_institution": "The University of Texas at Dallas",
                "created": "2016-02-03T05:38:39+00:00"
            }
        '''


        checks = ['login']

        try:
            vres = RequestValidation(request=request, checks=checks)
        except ValidationError as e:
            return Response({'msg': e.message}, status=e.status)

        try:
            org = models.Organization.objects.get(id=pk)
            org_details = self._get_response_data(org)
            return Response(org_details)
        except:
            msg = 'Error getting Organization: {0} from database'.format(pk)
            logging.error('{0}. Error: {1}'.format(msg, traceback.format_exc()))
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
