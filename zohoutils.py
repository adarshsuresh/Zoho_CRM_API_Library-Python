"""
Created on 26 May 2016
@author: Adarsh Suresh Mangalath
"""
import requests,pickle,json


_DEFAULT_ACCOUNTS_URL = "https://accounts.zoho.com/";
_DEFAULT_OAUTH2_URL = "https://accounts.zoho.com/oauth/v2/"



class ZAccounts(object):
    """Provides Accounts related functionalities for APIs."""
    def __init__(self, client_id, client_secret,redirect_uri,refresh_token=None):
        """ZAccouints constructor which generates a ZAccount to process account related calls.

        :param client_id: Client_id generated for OAUTH 2.
        :param client_secret: Client_secret generated for OAUTH 2.
        :param redirect_uri: Redirect_uri opted in Oauth.
        :param refresh_token: Refresh_token generated in Oauth process.

        :type client_id: str
        :type client_secret: str
        :type redirect_uri: str
        :type refresh_token: str
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token=refresh_token
        self.header = None
        self.body = None

    def _post_account(self,url,params):
        """To post a request for any account related api calls.

        :param url: URL to which the call is to be made.
        :param params: Prameters for the HTTP request.
        :return: Body of the request.
        """
        try:
            resp = requests.post(_DEFAULT_OAUTH2_URL + url, params=params)
        except requests.exceptions.Timeout:
            raise ValueError("Time out error.")
        except Exception as e:
            raise ValueError(e)
        return self._get_header_body(resp)


    def _get_header_body(self,resp):
        """This function gets the response to retrive the header and body to store in the Zaccount.

        :param resp: Response from a HTTP request.
        :returns: Body of the HTTP request
        """
        self.body =_account_exception(resp)
        self.headers = resp.headers
        if 'refresh_token' in self.body.keys():
            self.refresh_token = self.body['refresh_token']
        if 'access_token' in self.body.keys():
            self.access_token = self.body['access_token']
        return self.body

    def _generate_accesstoken(self):
        """ To generate access token using the details (refresh token) the user provided.

        :return: Returns a new access token.
        """
        params = {"refresh_token": self.refresh_token, "client_id": self.client_id, "client_secret": self.client_secret,
                  "redirect_uri": self.redirect_uri, "grant_type": "refresh_token"}

        resp = self._post_account("token", params=params)
        return self.access_token

    def _revoke_refreshtoken(self):
        """ When a refresh token is expired to revoke its access.

        :return: Returns a new access token
        """
        params = {"token": self.refresh_token}
        resp = self._post_account("token", params=params)
        return self.access_token

    def get_access_token(self):
        """ To get the access token from the refresh token
        :returns: A new access token.
        """
        if self.refresh_token is None :
            raise Exception('Either refresh token should be provided.')
        else:
            return self._generate_accesstoken()

class ZohoError(Exception):
    """Base Zoho API exception"""

    message = u'Error occurred for {url}. Error Code: {code} Response content: {content}'

    def __init__(self, url, status, content):
        self.url = url
        self.status = status
        self.content = content

    def __str__(self):
        return self.message.format(url=self.url, code=self.status, content=self.content)

    def __unicode__(self):
        return self.__str__()

# def _error_message(value):
#     """ Error message generator
#
#     :param value:
#     :return:
#     """
#
#     if "WEB_LOGIN_REQUIRED" == value:
#         return "Please use application specific password instead of your password."
#     elif "EXCEEDED_MAXIMUM_ALLOWED_AUTHTOKENS" == value:
#         return "Exceeded maximum allowed authtokens"
#     elif "null" == value:
#         return "Incorrect Email or Password."
#     elif "ACCOUNT_REGISTRATION_NOT_CONFIRMED" == value:
#         return "Email address has not been confirmed. Please confirm your email address to login to the application."
#     elif "REMOTE_SERVER_ERROR" == value:
#         return "Unable to log in. Please Contact your CRM administrator for further assistance."
#     elif "USER_NOT_ACTIVE" == value:
#         return "You are InActive. Please Contact your CRM administrator for further assistance."
#     elif "API_REQUEST_BLOCKED" == value:
#         return "Your request have been blocked. Please Contact your CRM administrator for further assistance."
#     elif "INVALID_PASSWORD" == value:
#         return "Incorrect Password"

def _exception_handler(result):
    """Exception router. Determines which error to raise for bad results

    :param result: Result returned from the HTTP request
    :returns: None
    :raises Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    if result.status_code == 200:
        return
    elif result.status_code == 400:
        raise ZohoError(result.url, result.status_code, "BAD REQUEST    Details:"+result.text)
    elif result.status_code == 401:
        raise ZohoError(result.url, result.status_code, "AUTHORIZATION ERROR    Details:"+result.text)
    elif result.status_code == 403:
        raise ZohoError(result.url, result.status_code, "FORBIDDEN  Details:"+result.text)
    elif result.status_code == 404:
        raise ZohoError(result.url, result.status_code, "NOT FOUND  Details:"+result.text)
    elif result.status_code == 405:
        raise ZohoError(result.url, result.status_code, "METHOD NOT ALLOWED Details:"+result.text)
    elif result.status_code == 413:
        raise ZohoError(result.url, result.status_code, "REQUEST ENTITY TOO LARGE   Details:"+result.text)
    elif result.status_code == 415:
        raise ZohoError(result.url, result.status_code, "UNSUPPORTED MEDIA TYPE Details:"+result.text)
    elif result.status_code == 429:
        raise ZohoError(result.url, result.status_code, "TOO MANY REQUEST   Details:"+result.text)
    elif result.status_code == 500:
        raise ZohoError(result.url, result.status_code, "INTERNAL SERVER ERROR  Details:"+result.text)
    elif result.status_code > 400:
        raise ZohoError(result.url, result.status_code, "UNEXPECTED ERROR   Details:"+result.text)

def _account_exception(result):
    """To check if the any account related queries landed in an error.

    :param result: Result returned from the HTTP request
    :return:
    :raises Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    if result.status_code is not 200:
        raise ZohoError(url=result.url, code=result.status, content=result.text)
    ret = json.loads(result.text)
    if 'error' in ret:
        raise ZohoError(url=result.url, code=result.status, content=result.text)
    return ret

def _save_dictionary(dictionary, File):
    """ Saves the confile as a dictionary.

    :param dictionary: Dict to be saved to the file
    :param File: Name of the file to be saved.
    :returns: None
    """
    with open(File, "wb") as myFile:
        pickle.dump(dictionary, myFile)
        myFile.close()

def _load_dictionary(File):
    """Loads the conf file from metadata.conf

    :param File: Name of the file that should be loaded .
    :returns: A dictionary with all the metadata.

    """
    with open(File, "rb") as myFile:
        dict = pickle.load(myFile)
        myFile.close()
        return dict
