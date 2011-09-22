#!/usr/bin/python

from urllib2 import Request, urlopen
import cookielib
import json
from pprint import pprint

ks_base="http://localhost:5001/v2.0"

def mk_req(url, method="GET", data=None, headers=[]):
    req = Request(url, data=data)
    for header in headers:
        req.add_header(header[0], header[1])
    req.get_method = lambda: method
    return req

def mk_admin_req(url, method="GET", data=None, headers=[], token="999888777666"):
    headers.append(["X-Auth-Token",token])
    return mk_req(url, method, data, headers)

def ks_url(api="endpointTemplates/", ks_base="http://localhost:5001/v2.0"):
    return ks_base + api

def json_admin_req(url, method="GET", data=None, headers=[]):
    return json.loads(urlopen(mk_admin_req(url, method, data, headers)).read())


#Endpoint Stuff

def get_endpointTemplates(api="endpointTemplates/", ks_base=ks_base):
    return json_admin_req(ks_url(api=api))

def get_endpointTemplatesForSvc(svc, api="endpointTemplates/", ks_base=ks_base):
    return [x for x in get_endpointTemplates(api, ks_base)['endpointTemplates']['values'] 
              if x['serviceId'] == svc]

def has_endpointTemplateForSvc(svc, api="endpointTemplates/", ks_base=ks_base):
    return len(get_endpointTemplatesForSvc(svc, api, ks_base)) != 0

#def create_endpointTemplate(admin_url="", internal_url="", public_url="") 
#def update_endpointTemplate(

#Tenant Stuff

def get_tenants(api="tenants/", ks_base=ks_base):
    return json_admin_req(ks_url(api=api))

#Main

def main():
    # I get svc_name, 3 urls for ept, bools, + tenant name to add endpoints to
    ep = get_endpointTemplates()
    pprint(get_endpointTemplatesForSvc("nova"))
    pprint(has_endpointTemplateForSvc("nova"))
    pprint(get_tenants())

if __name__ == "__main__":
    main()
