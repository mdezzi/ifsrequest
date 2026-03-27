import requests, logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class IfsRequest:
    def __init__(self, base_url, auth):
        self.base_url = base_url

        auth_type = auth.get('type')
        self.auth_type = auth_type.lower()
        
        if not auth_type:
            raise ValueError('Did not receive auth type.')
        
        if auth_type.lower() == 'client':
            logger.debug('Creating CLIENT auth object')
            client_secret = auth.get('client_secret')
            client_id = auth.get('client_id')
            realm = auth.get('realm')
            if not (client_secret and client_id):
                raise ValueError('Unable to create IFS Auth. Missing client_id or client_secret')
            self.client_id = client_id
            self.client_secret = client_secret
            self.realm = realm
            self.token = self._get_ifs_token()
        elif auth_type.lower() == 'user':
            username = auth.get('username')
            password = auth.get('password')
            if not (username and password):
                raise ValueError('Unable to create IFS Auth. Missing username or password')
            self.username = username
            self.password = password
        else:
            raise ValueError(f'Unable to create IFS Auth with auth type [{auth_type.lower()}]')

    def _get_ifs_token(self):
        token_data={"grant_type": "client_credentials",
                    "client_id":self.client_id,
                    "client_secret":self.client_secret}
        token_url = urljoin(self.base_url,f'/auth/realms/{self.realm}/protocol/openid-connect/token')
        logger.debug('Requesting token from IFS')
        r = requests.post(token_url, data=token_data)
        if r.status_code == 200:
            token = r.json().get('access_token')
            logger.debug('Token received')
        else:
            logger.error(f'Did not receive token from IFS. URL: {token_url} Data: {token_data}')
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
        if self.auth_type == 'client':
            attempts = 0
            while attempts < 3:
                headers = kwargs.get('headers',{}) | {'Authorization':f'Bearer {self.token}'}
                r = requests.get(url, headers=headers)
                if r.status_code == 401:
                    logger.warning(f'Received 401 from IFS. Attempting to retreive new token.')
                    self.token = self._get_ifs_token()
                    attempts += 1
                else:
                    return r
            else:
                logger.warning('Reached maximum retries')
                return r
        elif self.auth_type == 'user':
            headers = kwargs.get('headers',{})
            return requests.get(url, headers=headers, auth=(self.username, self.password))

    def post(self, url, **kwargs):
        url = self._handle_url(url)
        if self.auth_type == 'client':
            attempts = 0
            while attempts < 3:
                headers = kwargs.get('headers',{}) | {'Authorization':f'Bearer {self.token}'}
                json = kwargs.get('json',{})
                r = requests.post(url, json=json, headers=headers) if json else requests.post(url, headers=headers)
                if r.status_code == 401:
                    logger.warning(f'Received 401 from IFS. Attempting to retreive new token.')
                    self.token = self._get_ifs_token()
                    attempts += 1
                else:
                    return r
            else:
                logger.warning('Reached maximum retries')
                return r
        elif self.auth_type == 'user':
            headers = kwargs.get('headers',{})
            json = kwargs.get('json',{})
            r = requests.post(url, json=json, headers=headers, auth=(self.username, self.password)) if json else requests.post(url, headers=headers, auth=(self.username, self.password))
            return r
    
    def patch(self, url, **kwargs):
        url = self._handle_url(url)
        if self.auth_type == 'client':
            attempts = 0
            while attempts < 3:
                headers = kwargs.get('headers',{}) | {'Authorization':f'Bearer {self.token}'}
                json = kwargs.get('json',{})
                r = requests.patch(url, json=json, headers=headers) if json else requests.patch(url, headers=headers)
                if r.status_code == 401:
                    logger.warning(f'Received 401 from IFS. Attempting to retreive new token.')
                    self.token = self._get_ifs_token()
                    attempts += 1
                else:
                    return r
            else:
                logger.warning('Reached maximum retries')
                return r
        elif self.auth_type == 'user':
            headers = kwargs.get('headers',{})
            json = kwargs.get('json',{})
            r = requests.patch(url, json=json, headers=headers, auth=(self.username, self.password)) if json else requests.patch(url, headers=headers, auth=(self.username, self.password))
            return r

    def delete(self, url, **kwargs):
        url = self._handle_url(url)
        if self.auth_type == 'client':
            attempts = 0
            while attempts < 3:
                headers = kwargs.get('headers',{}) | {'Authorization':f'Bearer {self.token}'}
                json = kwargs.get('json',{})
                r = requests.delete(url, json=json, headers=headers) if json else requests.delete(url, headers=headers)
                if r.status_code == 401:
                    logger.warning(f'Received 401 from IFS. Attempting to retreive new token.')
                    self.token = self._get_ifs_token()
                    attempts += 1
                else:
                    return r
            else:
                logger.warning('Reached maximum retries')
                return r
        elif self.auth_type == 'user':
            headers = kwargs.get('headers',{})
            json = kwargs.get('json',{})
            r = requests.delete(url, json=json, headers=headers, auth=(self.username, self.password)) if json else requests.delete(url, headers=headers, auth=(self.username, self.password))
            return r
