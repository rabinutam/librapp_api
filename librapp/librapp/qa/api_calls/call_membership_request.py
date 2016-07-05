
import datetime
import random
from api_call import APICall

if __name__=='__main__':
    base_url = 'http://localhost:8000/'
    api_path = 'membership_requests'
    call = APICall(base_url=base_url, api_path=api_path)
    call.start_session(username='prg130130@utdallas.edu', password='dallasrocks')
    uid = 11 # prg130130@utdallas.edu
    oid = 8 # uid 11 is admin of oid 8

    randid = random.randint(1,10)
    randid2 = random.randint(5,15)
    now = datetime.datetime.now()

    # List :: 
    query_params = {"organization_id": oid, "state": "pending"}
    query_params = {"organization_id": oid} 
    query_params = {} # missind org id
    query_params = {"organization_id": 1111} #DNE
    query_params = {"organization_id": oid, "state": "pe"} #invalid state option
    query_params = {"organization_id": oid, "state": 1} #invalid state type
    query_params = {"organization_id": 'a', "state": "pending"} # invalid org id type
    call.listt(query_params=query_params)

    # Retrieve
    pk = 1
    query_params = {}
    #call.retrieve(pk=pk, query_params=query_params)

    # Create
    request_data = {'organization_id': randid}
    request_data = {'organization_id': 0} #DNE
    request_data = {'organization_id': 'a'} #invalid type
    request_data = {} # missing org id
    #call.create(request_data=request_data)

    # Update
    request_data = {'state': 'approved'} #ok
    request_data = {'state': 'a'} # invalid option
    request_data = {'state': 1} # invalid type
    request_data = {} # missing state
    #call.update(pk=randid, request_data=request_data)

    # Delete
    #call.destroy(pk=998) #DNE
    #call.destroy(pk=8)
    #call.destroy(pk=randid2)
