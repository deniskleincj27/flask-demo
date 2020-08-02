#!/usr/bin/env python3
import os
import pprint
from pymongo import MongoClient
import datetime
from pathlib import Path

demo_database = 'demo_database'

TEXT = ('txt',)
DOCUMENTS = tuple('docx xls xlsx'.split())
IMAGES = tuple('jpeg png svg bmp'.split())
DEFAULTS = TEXT + DOCUMENTS + IMAGES

# /home/denis/dady/work/python/flask-tut/tests/top_dir
def create_data(dpath):

  client = MongoClient('localhost', 27018)
  db = client[demo_database]
  collection = db.data_list
  collection.drop()
  print('list_collection_names: ', db.list_collection_names())

  for user_no in range(len(DEFAULTS)):

    user = 'user_' + DEFAULTS[user_no]
    path = os.path.join(dpath, user)
    try:
      os.makedirs(path)
    except Exception as e:
      print('Error: ', e)
      pass

    fname = path + '/' + DEFAULTS[user_no].strip() + '_file' + '.' + DEFAULTS[user_no]
    print(path)
    print(fname)

    with open(fname, 'w') as f:
      f.write('this is file: ' + fname)

  data = {'file_name' : '',
          'location'  : '',
          'notes'     : '',
          'date'      : datetime.datetime.utcnow()
  }

  collection = db.data_list
  for dirpath, _, filenames in os.walk(dpath):

    for fname in filenames:
      print(fname)
      data['file_name'] = fname
      data['location'] = dirpath + '/'
      data['notes'] = 'this is ' + fname + ' in ' + dirpath
      data['date'] = datetime.datetime.utcnow()

      collection.update_one(data, {'$set':data}, upsert = True)
  print('names: ', db.list_collection_names(), collection.count_documents({}))
  for data in collection.find():
    pprint.pprint(data)

def dump_mongo_db():

  # client = pymongo.MongoClient("mongodb://localhost:27018")
  client = MongoClient('localhost', 27018)
  mdb = client[demo_database]
  collection = mdb.data_list

  print('get_mongo_db: ', collection)
  print('names: ', mdb.list_collection_names(), ' count_documents: ', collection.count_documents({}))
  print('list_database_names: ', client.list_database_names(), collection.find())
  for data in collection.find():
    pprint.pprint(data)

  return mdb

def create_flask(flask_dir):

  # Absolute Path: from root
  top_dir = os.getcwd()
  path = os.path.join(top_dir, flask_dir) + 'demo/'
  try:
    os.makedirs(path)
  except Exception as e:
    print('Exception 1: ', e)
    return

  dir_list = [
    path + 'static',
    path + 'templates',
    path + 'templates/auth',
    path + 'templates/blog',
    path + 'templates/home',
  ]

  for d in dir_list:
    path = os.path.join(top_dir, d)
    print(path)
    try:
      os.mkdir(path)
    except Exception as e:
      print('Exception 2: ', e)

#####################################################################################
#                                   main
#####################################################################################

if __name__ == '__main__':

#  create_flask('flask-demo/')
  create_data('./flask-demo/tests/top_dir/')
#  dump_mongo_db()
