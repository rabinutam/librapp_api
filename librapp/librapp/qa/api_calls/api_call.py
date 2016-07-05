import requests
try:
    import simplejson as json
except ImportError:
    import json

class APICall(object):

    def __init__(self, base_url='', api_path=''):
        self.base_url = base_url
        self.api_path = api_path
        self.auth_path = 'auth/login'
        self.api_url = '{0}{1}'.format(base_url, api_path)
        self.auth_url = '{0}{1}/'.format(base_url, self.auth_path)

    def start_session(self, username='', password=''):
        #TODO after implementing login
        self.s0 = requests.Session()
        adata = {'username': username, 'password': password}
        #auth0 = self.s0.post(self.auth_url, headers={'X_Auth_User': username, 'X_Auth_Password': password})
        auth0 = self.s0.post(self.auth_url, data=adata)
        self.s0.headers = auth0.headers
        self.s0.headers.update(auth0.json()) # add auth Token
        self.s0.cookies.clear()
        self._print_result(response=auth0, name='login', method='POST', http_method='POST', url=self.auth_url)

    def _print_result(self, response=None, name=None, method=None, http_method=None, url=None):
        if name is None:
            name = self.api_path
        title = '{0} {1}'.format(method, name)
        call = '{0} {1}'.format(http_method, url)
        response_str = str(response.json())
        response_str = response_str.replace("u'", '"')
        response_str = response_str.replace("'", '"')

        print 80*'='
        print title
        print len(title)*'-'
        print 'API call:: {0}'.format(call)
        print response.status_code
        print response_str

    def _get_query_string(self, query_params=None):
        query_string = '&'.join('{0}={1}'.format(k, v) for k, v in query_params.iteritems())
        return query_string

    def _get_url(self, pk=None, query_params=None):
        url = self.api_url
        if pk:
            url = "{0}/{1}/".format(url, pk)
        else:
            url = "{0}/".format(url)
        if query_params:
            query_string = self._get_query_string(query_params=query_params)
            url = '{0}?{1}'.format(url, query_string)
        return url

    def retrieve(self, pk=None, query_params=None):
        self.s0.cookies.clear()
        # Way 1
        #url = self._get_url(pk=pk, query_params=query_params)
        #response = self.s0.get(url)

        # Way 2
        url = self._get_url(pk=pk, query_params=None)
        response = self.s0.get(url, params=query_params)
        self._print_result(response=response, method='Retrieve', http_method='GET', url=url)

    def listt(self, query_params=None):
        self.s0.cookies.clear()
        url = self._get_url(query_params=query_params)
        response = self.s0.get(url)
        self._print_result(response=response, method='List', http_method='GET', url=url)

    def create(self, request_data=None):
        self.s0.cookies.clear()
        url = self._get_url()
        response = self.s0.post(url, data=json.dumps(request_data))
        self._print_result(response=response, method='Create', http_method='POST', url=url)

    def update(self, pk=None, request_data=None):
        self.s0.cookies.clear()
        url = self._get_url(pk=pk)
        response = self.s0.put(url, data=json.dumps(request_data))
        #response = self.s0.put(url, data=request_data)
        self._print_result(response=response, method='Update', http_method='PUT', url=url)

    def destroy(self, pk=None, query_params=None):
        self.s0.cookies.clear()
        url = self._get_url(pk=pk, query_params=query_params)
        response = self.s0.delete(url)
        self._print_result(response=response, method='Destroy', http_method='DELETE', url=url)
