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
    return "%s: auth_url resource token action [inst] [key=value]..." % (sys.argv[0])

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
        sys.exit(1)
    ks = KeystoneClient(url, token)
    r = ks.__getattribute__(resource).__getattribute__(action)(**kwargs)
    print r

if __name__=="__main__":
    main()
