import configparser
import json
from sys import stdin

__CONFIG__=configparser.RawConfigParser()


def read_config(file):
    with open(file) as f:
        file_content = '[config]\n' + f.read()
    __CONFIG__.read_string(file_content)
    return __CONFIG__

def config(key,default=''):
    c=__CONFIG__['config']
    return c.get(key,default)

def get_config():
    items=__CONFIG__.items('config')
    data = {}
    for k, v in items:
        data[k] = v
    return data

def readjsoninput():
    input = stdin.read()
    return json.loads(input)


def returncode(code,message):
    '''
        Retourne le code au format json pour le backend
    '''
    data={}
    data['status']=code
    data['message']=message
    return json.dumps(data)

def is_backend_concerned(entity):
    peopleType=find_key(entity,config('branchAttr'))
    if type(peopleType) is list:
        listBackend=config('backendFor')
        for v in peopleType:
          peopleType=v
          if (listBackend.find(peopleType) == -1):
             return False
    return True

def find_key(element, key):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    return _finditem(element,key)

def _finditem(obj, key):
    if key in obj: return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            item = _finditem(v, key)
            if item is not None:
                return item

def make_entry_array(entity):
    data={}
    if "identity" in entity['payload']:
        objectclasses = entity['payload']['identity']['identity']['additionalFields']['objectClasses']
        inetOrgPerson=entity['payload']['identity']['identity']['inetOrgPerson']
        additionalFields=entity['payload']['identity']['identity']['additionalFields']['attributes']

    else:
        objectclasses=entity['payload']['additionalFields']['objectClasses']
        inetOrgPerson = entity['payload']['inetOrgPerson']
        additionalFields = entity['payload']['additionalFields']['attributes']
    #inetOrgPerson
    for k,v in inetOrgPerson.items():
        data[k]=str(v)

    for obj in objectclasses:
        for k,v in additionalFields[obj].items():
            data[k]=str(v)
    return data


def make_objectclass(entity):
    data = {}
    if "identity" in entity['payload']:
        objectclasses = entity['payload']['identity']['identity']['additionalFields']['objectClasses']
    else:
        objectclasses = entity['payload']['additionalFields']['objectClasses']

    return ['top', 'inetOrgPerson'] + objectclasses


def make_entry_array_without_empty(entity):
    data={}
    data1=make_entry_array(entity)
    for k,v in data1.items():
        if str(v) != "":
            data[k]=v
    return data
