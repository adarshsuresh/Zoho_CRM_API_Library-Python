from unittest import TestCase
from zohoclient import ZClient
import json, os ,time,random

client_id = ''
client_secret = ''
redirect_uri= ''
refresh_token = ''
access_token = ''
global_record_list={}
myclient=None
class TestZClient(TestCase):
    @classmethod
    def setUpClass(self):
        global global_record_list,myclient
        myclient = ZClient(client_id=client_id, client_secret=client_secret,
                           redirect_uri=redirect_uri,access_token=access_token,
                           refresh_token=refresh_token)
        myclient.loadmodules()
        global_record_list = insert_data(myclient)
        pass

    def setUp(self):
        pass

    def test__loadmodules(self):
        """Test ZClient.loadmodules functionality. """
        myclient.loadmodules()

    def test__users(self):
        """Test ZClient.users functionality. """
        myclient.users()

    def test__modules(self):
        """Test ZClient.modules functionality. """
        myclient.modules()

    def test__metadata(self):
        """Test ZClient.metadata functionality. """
        for val in myclient.modules_metadata.keys():
            myclient.metadata(val)


    def test__layouts(self):
        """Test ZClient.layouts functionality. """
        layouts={}
        for val in myclient.modules_metadata.keys():
            layouts[val] = myclient.layouts(params={'module': val})

    def test__get(self):
        """Test ZClient.get functionality by getting records from all possible modules."""
        recorddict={}
        for val in myclient.modules_metadata.keys():
            recorddict[val] = myclient.get(val,params={'sort_order': 'asc'},headers={'If-Modified-Since': '2016-05-18T14:37:50+05:30'})


    def test__insert_update_delete(self):
        """Test insert update and delete functionality of all the modules. """
        recorddict1 = insert_data(myclient)
        recorddict2 = update_data(myclient, recorddict1)
        self.assertTrue(set(recorddict1.items()) & set(recorddict2.items()))
        delete_data(myclient,recorddict2)


    def test__get_deleted(self):
        """Test ZClient.get_deleted functionality of all the modules"""
        for val in myclient.modules_metadata.keys():
            myclient.get_deleted(val,params={'type': 'all'})


    def test__upload_download_photo(self):
        """Test ZClient.upload_photo and ZClient.download_photo functionality for Leads and Contacts."""
        modulelist=['Leads','Contacts']
        for module in modulelist:
            myclient.upload_photo(module,global_record_list[module], os.path.abspath('')+'/zoho-crm.png')
            myclient.download_photo(module, global_record_list[module], os.path.abspath('') + '/zoho-crm-'+module+'.png')
            os.remove(os.path.abspath('') + '/zoho-crm-'+module+'.png')


    def test__upload_download_file(self):
        """Test ZClient.upload_file and ZClient.download_file functionality for all possible modules."""
        modulelist = []
        for module in myclient.modules_metadata.keys():
            relatedmodules=[relation['api_name'] for relation  in myclient.modules_metadata[module]['modules'][0]['relations']]
            if 'Attachments' in relatedmodules:
                modulelist.append(module)
        attachmentrecord={}
        for module in modulelist:
            if module in global_record_list.keys():
                try:
                    result=myclient.upload_file(module, global_record_list[module], os.path.abspath('') + '/TestJSON.txt')
                    if result['code']=='SUCCESS':
                        attachmentrecord[module]=result['details']['id']
                except Exception,e:
                    print module,e
            if  module in attachmentrecord.keys():
                myclient.download_file(module,global_record_list[module], attachmentrecord[module], os.path.abspath('') + '/TestJSON-'+module+'.txt')
                os.remove(os.path.abspath('') + '/TestJSON-'+module+'.txt')


    def test__insert_notes(self):
        """Test ZClient.insert_notes functionality for all possible modules."""
        mynote={
                'Note_Title': 'Test Note',
                'Note_Content': 'Test Note Added'
            }
        modulelist = []
        for module in myclient.modules_metadata.keys():
            relatedmodules=[relation['api_name'] for relation  in myclient.modules_metadata[module]['modules'][0]['relations']]
            if 'Notes' in relatedmodules:
                modulelist.append(module)
        for module in modulelist:
            if module in global_record_list:
                try:
                    value=myclient.insert_notes(module,global_record_list[module],[mynote])
                except Exception, e:
                    print 'Exception Occured inserting notes:', module, e

    def test__related_list(self):
        """Test ZClient.related_list functionality for all possible modules."""
        for module in myclient.modules_metadata.keys():
            relatedmodules = {}
            for relation in myclient.modules_metadata[module]['modules'][0]['relations']:
                if relation['href']!=None:
                    relatedmodules[relation['module']]=relation['api_name']
            for relmodule in relatedmodules.keys():
                try:
                    if module in global_record_list.keys():
                        mylist=myclient.related_list(module,global_record_list[module],relmodule,relatedmodules[relmodule])
                except Exception,e:
                    print 'Exception Occured:',module, relmodule, relatedmodules[relmodule],e


    def test__search(self):
        """Test ZClient.search functionality for all possible modules."""
        for module in myclient.modules_metadata.keys():
            try:
                mylist=myclient.search(module,{'word':'Test'})
            except Exception, e:
                print 'Exception Occured:',module,e

    def test__taxes(self):
        """Test ZClient.taxes functionality."""
        myclient.taxes()

    def test__roles(self):
        """Test ZClient.roles functionality."""
        myclient.roles()

    def test__tab_groups(self):
        """Test ZClient.tab_groups functionality."""
        myclient.tab_groups()


    def test__convert_leads(self):
        """Test ZClient.convert_lead functionality."""
        retdict=insert_data(myclient,['Leads'])
        leadinsertdata={"overwrite": True, "notify_lead_owner": True, "notify_new_entity_owner": True,
            "account": global_record_list['Accounts'], "contact": global_record_list['Contacts'],
            "potential": {
                "Potential_Name": "Potential_Name0",
                "Closing_Date": date_formatter(time.localtime()),
                "Stage": "Stage0",
                "Amount": random_digits(4)
            }
            }
        result=myclient.convert_lead(retdict['Leads'],[leadinsertdata])



    def tearDown(self):
        time.sleep(30)

    @classmethod
    def tearDownClass(self):
        delete_data(myclient, global_record_list)


class TestZObject(TestCase):
    @classmethod
    def setUpClass(self):
        global global_record_list, myclient
        myclient = ZClient(client_id=client_id, client_secret=client_secret,
                           redirect_uri=redirect_uri, access_token=access_token,
                           refresh_token=refresh_token)
        myclient.loadmodules()
        global_record_list = insert_data(myclient)
        pass

    def setUp(self):
        pass

    def test__get_update_delete(self):
        """Test ZObject.update and ZObject.delete functionality for all possible modules."""
        recorddict=insert_data(myclient)
        product=None
        record_list=[]
        for module in recorddict.keys():
            if module == 'Cases':
                pass
            record=myclient.get(module,recorddict[module])
            update_data=create_update_data(True,[module])
            add_record_ids(module, update_data[module], recorddict, True)
            record.dict.update(update_data[module])
            record.update()
            record_list.append(record)
        for record in record_list:
            if record.module == 'Products' and record != record_list[-1]:
                record_list.remove(record)
                record_list.append(record)
            else:
                record.delete()
    def test__related_list(self):
        """Test ZObject.related_list functionality for all possible modules."""
        for module in global_record_list.keys():
            record=myclient.get(module,global_record_list[module])
            relatedmodules = {}
            for relation in myclient.modules_metadata[module]['modules'][0]['relations']:
                if relation['href']!=None:
                    relatedmodules[relation['module']]=relation['api_name']
            for relmodule in relatedmodules.keys():
                try:
                    mylist=record.related_list(relmodule,relatedmodules[relmodule])
                except Exception,e:
                    print 'Exception Occured:',module, relmodule, relatedmodules[relmodule],e

    def test__insert_update_notes(self):
        """Test ZObject.insert_notes and ZObject.update_notes functionality for all possible modules."""
        modulelist = []
        createnote = {'Note_Title': 'Test Note', 'Note_Content': 'Test Note Added'}
        updatenote = {'Note_Title': 'Test Update Note', 'Note_Content': 'Updated Note Added'}
        for module in myclient.modules_metadata.keys():
            relatedmodules=[relation['api_name'] for relation  in myclient.modules_metadata[module]['modules'][0]['relations']]
            if 'Notes' in relatedmodules:
                modulelist.append(module)
        for module in modulelist:
            if module in global_record_list:
                record = myclient.get(module, global_record_list[module])
                try:
                    note=record.insert_notes(createnote)
                    record.update_notes(note[0]['id'],updatenote)
                except Exception, e:
                    print 'Exception Occured inserting notes:', module, e



    def test__upload_download_files(self):
        """Test ZObject.upload_file and ZObject.download_file functionality for all possible modules."""
        modulelist = []
        for module in myclient.modules_metadata.keys():
            relatedmodules=[relation['api_name'] for relation  in myclient.modules_metadata[module]['modules'][0]['relations']]
            if 'Attachments' in relatedmodules:
                modulelist.append(module)
        attachmentrecord={}
        for module in modulelist:
            if module in global_record_list.keys():
                try:
                    record=myclient.get(module, global_record_list[module])
                    record.upload_file(os.path.abspath('') + '/TestJSON.txt')
                    if record.code == 'SUCCESS':
                        attachmentrecord[module]=record.details['id']
                except Exception,e:
                    print module,e
            if  module in attachmentrecord.keys():
                record.download_file(attachmentrecord[module], os.path.abspath('') + '/TestJSON-'+module+'.txt')
                os.remove(os.path.abspath('') + '/TestJSON-'+module+'.txt')

    def test__upload_download_photo(self):
        """Test ZObject.upload_photo and ZObject.download_photo functionality for Leads and Contacts."""
        modulelist=['Leads','Contacts']
        for module in modulelist:
            record=myclient.get(module,global_record_list[module])
            record.upload_photo(os.path.abspath('')+'/zoho-crm.png')
            record.download_photo(os.path.abspath('') + '/zoho-crm-'+module+'.png')
            os.remove(os.path.abspath('') + '/zoho-crm-'+module+'.png')

    def tearDown(self):
        time.sleep(20)

    @classmethod
    def tearDownClass(self):
        delete_data(myclient, global_record_list)

def create_update_data(update,modulelist=[]):
    """Create data to be inserted using metadata.conf.

    :param update: Data is to be udated or inserted.
    :param modulelist: List of modules to create data.
    :type update: bool
    :type modulelist: list
    :return: A dictionary of created data.
    :rtype: dict
    """
    if not modulelist:
        modulelist=myclient.modules_metadata.keys()
    if update:
        text='Updated'
    else:
        text='Test'
    if 'Activities' in modulelist:
        modulelist.remove('Activities')
    myinputlist={}
    for module in modulelist:
        moduledata={}
        modulemetadata=myclient.modules_metadata[module]['modules'][0]
        fields= modulemetadata['fields']
        for field in fields:
            field_api_name=field['api_name']
            if field['view_type']['create']:
                if field['data_type'] == 'bigint':
                    if field_api_name == 'Layout':
                        moduledata[field_api_name] = modulemetadata['layouts'][0]['id']
                    elif field_api_name == 'Participants':
                        pass
                    elif field_api_name == 'Visitor_Score':
                        pass
                    else:
                        moduledata[field_api_name] = random_digits(field['length'])
                elif field['data_type'] == 'boolean':
                    moduledata[field_api_name] = True
                elif field['data_type'] == 'currency':
                    moduledata[field_api_name] = random_digits(field['length'])
                elif field['data_type'] == 'date':
                        moduledata[field_api_name] = date_formatter(time.localtime())
                elif field['data_type'] == 'datetime':
                    moduledata[field_api_name] = datetime_formatter(time.localtime())
                elif field['data_type'] == 'double':
                    moduledata[field_api_name] = random_digits(field['length'])
                elif field['data_type'] == 'email':
                    moduledata[field_api_name] = field_api_name + "@test" + rand_string(3) + '.com'
                elif field['data_type'] == 'integer':
                    moduledata[field_api_name] = random_digits(field['length'])
                elif field['data_type'] == 'lookup' :
                    if field_api_name != 'Who_Id' and field_api_name != 'What_Id':
                        moduledata[field_api_name]=None
                elif field['data_type'] == 'ownerlookup':
                    pass
                elif field['data_type'] == 'multiselectpicklist':
                    if field['pick_list_values']:
                        moduledata[field_api_name] = field['pick_list_values'][1]['actual_value']
                elif field['data_type'] == 'phone':
                    moduledata[field_api_name] =  rand_string(10)
                elif field['data_type'] == 'picklist':
                    if field['pick_list_values']:
                        if field_api_name == 'Remind_At':
                            pass
                        elif field_api_name == 'Stage':
                            moduledata[field_api_name] = 'Needs Analysis'
                        else:
                            moduledata[field_api_name] = field['pick_list_values'][0]['actual_value']
                elif field['data_type'] == 'text':
                    if field_api_name == 'Call_Duration':
                        moduledata[field_api_name]=str(random_digits(field['length']-6))
                    elif field_api_name == 'Product_Details':
                        moduledata[field_api_name]=[{"Discount": 0,"Tax": 0,"book": None,"list_price": 12,"net_total": 1476,"product":"{Product_Id}","product_description": None,"quantity": 123,"quantity_in_stock": 0,"total": 1476,"total_after_discount": 1476,"unit_price": 12}]
                    elif field_api_name == 'Pricing_Details':
                        moduledata[field_api_name] = [ { "discount": 12,"from_range": 123,"to_range": 123123}]
                    else:
                        moduledata[field_api_name] = text + field_api_name + rand_string(5)
                elif field['data_type'] == 'textarea':
                    moduledata[field_api_name] = text + field_api_name + " " + rand_string(15)
                elif field['data_type'] == 'website':
                    moduledata[field_api_name] = "www.test"+field_api_name+rand_string(4)+'.com'
        myinputlist[module]=moduledata
    return myinputlist

def insert_data( myclient,mylist=[]):
    """Insert data into crm from the list.

    :param myclient: ZClient which makes the api calls.
    :param mylist: List of modules to be inserted.
    :type myclient: ZClient
    :type mylist: list.
    :returns: Inserted  records ids as a list.
    :rtype: dict
    """
    insertdata = create_update_data(False,mylist)
    recorddict = {}
    prioritylist = [u"Accounts", u"Contacts", u"Vendors", u"Potentials", u"Products"]
    if not mylist:
        mylist=insertdata.keys()
        mylist = set(mylist) - set(prioritylist)
        mylist = prioritylist + list(mylist)
    for module in mylist:
        mydata = insertdata[module]
        add_record_ids(module, mydata, recorddict, False)
        myobjects = myclient.insert(module, [mydata])
        if myobjects:
            myobject = myobjects[0]
            if myobject.code != 'SUCCESS':
                return False
            recorddict[module] = myobject['id']
    return recorddict

def update_data( myclient, recorddict):
    """Update records given as a dictionary

    :param myclient: ZClient which makes the api calls.
    :param recorddict: Dictionary of records to be updated.
    :type myclient: ZClient
    :type recorddict: dict
    :returns: Updated record ids as a list.
    :rtype: dict
    """
    data = create_update_data(True,recorddict.keys())
    for module in data.keys():
        mydata = data[module]
        add_record_ids(module, mydata, recorddict, True)
        myobjects = myclient.update(module, [mydata])
        if myobjects:
            myobject = myobjects[0]
            if myobject.code != 'SUCCESS':
                print myobject
                return False
            recorddict[module] = myobject['id']
    return recorddict

def delete_data( myclient, records):
    """Delete records given as a dictionary.

    :param myclient: ZClient which makes the api calls.
    :param records: Dictionary of records to be deleted.
    :type myclient: ZClient
    :type records: dict
    :return: None
    """
    mylist=records.keys()
    if 'Products' in mylist:
        mylist.remove('Products')
        mylist.append('Products')
    for val in mylist:
        result = myclient.delete(val, records[val])


def add_record_ids( module, mydata, recorddict, update):
    """To add record ids while creating sample data.

    :param module: Module of the record.
    :param mydata: Data to be updated.
    :param recorddict: Recod id dictionary.
    :param update: To check if it is update or create data.

    :type module: str
    :type mydata: dict
    :type recorddict: dict
    :type update: bool

    :returns:None
    """
    if update:
        mydata['id']=recorddict[module]
    if 'Potential_Name' in mydata.keys() and 'Potentials' in recorddict.keys() and module != 'Potentials':
        mydata['Potential_Name'] = recorddict['Potentials']
    if 'Product_Name' in mydata.keys() and 'Products' in recorddict.keys() and module != 'Products':
        mydata['Product_Name'] = recorddict['Products']
    if 'Account_Name' in mydata.keys() and 'Accounts' in recorddict.keys() and module != 'Accounts':
        mydata['Account_Name'] = recorddict['Accounts']
    if 'What_Id' in mydata.keys() and 'Accounts' in recorddict.keys() and module != 'Accounts':
        mydata['What_Id'] = recorddict['Accounts']
    if 'Contact_Name' in mydata.keys() and 'Contacts' in recorddict.keys() and module != 'Contacts':
        mydata['Contact_Name'] = recorddict['Contacts']
    if 'Vendor_Name' in mydata.keys() and 'Vendors' in recorddict.keys() and module != 'Vendors':
        mydata['Vendor_Name'] = recorddict['Vendors']
    if 'Quote_Name' in mydata.keys() and 'Quotes' in recorddict.keys() and module != 'Quotes':
        mydata['Quote_Name'] = recorddict['Quotes']
    if 'Product_Details' in mydata.keys() and 'Products' in recorddict.keys():
        for products in mydata['Product_Details']:
            products['product'] = recorddict['Products']
    if 'Sales_Order' in mydata.keys() and 'Sales_Orders' in recorddict.keys() and module != 'Sales_Orders':
        mydata['Sales_Order'] = recorddict['Sales_Orders']

def rand_string(length=10):
    """ Random string generator for testing purpose.
    :param length: Length of the string needed.
    :return: A random string.
    :rtype: str
    """
    valid_letters='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join((random.choice(valid_letters) for i in xrange(length)))

def random_digits(n):
    """Random digit creater for testing purpose.

    :param n: Length of the digits needed.
    :return: A random number
    :rtype: int
    """
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)

def date_formatter(mytime):
    """
    Sample date formater for Zoho CRM.
    :param mytime: Time to be converted using time.localtime
    :type mytime: time
    :returns: A string of formatted time.
    :rtype: str
    """
    return time.strftime("%Y-%m-%d", mytime)

def datetime_formatter(mytime):
    """Sample datetime formater for Zoho CRM.
    :param mytime: Time to be converted using time.localtime.
    :type mytime: time
    :returns: A string of formatted time.
    :rtype: str
    """
    strdate=time.strftime("%Y-%m-%dT%H:%M:%S%z", mytime)
    return  strdate[:22] + ':' + strdate[22:]
