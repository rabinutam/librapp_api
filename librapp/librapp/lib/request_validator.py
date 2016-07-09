'''
**Usage**
    try:
        RequestValidation(request=request, checks=['check1', 'check2'], fields=[reqfield_obj1, reqfield_obj2])
    except ValidationError as e:
        return Response({'msg': e.message}, status=e.status)

    Add checks as needed, but make sure if the desired check is not already here
'''

import logging
import re
from rest_framework import status
from django.contrib.auth import authenticate, login

from librapp import models
from librapp.lib.rbac import RBAC
from librapp.utils.date_utils import DateUtils


class ValidationError(Exception):
    def __init__(self, message, status):
        super(ValidationError, self).__init__(message)
        self.status = status


class RequestValidation(object):
    '''Request Validator
    
    **Validates**
        - request body data
        - request Query Params

    **Init Parameters**
        checks_example = ['is_logged_in', 'has_permission']
        fields_example = [
            RequestField(**{'name': 'email', 'required': True, 'query_param': False,
            'field_type': (str, unicode), 'checks': ['is_valid_email', 'is_utd_email']})
            ]
    '''

    dutils = DateUtils()
    rbac = RBAC()

    def __init__(self, request=None, checks=None, fields=None, pk=None):
        self.user = None
        self._request = request
        self._request.pk = pk
        self._checks = checks if checks else []
        self._fields = fields if fields else []
        self._run_checks()

    def _get_http_code(self, code):
        if code == 400:
            return status.HTTP_400_BAD_REQUEST
        if code == 401:
            return status.HTTP_401_UNAUTHORIZED
        if code == 403:
            return status.HTTP_403_FORBIDDEN

    def _set_result(self, is_valid, message, status):
        self.is_valid = is_valid
        self.message = message
        self.status = status

    def _run_checks(self):
        '''
        global checks, and
        field specific local checks
        '''
        # Collective Checks
        self._preprocess_data() # may need it

        # Global Checks. Run this before all other checks.
        self._run_global_checks()

        # Check required fields are there and not empty
        self._check_required_fields()

        # Check Field Type
        self._check_field_types()

        # Run field specific local checks
        self._run_field_checks()

    def _preprocess_data(self):
        pass

    def _get_data(self, field):
        data = None

        if field.is_pk:
            data = self._request.pk
        elif field.query_param:
            data = self._request.query_params.get(field.name)
        else:
            data = self._request.data.get(field.name)

        if isinstance(data, (str, unicode)):
            data = data.strip()

        return data

    def _should_check_field(self, field):
        check_type = False
        if field.required:
            check_type = True
        elif field.name in self._request.data or field.name in self._request.query_params:
            check_type = True
        return check_type

    def _check_field_types(self):
        for field in self._fields:
            if field.types and self._should_check_field(field):
                data = self._get_data(field)
                msg = 'Expected type for {0} was {1}. Found: {2}'.format(field.name, field.types, type(data))
                if all(_ in (int, long) for _ in field.types):
                    try:
                        int(data)
                    except:
                        raise ValidationError(msg, self._get_http_code(400))
                elif bool in field.types:
                    if not data.lower() in ['true', 'false']:
                        raise ValidationError(msg, self._get_http_code(400))
                elif not isinstance(data, field.types):
                    raise ValidationError(msg, self._get_http_code(400))

    def _check_required_fields(self):
        for field in self._fields:
            if field.required:
                data = self._get_data(field)
                if data is None:
                    msg = '{0} is required field. Not found.'.format(field.name)
                    raise ValidationError(msg, self._get_http_code(400))
                # check required field value is not empty()
                if data == '' or data == []:
                    msg = '{0} is empty. No value found.'.format(field.name)
                    raise ValidationError(msg, self._get_http_code(400))

    def _run_check(self, check, field=None):
        # prevent looping
        if re.match('^_?run_.*checks?$', check):
            return

        if not check.startswith('_'):
            check = '_{0}'.format(check)

        if field is None:
            getattr(self, check)()
        else:
            getattr(self, check)(field)

    def _run_global_checks(self):
        for check in self._checks:
            self._run_check(check)

    def _run_field_checks(self):
        # Field Specific Checks
        for field in self._fields:
            if self._should_check_field(field):
                for check in field.checks:
                    self._run_check(check, field=field)

    ######## General Validation ########

    def _is_valid_email(self, field):
        data = self._get_data(field)
        if re.match(r'.*@\w*\.\w*$', data) is None:
            msg = '{0}: {1} is in invalid format.'.format(field.name, data)
            raise ValidationError(msg, self._get_http_code(400))
 
    def _is_valid_utd_email(self, field):
        data = self._get_data(field)
        if re.match(r'.*@utdallas.edu', data) is None:
            msg = 'UTD {0}: {1} is in invalid format.'.format(field.name, data)
            raise ValidationError(msg, self._get_http_code(400))

    def _is_valid_amount(self, field):
        data = float(self._get_data(field))
        if float < 0:
            msg = '{0}: {1} is negative and not valid.'.format(field.name, data)
            raise ValidationError(msg, self._get_http_code(400))

    def _ssn_does_not_exist(self, field):
        data = self._get_data(field)
        try:
            models.Borrower.objects.get(ssn=data)
        except models.Borrower.DoesNotExist:
            pass
        else:
            msg = 'Borrower with {0}: {1} already exists.'.format(field.name, data)
            raise ValidationError(msg, self._get_http_code(400))

    def _is_valid_privacy(self, field):
        return

    def _is_valid_state(self, field):
        return
    
    def _is_iso_format(self, field):
        data = self._get_data(field)
        try:
            self.dutils.get_dt_from_iso(data)
        except:
            msg = '{0}: {1} is not in ISO 8601 format.'.format(field.name, data)
            raise ValidationError(msg, self._get_http_code(400))


    ######## Auth and User Validation ########

    def _login(self):
        # uses TokenAuthBackend
        user = authenticate(request=self._request)
        if user is None:
            msg = 'Invalid token. Cannot Authenticate.'
            raise ValidationError(msg, self._get_http_code(401))
        self.user = user
        login(self._request, user)

    def _does_username_exist(self, field):
        data = self._get_data(field)
        try:
            models.User.objects.get(username=data)
        except:
            msg = 'funed {0}: {1} does not exist.'.format(field.name, data)
            raise ValidationError(msg, self._get_http_code(400))

    def _check_password(self, field):
        data = self._get_data(field)
        if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', data) is None:
            msg = '{0} is in invalid format.'.format(field.name)
            raise ValidationError(msg, self._get_http_code(400))

    ######## RBAC Validation ########

    def _is_admin(self, field):
        pass


    ######## Search Validation ########
    def _check_search_string(self, field):
        data = self._get_data(field)
        data = data.strip()
        if len(data) < 4:
            msg = 'Search string must be at least 4 character long'
            raise ValidationError(msg, self._get_http_code(400))
