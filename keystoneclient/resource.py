from urllib2 import Request, urlopen, HTTPError
import json

class KeystoneClient(object):
    def __init__(self, url, token,oname=None):
        self.url = url
        self.token = token
        self.oname = oname
        if not self.oname:
            self.oname = url.rsplit("/")[-1][0:-1]
    def _req(self, method="GET", data=None, xheaders=[], inst=None):
        url = self.url
        if inst:
            url += "/%d" % (inst)
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
        if not kwargs.has_key(self.oname):
            kwargs = { str(self.oname): kwargs }
        return kwargs
    def get(self, inst=None, **kwargs):
        return self._req(method="GET", inst=inst)
    def create(self, **kwargs):
        return self._req(method="POST", inst=None, data=self._data(**kwargs))
    def update(self, inst=None, **kwargs):
        return self._req(method="PUT", inst=inst, data=self._data(**kwargs))
    def delete(self, inst=None, **kwargs):
        return self._req(method="DELETE", inst=inst, data=None)
    def __getattr__(self, name):
        self.__dict__[name] = KeystoneClient("/".join([self.url, name]), self.token)
        return self.__dict__[name]

