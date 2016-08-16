"""
Created on 26 May 2016
@author: Adarsh Suresh Mangalath
"""
import json

prohibited_List = ["Created_Time", "Modified_Time", "Created_By", "Modified_By", "Last_Activity_Time"]


class ZObject(object):
    """Provides object related functionalities for each seperate record.Also provides dict like access for its object."""

    def __init__(self, zclient, jsondata, module,metadata={}, message="", status="", action="",details="",code=""):
        """ZObject constructor which generates a zobject.

        :param zclient: The client for the ZObject. Will be an object ZClient class.
        :param jsondata: The data retreived for that perticular record.
        :param module: Module of the record.
        :param metadata:Metadata of the module
        :param message: Message returned while getting , inserting or updating a record.
        :param status: Status returned while getting , inserting or updating a record.
        :param action: Action returned while upserting a record.

        :type zclient: ZClient
        :type jsondata: dict
        :type module: str
        :type metadata: dict
        :type message: str
        :type status: str
        :type action: str
        """
        self.zclient = zclient
        self.dict = jsondata
        self.module = module
        self.message = message
        self.status = status
        self.action = action
        self.details=details
        self.code=code
        self.metadata = metadata

    def __getitem__(self, key):
        """Getter method to have dict like access for the ZObjects.

        :param key: API field name for a field.
        :type key:str
        :return: The value of a field.
        :rtype: str
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        return self.dict[key]

    def __setitem__(self, key, value):
        """Setter method to have dict like access for the ZObjects.

        :param key: API field name for a field.
        :type key:str
        :param value: The value of a field.
        :type value:str
        :return: None
        """
        self.dict[key] = value

    def __str__(self):
        """To print out an zobject."""

        str="Module: "+ self.module
        str+= "\nMessage: " + self.message
        str += "\nStatus: " + self.status
        str += "\nAction: " + self.action
        str += "\nFields: " + json.dumps(self.dict)
        str+="\nDetails: "+json.dumps(self.details)
        str += "\nCode: " + self.code
        return str

    def _loaddata(self, record=None, mydict=None):
        """To load the returned object to the given object.

        :param record: To load from a record.
        :param mydict: To load from a dictionary.
        :type record: ZObject
        :type mydict: dict
        :returns: None
        """
        if record:
            if record.code == 'SUCCESS':
                self.dict.update(record.dict)
            self.message = record.message
            self.status = record.status
            self.action = record.action
            self.details = record.details
            self.code = record.code
        elif type(mydict) is dict:
            if 'status' in mydict.keys():
                self.status = mydict['status']
            if 'message' in mydict.keys():
                self.message = mydict['message']
            if 'code' in mydict.keys():
                self.code = mydict['code']
            if 'details' in mydict.keys():
                self.details = mydict['details']
            if 'action' in mydict.keys():
                self.action = mydict['action']

    def properties(self):
        """To get the list of all the fields of a record.
        :returns: A list of all the fields.
        :rtype:list
        """
        return self.dict.keys()

    def outputJSON(self):
        """Get all the values from the dict and construct a json for senting to server side.

        :returns: A dictionary which can be passed to insert , update and upsert methods.

        :rtype:dict
        """
        json = {}
        if not self.metadata:
            return self.dict
        else:
            fields = self.metadata['modules'][0]['fields']
            for field in fields:
                field_api_name = field['api_name']
                if field['view_type']['edit'] and field_api_name in self.dict.keys() and self[field_api_name] :
                    try:
                        if field['data_type'] == 'bigint' or field['data_type'] == 'ownerlookup' or field['data_type'] == 'lookup':
                            json[field_api_name]=self.dict[field_api_name]['id']
                        else:
                            json[field_api_name] = self.dict[field_api_name]
                    except:
                        json[field_api_name] = self.dict[field_api_name]
        try:
            json['id']=self.dict['id']
        except:
            pass
        return json

    def update(self):
        """Update the record with the new values.
        :return: None
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        ret = self.zclient.update(self.module, [self.outputJSON()])
        self._loaddata(record=ret[0])
        if self.code == 'SUCCESS':
            return True
        else:
            return False

    def delete(self):
        """Delete the record.

        :returns: True or False depending on the server reply.

        :rtype:bool

        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        ret = self.zclient.delete(self.module, self.dict["id"])
        self._loaddata(mydict=ret)
        if self.code == "SUCCESS":
            return True
        else:
            return False

    def related_list(self, related_module, relation_name):
        """To retreive the related list of the module.

        :param related_module: Related module of the record.
        :param relation_name: Id  provided in the metadata of the module as list_relation_id.

        :type related_module: str
        :type relation_name: int or str

        :returns: A list of ZObjects with the related module.
        :rtype: list
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        return self.zclient.related_list(self.module, self.dict["id"], related_module,relation_name)


    def update_relation(self, related_module, relation_name, related_record_id, datalist):
        """To add a new relation to the module.
            ..note:: Supported Modules : Campaigns -> Leads, Contacts
                                        Products -> Leads, Contacts, Accounts, Potentials, Price Books
                                        or their reverse as in Leads -> Campaings , Products

        :param related_module: The module of related record.
        :param relation_name: Relation name of the module.
        :param related_record_id: Id of the related record.
        :param datalist: Data to be inserted in a list of dicts.

        :type related_module: str
        :type relation_name: str
        :type related_record_id: str
        :type datalist: dict

        :returns: A list of ZObjects with the related records.

        :rtype: list
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        return self.zclient.update_relation(self.module, self.dict["id"], related_module, relation_name,
                                            related_record_id, datalist)

    def delete_relation(self, related_module, relation_name, related_record_id):
        """To delete a relation between two records.

        :param related_module:  The module of related record.
        :param relation_name: List_relation_id of the module.
        :param related_record_id: Id of the related record.

        :type related_module: str
        :type relation_name: str
        :type related_record_id: str

        :return:A dictionary with return message.
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        return self.zclient.delete_relation(self.module, self.dict["id"], related_module, relation_name,
                                            related_record_id)

    def convert_lead(self, data):
        """Converts a lead with the given data.

        :param data:Data to be inserted in a list of dicts.
        :type data: dict
        :return: Converted details.
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        if (self.module == "Leads"):
            return self.zclient.convert_lead(self.dict["id"], data)

    def insert_notes(self,data):
        """To insert notes into the module.

        :param data: Notes data to be inserted.
        :type data: dict
        :return: Note object in the list.
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        return self.zclient.insert_notes(self.module,self['id'],[data])

    def update_notes(self,id,data):
        """To insert notes in the module.

        :param id: Id of the module to be updated
        :param data: Notes data to be updated.
        :type id: str
        :type data: dict
        :returns: A list of updated notes
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        return self.zclient.update_relation(self.module,self['id'],'Notes','Notes',id,[data])

    def upload_file(self,file):
        """ To upload an attachment into the module.

        :param file: Filename of the file to be uploaded (full path or absolute path).
        :type file: str
        :returns: Bool depending whther the action occured or not.
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        ret= self.zclient.upload_file(self.module,self['id'],file)
        self._loaddata(mydict=ret)
        if self.code == 'SUCCESS':
            return True
        return False

    def download_file(self,fileid,filename):
        """To download an attachment from the module.

        :param fileid: Id of the file.
        :param filename: Filename of the file (full path or absolute path).
        :type fileid: str
        :type filename: str
        :returns: Bool depending whther the action occured or not
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        ret = self.zclient.download_file(self.module,self['id'],fileid,filename)
        self._loaddata(mydict=ret)
        return ret

    def upload_photo(self,file):
        """To upload a photo into the module.

        :param file: Filename of the photo (full path or absolute path).
        :type file: str
        :returns: Bool depending whther the action occured or not
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        if self.module == "Leads" or self.module=='Contacts':
            ret=self.zclient.upload_photo(self.module,self['id'],file)
            self._loaddata(mydict=ret)
            if self.code == 'SUCCESS':
                return True
        return False

    def download_photo(self,file=None):
        """To download a photo from the module.

        :param file: Filename of the photo (full path or absolute path).
        :type file: str
        :returns: Bool depending whther the action occured or not
        :raises: Zoho Exceptions: For all invalid requests see http status codes for Zoho CRM APIs for more details.
        """
        ret=False
        if self.module == "Leads" or self.module=='Contacts':
            ret= self.zclient.download_photo(self.module,self['id'],file)
            self._loaddata(mydict=ret)
        return ret



