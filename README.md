Requests wrapper for making IFS Cloud requests. 
-
To install latest commit directly from Github:

    pip install git+https://github.com/mdezzi/ifsrequest.git

To install specific realease from Github:

    pip install git+https://github.com/mdezzi/ifsrequest.git@0.3

To instantiate the class with client auth:

    from ifsrequest import IfsRequest
    
    auth = {'type':'client', 'client_id':'IFS_test', 'client_secret':'verysecretkey', 'realm':'mrdprod'}
    ifsrequest = IfsRequest(base_url='https://myifsserver.com', auth=auth)

To instantiate the class with user/pass auth:

    from ifsrequest import IfsRequest
    
    auth = {'type':'user','username':'matt','password':'verysecretpass'}
    ifsrequest = IfsRequest(base_url='https://myifsserver.com', auth=auth)

Once instantiated, you can call ifsrequest as if you were calling requests with get, post, patch, and delete methods:

    r = ifsrequest.get('UserSettings.svc/SingletonUser')
    print(r.text)

URL's can be in the following formats:
-

- Full server URL (i.e. https://myifsserver.com/main/ifsapplications/projection/v1/UserSettings.svc/SingletonUser)
- Omit base URL (i.e. main/ifsapplications/projection/v1/UserSettings.svc/SingletonUser)
- Projection Only (i.e. UserSettings.svc/SingletonUser)
