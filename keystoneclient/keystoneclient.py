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
    def __init__(self, url, token, oname=None):
        '''Create a KeystoneClient:
Arguments:
url - the public url to a keystone resource, eg http://keystone.domain.com:5001/v2.0
token - a valid token for keystone use
oname - the singular name of the resource you are pointed to (usually can be omitted)
'''
        self.url = url
        self.token = token
        self.oname = oname
        if not self.oname:
            #we'll guess that the object name is the url minus an 's'
            self.oname = url.rsplit("/")[-1][0:-1]
    def _req(self, method="GET", data=None, xheaders=[], inst=None):
        # make a keystone request
        url = self.url
        if inst:
            url += "/%s" % (inst)
        req = Request(url=url)
        req.get_method = lambda: method
        req.add_header("X-Auth-Token", self.token)
        req.add_header("Content-type","application/json")
        req.add_header("Accept","application/json")
        if isinstance(data, str):
            req.data = data
        elif data:
            req.data = json.dumps(data)
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
        return kwargs
    def get(self, inst=None, **kwargs):
        """gets data for the requested resource.  if inst is none, gets all instances"""
        return self._req(method="GET", inst=inst)
    def create(self, **kwargs):
        return self._req(method="POST", inst=None, data=self._data(**kwargs))
    def update(self, inst=None, **kwargs):
        return self._req(method="PUT", inst=inst, data=self._data(**kwargs))
    def delete(self, inst=None):
        return self._req(method="DELETE", inst=inst, data=None)
    def __getattr__(self, name):
        self.__dict__[name] = KeystoneClient("/".join([self.url, name]), self.token)
        return self.__dict__[name]
