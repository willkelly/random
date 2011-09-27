from urllib2 import Request, urlopen, HTTPError
import json

class KeystoneClient(object):
    '''A simple, stupid keystone client.
TODO: Auth (requires pregenerated token at this time)
Example Usage:
>>> from keystoneclient import KeystoneClient
>>> ks = KeystoneClient("http://127.0.0.1:5001/v2.0", "999888777666")
>>> ks.tenants.get()
{u'tenants': {u'values': [{u'enabled': 1, u'id': u'demo', u'description': None}, {u'enabled': 1, u'id': u'admin', u'description': u'test'}], u'links': []}}
>>> ks.tenants.get('demo')
{u'tenant': {u'enabled': 1, u'id': u'demo', u'description': None}}
'''
    def __init__(self, url="http://localhost:5001/v2.0", token="999888777666", oname=None, root=None):
        '''Create a KeystoneClient:
Arguments:
url - the public url to a keystone resource, eg http://keystone.domain.com:5001/v2.0
token - a valid token for keystone use
oname - the singular name of the resource you are pointed to (usually can be omitted)
root - the root object (first instance) of the KeystoneClient, used to share the token
'''
        self.url = url
        self.root = root or self
        if token:
            self.token = token
        # We'll use oname if provided or guess it is resource minus 's' (tenant / tenants)
        self.oname = oname or url.rsplit("/")[-1][0:-1]
    def _req(self, method="GET", data=None, xheaders=[], inst=None):
        # make a keystone request
        url = self.url
        if inst:
            url += "/%s" % (inst)
        req = Request(url=url)
        req.data = data
        req.get_method = lambda: method
        req.add_header("X-Auth-Token", self.root.token)
        req.add_header("Content-type","application/json")
        req.add_header("Accept","application/json")
        r = urlopen(req).read()
        if r == "":
            return { str(self.oname): None }
        else:
            return json.loads(r)
    def _data(self, **kwargs):
        # structure data in proper format, munge _ variables in kwargs to allow for use of reserved words
        if not kwargs.has_key(self.oname):
            kwargs = { str(self.oname): kwargs }
        for k in [ k for k in kwargs[self.oname].keys() if k.find("_") == 0]:
            kwargs[self.oname][k[1:]] = kwargs[self.oname][k]
            del kwargs[self.oname][k]
        return json.dumps(kwargs)
    def get(self, inst=None, **kwargs):
        """gets data for the requested resource.  if inst is none, gets all instances"""
        return self._req(method="GET", inst=inst)
    def create(self, **kwargs):
        return self._req(method="POST", inst=None, data=self._data(**kwargs))
    def update(self, inst=None, **kwargs):
        return self._req(method="PUT", inst=inst, data=self._data(**kwargs))
    def delete(self, inst=None):
        return self._req(method="DELETE", inst=inst, data=None)
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            self.__dict__[name] = KeystoneClient("/".join([self.url, name]), 
                                                 root=self.root)
        return object.__getattribute__(self, name)

def usage():
    import sys
    return "%s: auth_url resource token action [key=value] [key=value]..." % (sys.argv[0])

def required(*args, **kwargs):
    def d(f):
        def newf(*_args, **_kwargs):
            if len(args) > 0:
                required = args[0]
            else:
                required = kwargs['request']
            bad_kwargs = [ x for x in required if not x in _kwargs.keys() ]
            if len(bad_kwargs) > 0:
                raise TypeError("The following keyword values are missing or malformed: %s" % (bad_kwargs))
            return f(*_args, **_kwargs)
        return newf
    return d

def compare(d1, d2):
    newd1 = dict(d1)
    newd2 = dict(d2)
    for d in (newd1,newd2):
        for k in d.keys():
            if k.find("_") == 0:
                d[k[1:]] = d[k]
                del d[k]
            if k == 'id':
                del d[k]
    return newd1 == newd2

@required(['adminURL', 'region', '_global', 'enabled', 
           'serviceId', 'internalURL', 'publicURL'])
def createEndpointTemplate(ks, **kwargs):
    kwargs['global'] = kwargs['_global']
    del kwargs['_global']
    try:
        ks.services.get(kwargs['serviceId'])
    except HTTPError:
        ks.services.create(_id=kwargs['serviceId'], description=kwargs['serviceId'])
    for et in ks.endpointTemplates.get()['endpointTemplates']['values']:
        if compare(kwargs,et):
            return ks.endpointTemplates.get(et['id'])
    return ks.endpointTemplates.create(**kwargs)
    
def main():
    import sys
    try:
        args = sys.argv[1:]
        url = args.pop(0)
        token = args.pop(0)
        resource = args.pop(0)
        action = args.pop(0)
        kwargs = dict(map(lambda x: tuple(x.split("=",2)), args))
    except:
        print usage()
    #    sys.exit(1)
    ks = KeystoneClient(url, token)
    #r = ks.__getattribute__(resource).__getattribute__(action)(**kwargs)
    et = {u'adminURL': u'http://50.56.12.206:8080/', u'region': u'RegionOne', u'_global': True, u'enabled': True, u'serviceId': u'will', u'internalURL': u'http://50.56.12.206:8080/v1/AUTH_%tenant_id%', u'publicURL': u'http://50.56.12.206:8080/v1/AUTH_%tenant_id%'}
    print createEndpointTemplate(ks, **et)

if __name__=="__main__":
    main()
