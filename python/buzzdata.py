
import urllib, urllib2, json

class API:
    def call(self, url, getparams, postparams):
        
        if getparams:
            url += "/?%s" % urllib.urlencode(getparams)
        post = json.dumps(postparams)
        
        try:
            if postparams:
                req = urllib2.Request(url)
                req.add_header('Content-Type', 'application/json')
                return json.load(urllib2.urlopen(req, post))
            else:
                return json.load(urllib2.urlopen(url))
        except Exception as e:
            return "Error: %s" % str(e)
    
    def get(self, url, params):
        return self.call(url, params, {})
    
    def post(self, url, params):
        return self.call(url, {}, params)

class DataRoom(API):
    def __init__(self, user, dataroom, api = None):
        
        if not isinstance(user, User):
            self.user = User(user, api)
        else:
            self.user = user
        
        self.dataroom = dataroom
        self.api = api
    
    @staticmethod
    def create(user, api, name, public, readme, license, topics):
        room_details = {'name':name,
                        'public':public,
                        'readme':readme,
                        'license':license,
                        'topics':topics}
        params = {'api_key': api, 'dataset':room_details}
        url = "https://buzzdata.com/api/%s/datasets" % str(user)
        room = DataRoom(user, name, api)
        response = room.post(url, params)
        return (response, room)
    
    def details(self):
        params = {}
        if self.api:
            params['api_key'] = self.api
        url = "https://buzzdata.com/api/%s/%s" % (str(self.user), self.dataroom)
        return self.get(url, params)
    
    def list_datafiles(self):
        params = {}
        if self.api:
            params['api_key'] = self.api
        url = "https://buzzdata.com/api/%s/%s/list_datafiles" % (str(self.user), self.dataroom)
        return self.get(url, params)
    
    def create_datafile(self, name):
        if not self.api:
            return "Error: Must specify an api."
        params = {'data_file_name': name, 'api_key': self.api}
        url = "https://buzzdata.com/api/%s/%s/create_datafile" % (str(self.user), self.dataroom)
        return self.post(url, params)
    
    def __str__(self):
        return self.dataroom
    
    def __repr__(self):
        return self.__str__()

class DataFile(DataRoom):
    def __init__(self, user, dataroom, uuid, api = None):
        DataRoom.__init__(self, user, dataroom, api)
        self.uuid = uuid
    
    def history(self):
        params = {}
        if self.api:
            params['api_key'] = self.api
        url = "https://buzzdata.com/api/data_files/%s/history" % self.uuid
        return self.get(url, params)
    
    def download(self, version=None, filename=None):
        params = {}
        if version:
            params['version'] = version
        if self.api:
            params['api_key'] = self.api
        url = "https://buzzdata.com/api/%s/%s/%s/download_request" % (self.user, self.dataroom, self.uuid)
        location = self.post(url, params)['download_request']['url']
        u = urllib2.urlopen(location)
        if not filename:
            if not version:
                version = 'head'
            filename = "%s.%s.%s" % (self.dataroom, self.uuid, str(version))
        f = open(filename, 'w')
        f.write(u.read())
        f.close()

class User(API):
    def __init__(self, user, api = None):
        self.user = user
        self.api = api
    
    def details(self):
        params = {}
        if self.api:
            params['api_key'] = self.api
        url = "https://buzzdata.com/api/%s" % self.user
        return self.get(url, params)
    
    def list_datarooms(self):
        params = {}
        if self.api:
            params['api_key'] = self.api
        url = "https://buzzdata.com/api/%s/datasets/list" % self.user
        return self.get(url, params)
    
    def __str__(self):
        return self.user
    
    def __repr__(self):
        return self.__str__()

def buzz_search(query, api = None):
    params = {'query':query}
    if api:
        params['api_key'] = api
    return API().get('https://buzzdata.com/api/search', params)
