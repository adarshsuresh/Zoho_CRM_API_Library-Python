"""
Created on 26 May 2016
@author: Adarsh Suresh Mangalath
"""
import requests
import json
import zohoutils
from zohoapimethods import modules
from zohoapimethods import layouts
from zohoapimethods import metadata
from zohoapimethods import users
from zohoapimethods import get
from zohoapimethods import insert
from zohoapimethods import update
from zohoapimethods import delete
from zohoapimethods import upsert
from zohoapimethods import get_deleted
from zohoapimethods import related_list
from zohoapimethods import insert_notes
from zohoapimethods import update_relation
from zohoapimethods import delete_relation
from zohoapimethods import upload_photo
from zohoapimethods import download_photo
from zohoapimethods import upload_file
from zohoapimethods import download_file
from zohoapimethods import search
from zohoapimethods import taxes
from zohoapimethods import roles
from zohoapimethods import tab_groups
from zohoapimethods import convert_lead
from zohoapimethods import loadmodules

_DEFAULT_ZOHO_URL = "https://crm.localzoho.com/crm/v2/"


class ZClient(object):
    """ Performs requests to the Zoho CRM Rest API services."""
    loadmodules = loadmodules
    users = users
    modules = modules
    metadata = metadata
    layouts = layouts
    get = get
    insert = insert
    update = update
    delete = delete
    upsert = upsert
    get_deleted = get_deleted
    convert_lead = convert_lead
    related_list = related_list
    insert_notes = insert_notes
    update_relation = update_relation
    delete_relation = delete_relation
    upload_photo = upload_photo
    download_photo = download_photo
    upload_file = upload_file
    download_file = download_file
    search = search
    taxes = taxes
    roles = roles
    tab_groups = tab_groups

    def __init__(self, client_id, client_secret, redirect_uri, access_token=None, refresh_token=None):
        """ZClient constructor. Should either provide authtoken or client_id/client_password. Genereates authtoken if not provided.

        :param client_id: Client_id generated for OAUTH 2.
        :param client_secret: Client_secret generated for OAUTH 2.
        :param redirect_uri: Redirect_uri opted in Oauth.
        :param access_token: Authtoken to make autherize API call.
        :param refresh_token: Refresh_token generated in Oauth process.

        :type client_id: str
        :type client_secret: str
        :type redirect_uri: str
        :type access_token: str
        :type refresh_token: str

        """
        self.account = zohoutils.ZAccounts(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri,
                                           refresh_token=refresh_token)
        if access_token is None:
            self.access_token = self.account.get_access_token()
        else:
            self.access_token = access_token
        self.headers = None
        self.body = None
        self.X_RATELIMIT_DAY_LIMIT = None
        self.X_RATELIMIT_DAY_REMAINING = None
        self.X_RATELIMIT_LIMIT = None
        self.X_RATELIMIT_REMAINING = None
        self.X_RATELIMIT_RESET = None
        self.X_ACCESSTOKEN_RESET = None
        self.modules_metadata = None


    def _get(self, url, params, headers={}, stream=False, base_url=_DEFAULT_ZOHO_URL,retry=1):
        """GET request formater for the ZClient. (Internal USE)

        :param url: URL for the get request.
        :param params: HTTP parameters for the request.
        :param headers: HTTP headers for the request.
        :param stream: Data stream to download and upload files.
        :param base_url: Default API url for Zoho CRM.
        :param retry: Whether the call must be retried.

        :type url: str
        :type params: dict
        :type headers: dict
        :type stream: bool
        :type base_url: str
        :type retry: bool

        :returns: JSON returned from the api call.
        :rtype: dict
        :raises Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        headers = self._autherize_url(headers)
        try:
            resp = requests.get(base_url + url, params=params, headers=headers, stream=stream)
        except requests.exceptions.Timeout:
            raise ValueError("Time out error.")
        except Exception as e:
            raise ValueError(e)
        if stream and resp.status_code == 200:
            return resp
        try:
            result = self._get_header_body(resp)
        except Exception as e:
            if e.status == 401 and retry==1:
                self.access_token = self.account.get_access_token()
                result=self._get( url, params, headers=headers, stream=stream, base_url=base_url,retry=0)
            else:
                result=self._get_header_body(resp)
        return result

    def _post(self, url, params, headers={}, payload={}, files={}, base_url=_DEFAULT_ZOHO_URL,retry=1):
        """ POST request formater for the ZClient. (Internal USE)

        :param url: URL for the post request.
        :param params: HTTP parameters for the request.
        :param headers: HTTP headers for the request.
        :param payload: JSON data that should be sent with post request.
        :param files: File handler to upload file.
        :param base_url: Default API url for Zoho CRM.
        :param retry: Whether the call must be retried.

        :type url: str
        :type params: dict
        :type headers: dict
        :type payload: dict
        :type base_url: str
        :type files: dict
        :type retry: bool

        :returns: JSON returned from the api call.
        :raises Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        headers = self._autherize_url(headers)
        try:
            if payload:
                resp = requests.post(base_url + url, params=params, data=json.dumps(payload), headers=headers)
            if files:
                resp = requests.post(base_url + url, files=files,headers=headers)
        except requests.exceptions.Timeout:
            raise ValueError("Time out error.")
        except Exception as e:
            raise ValueError("Exception:" + e)
        try:
            result = self._get_header_body(resp)
        except Exception as e:
            if e.status == 401 and retry == 1:
                self.access_token = self.account.get_access_token()
                result = self._post(url, params, headers=headers, payload=payload, files=files, base_url=base_url,retry=0)
            else:
                result = self._get_header_body(resp)
        return result

    def _put(self, url, params, payload, headers={}, base_url=_DEFAULT_ZOHO_URL,retry=1):
        """PUT request formater for the ZClient. (Internal USE)

        :param url: URL for the put request.
        :param params: HTTP parameters for the request.
        :param headers: HTTP headers for the request.
        :param payload: JSON data that should be sent with put request.
        :param base_url: Default API url for Zoho CRM.
        :param retry: Whether the call must be retried.

        :type url: str
        :type params: dict
        :type headers: dict
        :type payload: dict
        :type base_url: str
        :type retry: bool

        :returns: JSON returned from the api call.
        :raises Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        self._autherize_url(headers)
        try:
            resp = requests.put(base_url + url, params=params, data=json.dumps(payload), headers=headers)
        except requests.exceptions.Timeout:
            raise ValueError("Time out error.")
        except Exception as e:
            raise ValueError("Exception:" + e)
        try:
            result = self._get_header_body(resp)
        except Exception as e:
            if e.status == 401 and retry == 1:
                self.access_token = self.account.get_access_token()
                result = self._put(url, params, headers=headers, payload=payload, base_url=base_url,
                                    retry=0)
            else:
                result = self._get_header_body(resp)
        return result

    def _delete(self, url, headers={}, base_url=_DEFAULT_ZOHO_URL,retry=1):
        """DELETE request formater for the Zclient.

        :param url: URL for the delete request.
        :param headers: HTTP headers for the request.
        :param base_url: Default API url for Zoho CRM.
        :param retry: Whether the call must be retried.

        :type url: str
        :type headers: dict
        :type base_url: str
        :type retry: bool
        :returns: JSON returned from the api call.
        :raises Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        headers = self._autherize_url(headers)
        try:
            resp = requests.delete(base_url + url, headers=headers)
        except requests.exceptions.Timeout:
            raise ValueError("Time out error.")
        except Exception as e:
            raise ValueError("Exception:" + e)
        try:
            result = self._get_header_body(resp)
        except Exception as e:
            if e.status == 401 and retry == 1:
                self.access_token = self.account.get_access_token()
                result = self._delete(url, headers=headers, base_url=base_url,
                                    retry=0)
            else:
                result = self._get_header_body(resp)
        return result

    def _autherize_url(self, headers):
        """To add the authtoken to the header of the request.

        :param headers: Header of the request
        :type headers: dict

        :returns: None

        :raise Value Error if authtoken is not provided.
        """

        if self.access_token:
            if headers is None:
                headers={}
            headers['Authorization'] = 'Zoho-authtoken ' + self.access_token
            return headers
        raise ValueError("Must provide API key for this API.")

    def _get_header_body(self, resp):
        """This function gets the response to retrive the header and body to store in the zclient.

        :param resp: Returned response from an api call.
        :type resp: request.response
        :returns: JSON body of the response.
        """
        zohoutils._exception_handler(resp)
        if resp.status_code == 204 or resp.status_code == 301 or resp.status_code == 302 or resp.status_code == 304:
            return None
        self.headers = resp.headers
        self.body = json.loads(resp.text)
        for var in self.headers.keys():
            if var == "X-RATELIMIT-DAY-LIMIT":
                self.X_RATELIMIT_DAY_LIMIT = self.headers["X-RATELIMIT-DAY-LIMIT"]
            elif var == "X-RATELIMIT-DAY-REMAINING":
                self.X_RATELIMIT_DAY_REMAINING = self.headers["X-RATELIMIT-DAY-REMAINING"]
            elif var == "X-RATELIMIT-LIMIT":
                self.X_RATELIMIT_LIMIT = self.headers["X-RATELIMIT-LIMIT"]
            elif var == "X-RATELIMIT-REMAINING":
                self.X_RATELIMIT_REMAINING = self.headers["X-RATELIMIT-REMAINING"]
            elif var == "X-RATELIMIT-RESET":
                self.X_RATELIMIT_RESET = self.headers["X-RATELIMIT-RESET"]
            elif var == "X-ACCESSTOKEN-RESET":
                self.X_ACCESSTOKEN_RESET = self.headers["X-ACCESSTOKEN-RESET"]
        return self.body

    # def _get_related_list_id(self, related_module, module):
    #     metadata = self.modules_metadata[related_module]
    #     relations=metadata["modules"][0]['relations']
    #     for relmodule in relations:
    #         if relmodule["module"] == module:
    #             return relmodule["list_relation_id"]
    #     return None
# ZClient.loadmodules = loadmodules
# ZClient.users = users
# ZClient.modules = modules
# ZClient.metadata = metadata
# ZClient.layouts = layouts
# ZClient.get = get
# ZClient.insert = insert
# ZClient.update = update
# ZClient.delete = delete
# ZClient.upsert = upsert
# ZClient.get_deleted = get_deleted
# ZClient.convert_lead = convert_lead
# ZClient.related_list = related_list
# ZClient.insert_relation = insert_relation
# ZClient.update_relation = update_relation
# ZClient.delete_relation = delete_relation
# ZClient.upload_photo = upload_photo
# ZClient.download_photo = download_photo
# ZClient.upload_file = upload_file
# ZClient.download_file = download_file
# ZClient.search = search
# ZClient.taxes = taxes
# ZClient.roles = roles
# ZClient.tab_groups = tab_groups

