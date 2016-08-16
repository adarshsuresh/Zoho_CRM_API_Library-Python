"""
Created on 26 May 2016
@author: Adarsh Suresh Mangalath
"""
import os, json,zohoutils

from Zoho_CRM_API_Library.zohoobject import ZObject

_METADATA_FILE = os.path.abspath('')+"/metadata.conf"


def loadmodules(zclient, rfile=True, modules=[]):
    """Loads all module details for easy use of the ZohoCRM APIs.

    :param zclient: Client which makes the call.
    :param rfile: Depending on the value fetches from the server or local file.

    .. note:: True : Tries to fetch from local and if unavailable fetches from the server.
        False: Fetched from the server and updates the local file.

    :param modules: (Optional) List of strings use only if perticular modules is needed to be loaded.

    :type zclient: ZClient Object
    :type rfile: bool
    :type modules: list

    :returns: dict with the metadata.

    :rtype: dict

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    if rfile:
        if os.path.exists(_METADATA_FILE):
            zclient.modules_metadata = zohoutils._load_dictionary(_METADATA_FILE)
        else:
            rfile = False
    if not rfile:
        metadata = {}
        if not modules:
            modlist = zclient.modules()
            for var in modlist:
                if var['api_supported']:
                    modules.append(var['api_name'])
        for module in modules:
            mymetadata = zclient.metadata(module)
            metadata[module] = mymetadata
        zclient.modules_metadata = metadata
        if metadata:
            zohoutils._save_dictionary(metadata,_METADATA_FILE)
    return zclient.metadata


def _getlist(zclient, url_path, params, type, module=None, headers={}):
    """To create a list of zoho objects from get API calls  (Internal USE)

    :param zclient: Client which makes the call.
    :param url_path: URL path for the request.
    :param params: HTTP parameters for the get requests.
    :param type: Key for the JSON array.
    :param module: Module of the zoho object.
    :param headers: HTTP headers for the get request.

    :type zclient: ZClient Object
    :type url_path: str
    :type params: dict
    :type type: str
    :type module: str
    :type headers: dict

    :returns: A list of ZObjects.

    :rtype: list

    :raises: Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    jsondata = zclient._get(url_path, params, headers=headers)
    list = []
    if jsondata is None:
        return []
    if module in zclient.modules_metadata.keys():
        metadata=zclient.modules_metadata[module]
    else:
        metadata={}
    if module:
        for var in jsondata[type]:
            if module:
                list.append(ZObject(zclient, var, module,metadata=metadata))
    else:
        return jsondata[type];
    return list


def _getlist_iu(zclient,retdata,datalist, type, module=None):
    """To create a list of zoho objects from get API calls  (Internal USE)

    :param zclient: Client which makes the call.
    :param url_path: URL path for the request.
    :param params: HTTP parameters for the get requests.
    :param type: Key for the JSON array.
    :param module: Module of the zoho object.
    :param headers: HTTP headers for the get request.

    :type zclient: ZClient Object
    :type url_path: str
    :type params: dict
    :type type: str
    :type module: str
    :type headers: dict

    :returns: A list of ZObjects.

    :rtype: list

    :raises: Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    if retdata is None or not retdata:
        return []
    if module in zclient.modules_metadata.keys():
        metadata = zclient.modules_metadata[module]
    else:
        metadata = {}
    list=[]
    for i in range(0, len(retdata)):
        if retdata[i]["code"] == "SUCCESS" or retdata[i]["code"]=="DUPLICATE_DATA":
            datalist[i]["id"] = retdata[i]["details"]["id"]
            if retdata[i]["code"]!="DUPLICATE_DATA":
                datalist[i]["created_by"] = retdata[i]["details"]["created_by"]
                datalist[i]["modified_by"] = retdata[i]["details"]["modified_by"]
                datalist[i]["modified_time"] = retdata[i]["details"]["modified_time"]
                datalist[i]["created_time"] = retdata[i]["details"]["created_time"]
        list.append(ZObject(zclient, datalist[i], module,metadata=metadata, status=retdata[i]["status"], message=retdata[i]["message"],
                            details=retdata[i]["details"],code=retdata[i]['code']))
    return list

def users(zclient, params={}):
    """To get the users in the organization.

    :param zclient: Client which makes the call.
    :param params: (Optional) Parameters for the user get requests.

    .. note:: type={AllUsers|ActiveUsers|DeactiveUsers|ConfirmedUsers|NotConfirmedUsers|DeletedUsers|ActiveConfirmedUsers|AdminUsers|ActiveConfirmedAdmins|CurrentUser}

    :type zclient: ZClient Object
    :type params: dict

    :returns: A list of json (json array)  with users details.

    :rtype:list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = "users"
    return _getlist(zclient, url_path, params, "users")


def modules(zclient):
    """To get the module related data.

    :param zclient: Client which makes the call.

    :type zclient: ZClient Object

    :returns: A list of json (json array) with module details.

    :rtype:list

    .. note:: The key "api_name" in each module will be used to access the resource.

    :raises: Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = "settings/modules"
    return _getlist(zclient, url_path, {}, "modules")


def metadata(zclient, module):
    """To get the meta data (fields, related list, module, layouts data) for the modules (Contacts,Leads).

    :param zclient: Client which makes the call.
    :param module: The module of the layout to be fetched.

    :type zclient: ZClient Object
    :type module: str

    :returns: A json array with module's metadata.

    :rtype: list

    .. note:: It list all the fields available, related list for that user. For insert and update apis , use " api_name" in the json data.

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = "settings/modules/" + module
    return  zclient._get(url_path, {})


def layouts(zclient, id=None, params={}):
    """To get the layouts associated with the particular module or to get the particular layout details.

    :param zclient: Client which makes the call.
    :param id: (Optional) Id of the layout to be fetched.
    :param params: HTTP parameter for get request.

    .. note:: module={MODULE}

    :type zclient: ZClient Object
    :type id: str
    :type params: dict

    :returns: Returns a list of ZObject with layout details.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = "settings/layouts"
    if id is not None:
        url_path = url_path + "/" + str(id)
    return _getlist(zclient, url_path, params, "layouts")


def get(zclient, module, id=None, headers={}, params={}):
    """To get the records from a module.

    :param zclient: Client which makes the call.
    :param module: The module of the record to be fetched.
    :param id: (Optional) Id of the record to be fetched.
    :param headers: (Optional) HTTP headers for request.

    .. note:: {If-Modified-Since:last modified time}

    :param params: (Optional) HTTP parameters for request.

    .. note:: sort_by, fields (comma separated), sort_order (asc or desc), converted (true or false), approved (true or false), page(1,2..),per_page(200)
        e.g {sort_order: asc}

    :type zclient: ZClient
    :type module: str
    :type id: str
    :type headers: dict
    :type params: dict

    :returns: A list of ZObjects with fetched records.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module
    if id is not None:
        url_path = url_path + "/" + str(id)
        list = _getlist(zclient, url_path, params, "data", module, headers=headers)
        if list:
            return list[0]
        else:
            return None
    return _getlist(zclient, url_path, params, "data", module, headers=headers)


def insert(zclient, module, datalist):
    """To insert a new entity into the module.

    :param zclient: Client which makes the call.
    :param module: The module of the record to be inserted.
    :param datalist: Data to be inserted in a list of dicts.

    .. note:: eg:[{"Last_Name":"Last_Name"},{"Last_Nam":"Last_Name"}]

    :type zclient: ZClient
    :type module: str
    :type datalist: list

    :returns: A list of ZObject with inserted records information.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module
    retdata = zclient._post(url_path, {},payload={"data": datalist})["data"]
    list = _getlist_iu(zclient,retdata,datalist,'data',module=module)
    return list


def update(zclient, module, datalist):
    """To update an existing record in the module.

    :param zclient: Client which makes the call.
    :param module: The module of the record to be updated.
    :param datalist: Data to be inserted in a list of dicts.

    .. note:: eg:[{"id":"410888000000482039","Last_Name":"Last_Name"},{"id":"410888000000482040","Last_Name":"Last_Name"}]

    :type zclient: ZClient
    :type module: str
    :type datalist: list

    :returns: A list of ZObjects with updated records information.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module
    retdata = zclient._put(url_path, {}, payload={"data": datalist})["data"]
    list = _getlist_iu(zclient,retdata,datalist,'data',module=module)
    return list


def delete(zclient, module, id):
    """To delete the particular entity

    :param zclient: Client which makes the call.
    :param module: The module of the record to be deleted.
    :param id: Id of the record to be deleted.

    :type zclient: ZClient
    :type module: str
    :type id: str

    :returns: A dictionary with return message.

    .. note:: eg:{"message": "record deleted","details": {},"status": "success","code": "SUCCESS"}

    :rtype: dict

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module + "/" + id
    return zclient._delete(url_path)


def upsert(zclient, module, datalist):
    """To insert the record if not exists already (checked based on duplicate check). If the records exists , then it'll be updated.

    :param zclient: Client which makes the call.
    :param module: The module of the record to be upsert.
    :param datalist: Data to be inserted in a list of dicts.

    .. note:: eg:[{"id":"410888000000482039","Last_Name":"Last_Name"},{"id":"410888000000482040","Last_Name":"Last_Name","Email":"sriram.rajamanickam@zohocorp.com"}]

    :type zclient: ZClient
    :type module: str
    :type datalist: list

    :returns: A list of ZObject with upserted records information.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module + "/upsert"
    retdata = zclient._post(url_path, {}, {"data": datalist})["data"]
    list = _getlist_iu(zclient,retdata,datalist,'data',module=module)
    return list


def get_deleted(zclient, module, params={}):
    """To get the deleted records.

    :param zclient: Client which makes the call.
    :param module: The module from which deleted records should be fetched.
    :param params: (Optinal) HTTP parameters for the request.

    .. note:: eg: {type: all|recycle|permanent} - recycle bin records or permanently deleted records

    :type zclient: ZClient
    :type module: str
    :type params: dict

    :returns: A list of ZObjects with deleted records.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module + "/deleted"
    return _getlist(zclient, url_path, params, "data", module)


def related_list(zclient, related_module, related_id, module,relation_name):
    """To get the related list records.

    :param zclient: Client which makes the call.
    :param related_module: The module to which other are related.
    :param related_id: Id of the record of related module.
    :param module: The module to which the record is related.
    :param related_list_id: Related list id feteched from the relations in the metadata of the module.

    :type zclient: ZClient
    :type related_module: str
    :type related_id: str
    :type module: str
    :type related_list_id: str

    :returns: A list of ZObjects with related records.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.

    .. note:: related_module: Leads | related_id: 3000000029001 | module: Notes | related_list_id: 3000000013433/
        The function will fetch the Notes which are located under the lead with id 3000000029001 and Note's related list id is 3000000013433

    """
    url_path = related_module + "/" + str(related_id) + "/"+relation_name
    return _getlist(zclient, url_path, {}, "data", module)


def insert_notes(zclient, related_module, related_id, datalist):
    """To insert a note the records.

    :param zclient: Client which makes the call.
    :param related_module: The module to which other are related.
    :param related_id: Id of the record of related module.
    :param datalist: Data to be inserted in a list of dicts.

    :type zclient: ZClient Object
    :type related_module: str
    :type related_id: str
    :type datalist: list

    :returns: A list of ZObjects with related records.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = related_module + "/" + str(related_id) + "/Notes"
    retdata = zclient._post(url_path, {}, payload={"data": datalist})["data"]
    list = _getlist_iu(zclient,retdata,datalist,'data',module='Notes')
    return list

def update_notes(zclient, related_module, related_id, datalist):
    """To insert a note the records.

    :param zclient: Client which makes the call.
    :param related_module: The module to which other are related.
    :param related_id: Id of the record of related module.
    :param datalist: Data to be inserted in a list of dicts.

    :type zclient: ZClient Object
    :type related_module: str
    :type related_id: str
    :type datalist: list

    :returns: A list of ZObjects with related records.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = related_module + "/" + str(related_id) + "/Notes"
    retdata = zclient._put(url_path, {}, payload={"data": datalist})["data"]
    list = _getlist_iu(zclient,retdata,datalist,'data',module='Notes')
    return list


def update_relation(zclient, related_module, related_id, module, relation_name, related_record_id, datalist):
    """To update the relation between the records

    :param zclient: Client which makes the call.
    :param related_module: The module to which other are related.
    :param related_id: Id of the record of related module.
    :param module: The module to which the record is related.
    :param related_list_id: Related list id feteched from the relations in the metadata of the module.
    :param module_id: Id of the record that has to be updated in the module.
    :param datalist: Data to be inserted in a list of dicts.

    :type zclient: ZClient Object
    :type related_module: str
    :type related_id: str
    :type module: str
    :type related_list_id: str
    :type module_id: str
    :type datalist: list

    :returns: A list of ZObject with related records.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.

    .. note:: Supported Modules :
        Campaigns -> Leads, Contacts
        Products -> Leads, Contacts, Accounts, Potentials, Price Books
        or their reverse as in Leads -> Campaings , Products
        Sample Data For Adding Relation Between Leads, Campaigns (Not Mandatory, you can send the request without body)
        datalist:[ {"Status" : "active"}]
        Sample Data For Adding Relation Between Contact, Potentials (Mandatory, you need to send body)
        datalist :[ {"Contact_Role" : "1000000024229"}]
        Sample Data For Adding Relation Between Products, Price_Books (Mandatory, you need to send body)
        datalist :[ {"list_price" : 50.56}]
        Adding Relation Between Other Modules, Need Not To Send The Body
    """
    url_path = related_module + "/" + str(related_id) + "/" + relation_name + "/" + str(related_record_id)
    retdata = zclient._put(url_path, {},payload= {"data": datalist})["data"]
    list = _getlist_iu(zclient,retdata,datalist,'data',module=module)
    return list


def delete_relation(zclient, related_module, related_id, module, relation_name, related_record_id):
    """To delete the association between modules.

    :param zclient: Client which makes the call.
    :param related_module: The module to which other are related.
    :param related_id: Id of the record of related module.
    :param module: The module to which the record is related.
    :param related_list_id: Related list id feteched from the relations in the metadata of the module.
    :param module_id: Id of the record that has to be updated in the module.

    :type zclient: ZClient
    :type related_module: str
    :type related_id: str
    :type module: str
    :type related_list_id: str
    :type module_id: str

    :returns: A dictionary with return message.

    .. note:: eg. {"data": [{"message": "relation removed","details": {},"status": "success","code": "SUCCESS"}]}

    :raises: Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.

    """
    url_path = related_module + "/" + str(related_id) + "/"  + relation_name + "/" + str(related_record_id)
    return zclient._delete(url_path)


def convert_lead(zclient, id, data):
    """To convert a lead to contact/account/potential.

    :param zclient: Client which makes the call.
    :param id: Id of the lead record to be updated.
    :param data: Data to be inserted in a list of dicts.

     .. note:: eg:[{
        "overwrite": true,
        "notify_lead_owner": true,
        "notify_new_entity_owner": true,
        "account": "1000000112248",
        "contact": "1000000112250",
        "assign_to": "1000000028468",
        "potential":
        {
        "Campaign_Source": "1000000112256",
        "Potential_Name": "Potential_Name0",
        "Closing_Date": "2016-02-18",
        "Stage": "Stage0",
        "Amount": 56.6
        }
        }]

    :type zclient: ZClient Object
    :type id: str
    :type data: dict

    :returns: A dictionary with return message.

    .. note:: eg:{"data": [{"potential": "1000000235001","account": "1000000112248","contact": "1000000112250"}]}

    :rtype: dict

    :raises: Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = "Leads" + "/" + str(id) + "/" + "convert"
    return zclient._post(url_path, {},headers={},payload= {"data": data})["data"]


def upload_photo(zclient, module, id, file):
    """To upload a photo (as MULTIPART) to a record in Leads or Contacts.

    :param zclient: Client which makes the call.
    :param module: The module to which the record has to be updated.
    :param id: Id of the record where the photo should be added.
    :param file: Filename of the photo (full path or absolute path).

    :type zclient: ZClient
    :type module: str
    :type id: str
    :type file: str

    :returns: A dictionary with return message.

    .. note:: eg: {"message": "photo uploaded successfully","details": {},"status": "success","code": "SUCCESS"}

    :rtype:dict

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module + "/" + str(id) + "/" + "photo"
    files = {'file': open(file, 'rb')}
    return zclient._post(url_path, {}, files=files)


def download_photo(zclient, module, id, filename=None):
    """To download the photo associated with a Lead/Contact.

    :param zclient: Client which makes the call.
    :param module: The module from which photo to be downloaded.
    :param id: Id of the record from which photo should be downloaded.
    :param filename: (Optional)FileName under which the file should be saved (full path or absolute path).

    :type zclient: ZClient
    :type module: str
    :type id: str
    :type filename: str

    .. note:: e.g /Users/path/stored/filename.jpg or if left empty will be stored as {id}.png.

    :returns: None

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module + "/" + id + "/" + "photo"
    resp = zclient._get(url_path, {}, stream=True)
    if not filename:
        filename = id + '.png'
    with open(filename, 'wb') as f:
        for chunk in resp:
            f.write(chunk)
    if resp.status_code==200:
        return True
    else:
        return False


def upload_file(zclient, module, id, file):
    """To upload a file (as MULTIPART) as attachment.

    :param zclient: Client which makes the call.
    :param module: The module to which the file has to be uploaded .
    :param id: Id of the record where the file should be added.
    :param related_id: Related list id of attachments fetched from the relations in the metadata of the module.
    :param file: Filename of the uploading file (full path or absolute path).

    :type zclient: ZClient
    :type module: str
    :type id: str
    :type related_id: str
    :type file: str

    :return: Returns a dictionary with return message.

    .. note:: eg:{"message": "attachment uploaded successfully","details": {"id":"1000000033547"},"status": "success","code": "SUCCESS"}

    :rtype: dict

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module + "/" + str(id) + "/Attachments"
    files = {'file': open(file, 'rb')}
    return zclient._post(url_path, {}, files=files)


def download_file(zclient, module, id, file_id, file_name):
    """To download a file.

    :param zclient: Client which makes the call.
    :param module: The module from which the file has to be download.
    :param id: Id of the record  from where the file should be downloaded.
    :param related_id: Related list id of attachments feteched from the relations in the metadata of the module.
    :param file_id: Id of the file from related list records of attachments.
    :param file_name: Filename of the file from related list records of attachments.

    :type zclient: ZClient
    :type module: str
    :type id: str
    :type related_id: str
    :type file_id: str
    :type file_name: str

    :returns: None

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module + "/" + str(id) + "/Attachments/"+ str(file_id)
    resp = zclient._get(url_path, {}, stream=True)
    with open(file_name, 'wb') as f:
        for chunk in resp:
            f.write(chunk)
    if resp.status_code == 200:
        return True
    else:
        return False

def search(zclient, module, params={}):
    """To search the records.

    :param zclient: Client which makes the call.
    :param module: The module to which searched.
    :param params: HTTP parameters for the request.

    .. note:: Search By Criteria
        criteria = (({apiname}:{starts_with|equals}:{value}) and ({apiname}:{starts_with|equals}:{value}))...
        Global Search By Email (all the email fields in particular module)
        email = {email}
        Global Search By Phone (similar to email)
        phone = {phone}
        Global Search By Word (searching on all the fields in particular module)
        word = {word}
        ** all the get api supported params are available (fields, converted, approved, page, per_page)**

    :type zclient: ZClient
    :type module: str
    :type params: dict

    :returns: A list of ZObjects with fetched records.

    :rtype: list

    :raises: Zoho Exceptions:For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = module + "/search"
    return _getlist(zclient, url_path, params, "data", module)


def taxes(zclient):
    """ To get all the taxes.

    :param zclient: Client which makes the call.

    :type zclient: ZClient

    :returns: A list of json (json array)  with users details.

    :rtype: list
    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = "taxes"
    return _getlist(zclient, url_path, {}, "taxes")


def roles(zclient):
    """To get all the contact roles.

    :param zclient: Client which makes the call.

    :type zclient: ZClient

    :returns: A list of json (json array)  with users details.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = "Contacts/roles"
    return _getlist(zclient, url_path, {}, "contact_roles")


def tab_groups(zclient):
    """ To get all the tab groups.

    :param zclient: Client which makes the call.

    :type zclient: ZClient

    :returns: A list of json (json array)  with users details.

    :rtype: list

    :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
    """
    url_path = "settings/tab_groups"
    return _getlist(zclient, url_path, {}, "tab_groups")
