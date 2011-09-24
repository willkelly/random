#!/usr/bin/python

from urllib2 import Request, urlopen
import cookielib
import json
from pprint import pprint
from functools import partial

def compose(o,i):
    def f(*args, **kwargs):
        return o(i(*args,**kwargs))
    return f

def ks_api(token, url=None, obj=None, 




















def json_or_blank(s):
    try:
        return json.loads(s)
    except ValueError:
        return ""

def req(url=None, method="GET", data=None, headers=[], handler=None):
    request = Request(url, data=data)
    for header in headers:
        request.add_header(header[0], header[1])
    request.get_method = lambda: method
    return request

def go(request, handler=None):
    resp = urlopen(request).read()
    if callable(handler):
        return handler(resp)
    else:
        return resp

def admin_req(token, *args, **kwargs):
    request = req(*args, **kwargs)
    request.add_header("X-Auth-Token",token)
    return request

def admin_call(token, *args, **kwargs):
    return go(admin_req(token, *args, **kwargs))

def json_admin_req(token, *args, **kwargs):
    request = admin_req(token, *args, **kwargs)
    request.add_header("Accept", "application/json")
    request.add_header("Content-type", "application/json")
    return request

def json_admin_call(token, *args, **kwargs):
    print token
    return go(json_admin_req(token, *args, **kwargs), handler=json_or_blank)

def ks_url(api="endpointTemplates/", ks_base="http://localhost:5001/v2.0/"):
    return ks_base + api
  
#Service Stuff

def get_Services(token, api="services/"):
    print ks_url(api=api)
    t = json_admin_call(token, url=ks_url(api=api))
    pprint(t)
    return t
    
def Service(svc, description):
    return json.dumps({"service": {"id": svc, "description": description}})

def create_Service(token, svc, description, api="services/", ks_base=ks_base):
    if not has_Service(token, svc):
        return json_admin_call(token, url=ks_url(api=api), method="POST", data=Service(svc, description))
    
def delete_Service(svc, description="", api="services/", ks_base=ks_base):
    print ks_url(api+svc)
    return json_admin_req(ks_url(api=api+svc), method="DELETE")

def get_Service(token, svc, api="services/"):
    return [ x for x in get_Services(token, api=api)['services']['values'] if x['id'] == svc ]

def has_Service(token, svc, api="services/", ks_base=ks_base):
    return len(get_Service(token, svc, api=api)) != 0
 
#Endpoint Stuff

def get_endpointTemplates(token, api="endpointTemplates/"):
    return json_admin_call(token, ks_url(api=api))

def get_endpointTemplatesForSvc(token, svc, api="endpointTemplates/"):
    return [x for x in get_endpointTemplates(token, api=api)['endpointTemplates']['values'] 
              if x['serviceId'] == svc]

def has_endpointTemplateForSvc(token, svc, api="endpointTemplates/"):
    return len(get_endpointTemplatesForSvc(token, svc, api)) != 0

def json_endpointTemplate(region, svc, admin_url, internal_url, 
                          public_url, enabled, is_global):
     return json.dumps({"endpointTemplate": {u'adminURL': admin_url,
                        u'enabled': enabled,
                        u'global': is_global,
                        u'internalURL': internal_url,
                        u'publicURL': public_url,
                        u'region': region,
                        u'serviceId': svc}})

def create_endpointTemplate(token, region, svc, admin_url, internal_url, public_url, 
                            enabled=True, is_global=True, 
                            api="endpointTemplates/", headers=[]):
    create_Service(token, svc, svc)
    if not has_endpointTemplateForSvc(token, svc):
        return json_admin_call(token, ks_url(api=api), method="POST", headers=headers,
                          data=json_endpointTemplate(region,svc,admin_url,internal_url,
                                                     public_url,enabled,is_global))

#Tenant Stuff

def get_tenants(api="tenants/", ks_base=ks_base):
    return json_admin_req(ks_url(api=api))
