import logging
import time
from urllib.parse import urljoin, urlparse
import requests
from typing import Any, Dict, Optional
from requests import Response, Session

logger = logging.getLogger(__name__)

class IfsRequestError(RuntimeError):
    """Exception raised for HTTP errors returned by IFS.

    Attributes
    ----------
    status : int
        HTTP status code returned by the server.
    body : str
        Textual response body (or a short excerpt) for debugging.
    """

    def __init__(self, status: int, body: str) -> None:
        super().__init__(f'IFS request failed [{status}]: {body}')
        self.status = status
        self.body = body

class IfsRequest:
    """Client for the IFS REST API supporting client‑credential and basic auth.

    Parameters
    ----------
    base_url : str
        Base URL of the IFS service (e.g. ``https://ifs.example.com``).
    auth : dict
        Authentication configuration. Must contain a ``type`` key with value
        ``"client"`` or ``"user"`` and the corresponding credentials.
    """

    def __init__(self, base_url: str, auth: Dict[str, Any]) -> None:
        if not base_url:
            raise ValueError('base_url must be a non‑empty string')
        parsed = urlparse(base_url)
        if not parsed.scheme:
            raise ValueError('base_url must include a URL scheme (e.g. https://)')
        # Normalise base_url – remove trailing slash for consistent joins
        self.base_url = base_url.rstrip('/')

        # Initialise a session for connection reuse
        self.session: Session = requests.Session()

        auth_type = auth.get('type')
        if not auth_type:
            raise ValueError('Did not receive auth type.')
        self.auth_type = auth_type.lower()

        auth_type = auth.get('type')
        if not auth_type:
            raise ValueError('Did not receive auth type.')
        self.auth_type = auth_type.lower()

        if self.auth_type == 'client':
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
        elif self.auth_type == 'user':
            username = auth.get('username')
            password = auth.get('password')
            if not (username and password):
                raise ValueError('Unable to create IFS Auth. Missing username or password')
            self.username = username
            self.password = password
        else:
            raise ValueError(f'Unable to create IFS Auth with auth type [{self.auth_type}]')

    def _get_ifs_token(self) -> str:
        """Obtain a client‑credentials access token from IFS.

        Returns
        -------
        str
            The ``access_token`` string.
        """
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        token_url = urljoin(self.base_url, f'/auth/realms/{self.realm}/protocol/openid-connect/token')
        logger.debug('Requesting token from IFS: %s', token_url)
        r = self.session.post(token_url, data=token_data)
        if r.status_code != 200:
            logger.error('Token request failed [%s]: %s', r.status_code, r.text)
            raise IfsRequestError(r.status_code, r.text)
        data = r.json()
        # Store expiry if provided (defaults to 1 hour)
        expires_in = int(data.get('expires_in', 3600))
        self.token_expires_at = time.time() + expires_in
        logger.debug('Token received, expires in %s seconds', expires_in)
        return data.get('access_token')

    def _check_ifs_token(self) -> bool:
        """Simple health‑check to verify the current token is valid.

        Returns ``True`` if the endpoint responds with HTTP 200.
        """
        api_url = urljoin(self.base_url, "/main/ifsapplications/projection/v1/UserSettings.svc/SingletonUser")
        r = self.session.get(api_url)
        return r.status_code == 200

    def _handle_url(self, url: str) -> str:
        """Return a fully qualified URL.

        If ``url`` is already absolute and contains ``self.base_url`` it is returned
        unchanged. Otherwise it is joined with the appropriate base path.
        """
        if not url:
            raise ValueError('url must be a non‑empty string')
        if self.base_url not in url:
            # Assume a projection‑only relative path if the projection segment is missing
            if 'main/ifsapplications/projection/v1' not in url:
                url = urljoin(f'{self.base_url}/main/ifsapplications/projection/v1/', url)
            else:
                url = urljoin(self.base_url, url)
        return url

    def _ensure_token(self) -> None:
        """Refresh the client token if it is close to expiration.

        The token is refreshed one minute before expiry to avoid race conditions.
        """
        # ``self.token_expires_at`` is set when the token is first obtained.
        if getattr(self, 'token_expires_at', 0) - time.time() < 60:
            logger.debug('Token nearing expiry, refreshing')
            self.token = self._get_ifs_token()

    def _request(self, method: str, url: str, **kwargs: Any) -> Response:
        """Centralised request handling with retry on 401 for client auth.

        Parameters
        ----------
        method : str
            HTTP method name (e.g. ``'GET'``, ``'POST'``).
        url : str
            Endpoint URL (relative or absolute).
        **kwargs : Any
            Passed through to :func:`requests.Session.request`.
        """
        url = self._handle_url(url)
        for attempt in range(3):
            headers = dict(kwargs.pop('headers', {}))
            auth: Optional[tuple] = None
            if self.auth_type == 'client':
                self._ensure_token()
                headers['Authorization'] = f'Bearer {self.token}'
            elif self.auth_type == 'user':
                auth = (self.username, self.password)
            else:
                raise RuntimeError('Unsupported auth type')

            logger.debug('%s %s (attempt %d)', method.upper(), url, attempt + 1)
            response = self.session.request(method, url, headers=headers, auth=auth, **kwargs)

            if response.status_code != 401:
                logger.debug('Response %s → %s', method.upper(), response.status_code)
                if not response.ok:
                    raise IfsRequestError(response.status_code, response.text)
                return response

            # 401 – only client auth can be refreshed
            if self.auth_type == 'client':
                logger.warning('Received 401, refreshing token')
                self.token = self._get_ifs_token()
                continue
            break

        logger.warning('Maximum retries reached for %s %s', method.upper(), url)
        raise IfsRequestError(response.status_code, response.text)

    def get(self, url: str, **kwargs: Any) -> Response:
        """Send a GET request.

        See :meth:`_request` for detailed behaviour.
        """
        return self._request('GET', url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        """Send a POST request.

        ``json`` payload (if provided) is passed through unchanged.
        """
        return self._request('POST', url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Response:
        """Send a PATCH request."""
        return self._request('PATCH', url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """Send a DELETE request."""
        return self._request('DELETE', url, **kwargs)