from urllib2 import Request, urlopen, HTTPError
import json


class KeystoneClient(object):
    '''A simple, stupid keystone client.'''
    def __init__(self, admin_url="http://localhost:5001/v2.0", token=None,
                 service_url=None, oname=None, root=None,
                 user=None, password=None):
        self.admin_url = admin_url
        self.service_url = service_url
        self.user = user
        self.password = password
        self.root = root or self
        self.version = "unknown"
        if token:
            self.root.token = token
        elif self == self.root:
            self.authenticate()
        # We'll use oname if provided or resource minus 's' (tenant / tenants)
        self.oname = oname or admin_url.rsplit("/")[-1][0:-1]

    def _req(self, method="GET", data=None, xheaders=[], inst=None):
        # make a keystone request
        url = self.admin_url
        if inst:
            url += "/%s" % (inst)
        req = Request(url=url)
        req.data = data
        req.get_method = lambda: method
        req.add_header("X-Auth-Token", self.root.token)
        req.add_header("Content-type", "application/json")
        req.add_header("Accept", "application/json")
        r = urlopen(req).read()
        if r == "":
            return {str(self.oname): None}
        else:
            return json.loads(r)

    def authenticate(self):
        """Authenticate against service api"""
        req = Request(url="%s/tokens" % self.root.service_url)
        req.add_header("Content-Type", "application/json")
        try:
            try:
                req.data = json.dumps({"passwordCredentials": {
                            "username": self.root.user,
                            "password": self.root.password}})
                r = json.loads(urlopen(req).read())
                print "{'auth': %s}" % req.data
                self.root.version = "2.0a"
            except HTTPError:
                req.data = '{"auth": %s}' % req.data
                r = json.loads(urlopen(req).read())
                self.root.version = "2.0b"
            self.root.token = r['auth']['token']['id']
        except KeyError:
            raise ValueError("Failed to authenticate to keystone: %s" % r)

    def _data(self, **kwargs):
        # structure data, munge _ variables in kwargs to remove _
        if not self.oname in args:
            kwargs = {str(self.oname): kwargs}
        for k in [k for k in kwargs[self.oname].keys() if k.find("_") == 0]:
            kwargs[self.oname][k[1:]] = kwargs[self.oname][k]
            del kwargs[self.oname][k]
        return json.dumps(kwargs)

    def get(self, inst=None, **kwargs):
        """gets data for the requested resource"""
        return self._req(method="GET", inst=inst)

    def create(self, **kwargs):
        """create a new resource"""
        return self._req(method="POST", inst=None, data=self._data(**kwargs))

    def update(self, inst=None, **kwargs):
        """update an existing resource"""
        return self._req(method="PUT", inst=inst, data=self._data(**kwargs))

    def delete(self, inst=None):
        """delete an existing resource"""
        return self._req(method="DELETE", inst=inst, data=None)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            self.__dict__[name] = KeystoneClient("/".join([self.admin_url,
                                                           name]),
                                                 root=self.root)
        return object.__getattribute__(self, name)
