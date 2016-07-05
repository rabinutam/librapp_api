
#import datetime
import random
from api_call import APICall

if __name__=='__main__':
    base_url = 'http://localhost:8000/'
    api_path = 'organizations'
    call = APICall(base_url=base_url, api_path=api_path)
    call.start_session(username='prg130130@utdallas.edu', password='dallasrocks')

    # List :: All
    query_params = {}
    call.listt(query_params=query_params)

    # List :: my_organizations
    query_params = {"my_organizations": True}
    call.listt(query_params=query_params)

    # Retrieve (no login)
    pk = random.randint(1,10)
    query_params = {}
    call.retrieve(pk=pk, query_params=query_params)
