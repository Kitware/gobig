#! /usr/bin/env python

import json
import os.path

from argparse import ArgumentParser
from time import sleep

from girder.constants import AssetstoreType
from girder_client import GirderClient

def rest(client, method, *args, **kwds):
    method = getattr(client, method)
    old_parameters = kwds.pop('parameters')
    kwds['parameters'] = {}
    kwds['parameters'].update(
        (k, v[1:-1]) if (v.startswith('"') and v.endswith('"')) else (k, v)
        for k, v in (
            (key, json.dumps(value))
            for key, value in old_parameters.items()))

    print kwds['parameters']
    return method(*args, **kwds)

def post(client, *args, **kwds):
    return rest(client, 'post', *args, **kwds)

def put(client, *args, **kwds):
    return rest(client, 'put', *args, **kwds)

def get(client, *args, **kwds):
    return rest(client, 'get', *args, **kwds)

def register_and_authenticate(client, **kwds):
    username = kwds['login']
    password = kwds['password']

    try:
        client.authenticate(username, password)
    except:
        post(client,
             'user',
             parameters=dict(login=username,
                             password=password,
                             email=kwds['email'],
                             firstName=kwds['firstName'],
                             lastName=kwds['lastName']))
        client.authenticate(username, password)

def find_assetstore(name):
    offset = 0
    limit = 50
    result = None
    while result is None:
        assetstore_list = get(client,
                              'assetstore',
                              parameters=dict(limit=limit, offset=offset))

        if not assetstore_list:
            break

        for assetstore in assetstore_list:
            if assetstore['name'] == name:
                result = assetstore['_id']
                break

        offset += limit

    return result

def find_collection(name):
    offset = 0
    limit = 50
    result = None
    while result is None:
        collection_list = get(client,
                              'collection',
                              parameters=dict(limit=limit, offset=offset))

        if not collection_list:
            break

        for collection in collection_list:
            if collection['name'] == name:
                result = collection['_id']
                break

        offset += limit

    return result

parser = ArgumentParser(description='Initialize the girder environment')
parser.add_argument('--user', help='name of the user to create')
parser.add_argument('--password', help='password of the user to create')
parser.add_argument('--host', help='host to connect to')
parser.add_argument('--port', type=int, help='port to connect to')
parser.add_argument('--data-root', help=("root directory for the girder "
                                         "server's local filesystem data"))
parser.add_argument('--broker', help='romanesco broker URI')
parser.add_argument('--hdfs-user', help='Hadoop HDFS user')
parser.add_argument('--hdfs-namenode', help='Hadoop HDFS namenode')
parser.add_argument('--hdfs-port', type=int, help='Hadoop HDFS port')
parser.add_argument('--web-hdfs-port', type=int, help='Hadoop WebHDFS port')

args = parser.parse_args()

client = GirderClient(host=args.host, port=args.port)
register_and_authenticate(client,
                          login=args.user,
                          password=args.password,
                          email='{}@localhost.com'.format(args.user),
                          firstName='Girder',
                          lastName='Admin')

local_assetstore_name = 'local'

if find_assetstore(local_assetstore_name) is None:
    post(client,
         'assetstore',
         parameters=dict(name=local_assetstore_name,
                         type=AssetstoreType.FILESYSTEM,
                         root=os.path.join(args.data_root,
                                           'assetstores',
                                           'local'),
                         readOnly=False))

put(client,
    'system/plugins',
    parameters=dict(plugins=['celery_jobs',
                             'climos_test',
                             'user_quota',
                             'hdfs_assetstore',
                             'jobs',
                             'romanesco',
                             'sparktest']))

client.put('system/restart')

sleep(30)

put(client,
    'system/setting',
    parameters=dict(list=[dict(key='romanesco.require_auth', value=False),
                          dict(key='romanesco.broker', value=args.broker),
                          dict(key='romanesco.backend', value=args.broker)]))

hdfs_assetstore_name = 'hdfs'
if find_assetstore(hdfs_assetstore_name) is None:
    post(client,
         'assetstore',
         parameters=dict(name=hdfs_assetstore_name,
                         type='hdfs',
                         path='/girder',
                         host=args.hdfs_namenode,
                         user=args.hdfs_user,
                         port=args.hdfs_port,
                         webHdfsPort=args.web_hdfs_port))

hdfs_collection_name = 'hdfs'
if find_collection(hdfs_collection_name) is None:
    post(client,
         'collection',
         parameters=dict(name=hdfs_collection_name,
                         description='HDFS Collection',
                         public=False))

client.put('system/restart')

