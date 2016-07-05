
import datetime
import random
from api_call import APICall

if __name__=='__main__':
    base_url = 'http://localhost:8000/'
    api_path = 'users'
    call = APICall(base_url=base_url, api_path=api_path)
    call.start_session(username='prg130130@utdallas.edu', password='utdrocks')
    uid = 11
    oid = 8

    randid = random.randint(1,10)
    now = datetime.datetime.now()
    start = now + datetime.timedelta(1)
    end = start + datetime.timedelta(0.25)

    # List :: all
    query_params = {}
    call.listt(query_params=query_params)

    # List :: an organization's users
    query_params = {"organization_id": randid}
    call.listt(query_params=query_params)

    # Retrieve
    pk = 45
    #call.retrieve(pk=pk, query_params=query_params)

    # Create
    privacy_options = ['private', 'public']
    privacy = privacy_options[random.randint(0,1)]
    request_data = {
            'name': 'spring 2016 bash',
            'organization_id': oid,
            'location': 'central lawn',
            'address': '123 example way, Richardson, TX 75080',
            'privacy': privacy,
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'description': 'you want to be here'
            }
    #call.create(request_data=request_data)

    # Update: password
    request_data = {
            "password": "utdrocks"
            }
    pk = 11
    call.update(pk=pk, request_data=request_data)
