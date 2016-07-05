
import datetime
from api_call import APICall

if __name__=='__main__':
    base_url = 'http://localhost:8000/'
    api_path = 'search'
    call = APICall(base_url=base_url, api_path=api_path)
    call.start_session(username='prg130130@utdallas.edu', password='dallasrocks')

    # List :: Search
    query_params = {"q": "lecture"}
    call.listt(query_params=query_params)

    # List :: Search
    query_params = {"q": "juju"}
    call.listt(query_params=query_params)

    # List :: Search, Invalid length
    query_params = {"q": "law"}
    call.listt(query_params=query_params)
