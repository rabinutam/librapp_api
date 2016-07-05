'''Request Field: pk/id, query parameter or request data field

Example Usage:
    >>> field_data = {
            'name': 'email', 'required': True, 'query_param': True,
            'field_type': (str, unicode), 'checks': ['is_valid_email', 'is_utd_email']
            }
    >>> req_field = RequestField(**field_data)
'''

class RequestField(object):
    '''
    Applicable to:
        - Query string fields
        - Request body fields
    '''

    def __init__(self, name='', required=False, is_pk=False, query_param=False, types=None, checks=None):
        self.name = name
        self.required = required
        self.is_pk= is_pk
        self.query_param = query_param
        self.types = types if types else []
        self.checks = checks if checks else []
