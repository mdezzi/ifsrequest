import requests
from urllib.parse import urljoin

class IfsRequest:
    def __init__(self, base_url, client_id, client_secret, namespace):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.namespace = namespace
        self.token = self._get_ifs_token()

    def _get_ifs_token(self):
        token_data={"grant_type": "client_credentials",
                    "client_id":self.client_id,
                    "client_secret":self.client_secret}
        token_url = urljoin(self.base_url,f'/auth/realms/{self.namespace}/protocol/openid-connect/token')
        r = requests.post(token_url, data=token_data)
        if r.status_code == 200:
            token = r.json().get('access_token')
        else:
            raise ValueError('Unable to retrieve IFS token. Please check credentials.')
        return token
    
    def _check_ifs_token(self):
        api_url = urljoin(self.base_url, "/main/ifsapplications/projection/v1/UserSettings.svc/SingletonUser")
        r = requests.get(api_url)
        if r.status_code == 200:
            return True
        else:
            return False
    
    def _handle_url(self, url):
        if self.base_url not in url:
            # checking if it is projection only
            if f'main/ifsapplications/projection/v1' not in url:
                url = urljoin(f'{self.base_url}/main/ifsapplications/projection/v1/',url)
            else:
                url = urljoin(self.base_url, url) 
        return url

    def get(self, url, **kwargs):
        url = self._handle_url(url)
        attempts = 0
        while attempts < 3:
            headers = kwargs.get('headers',{}) | {'Authorization':f'Bearer {self.token}'}
            r = requests.get(url, headers=headers)
            if r.status_code == 401:
                self.token = self._get_ifs_token()
                attempts += 1
            else:
                return r
        else:
            return r

    def post(self, url, **kwargs):
        url = self._handle_url(url)
        attempts = 0
        while attempts < 3:
            headers = kwargs.get('headers',{}) | {'Authorization':f'Bearer {self.token}'}
            json = kwargs.get('json',{})
            r = requests.post(url, json=json, headers=headers) if json else requests.get(url, headers=headers)
            if r.status_code == 401:
                self.token = self._get_ifs_token()
                attempts += 1
            else:
                return r
        else:
            return r
    
    def patch(self, url, **kwargs):
        url = self._handle_url(url)
        attempts = 0
        while attempts < 3:
            headers = kwargs.get('headers',{}) | {'Authorization':f'Bearer {self.token}'}
            json = kwargs.get('json',{})
            r = requests.patch(url, json=json, headers=headers) if json else requests.get(url, headers=headers)
            if r.status_code == 401:
                self.token = self._get_ifs_token()
                attempts += 1
            else:
                return r
        else:
            return r

    def delete(self, url, **kwargs):
        url = self._handle_url(url)
        attempts = 0
        while attempts < 3:
            headers = kwargs.get('headers',{}) | {'Authorization':f'Bearer {self.token}'}
            json = kwargs.get('json',{})
            r = requests.delete(url, json=json, headers=headers) if json else requests.get(url, headers=headers)
            if r.status_code == 401:
                self.token = self._get_ifs_token()
                attempts += 1
            else:
                return r
        else:
            return r

