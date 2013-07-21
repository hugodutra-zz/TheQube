try:
 import pysqlite2.dbapi2 as sqlite
except ImportError:
 import sqlite3 as sqlite
from logger import logger
logging = logger.getChild('core.db')

from glob import glob

import global_vars
import paths
import threading
import os


connection = cursor = None
VACUUM_REQUIRED = False
BUFFERS_TABLE = 'Buffers'

def initialize ():
 global BUFFERS_TABLE
 logging.debug("Database: Initializing database subsystem...")
 if not TableExists (BUFFERS_TABLE):
  CreateBuffersTable()

def CreateBuffersTable ():
 global BUFFERS_TABLE
 logging.debug("Database: Creating required table to store buffer metadata...")
 command = 'create table "%s" (id integer primary key, name string, index integer, table string, owner string);' % BUFFERS_TABLE


def NewCursor():
 global connection
 if not connection:
  try:
   connection = threading.local().connection
  except:
   connection = NewConnection()
  threading.local().connection = connection
 return connection.cursor()

def DestroyCursor ():
 pass

def NewConnection (file):
 global connection
 filename = paths.data_path(file)
 if not glob(filename):
  logging.debug("Database: Database file does not exist.")
  NewDatabase(filename)
 if type(threading.currentThread()) is threading._MainThread:
  global connection
  if not connection:
   connection = sqlite.connect(filename)
   return connection
 ThreadLocalData = threading.local()
 try:
  output = ThreadLocalData.connection
#  logging.info("Retrieving connection from local thread storage.")
 except:
#  logging.info("Establishing Thread Database connection to %s from thread %s" % (filename, threading.currentThread().name))
  con = sqlite.connect(filename)
  #con.row_factory = sqlite.dbapi2.Row
  ThreadLocalData.connection = con
  return ThreadLocalData.connection

def NewDatabase(filename):
 logging.info("Database: Creating new file: %s " % filename)
 if not filename:
  logging.warning("Database: No filename supplied to the database creator.")
  return
 con=sqlite.connect(filename)
 con.close();
 con=sqlite.connect(filename);
 logging.debug("Database: Created new file: %s" % filename)
 return con;

def get_tables ():
 cur=NewCursor()
 cur.execute("select name from sqlite_master where type = 'table';")
 tables = [table[0] for table in cur]
 cur.close()
 return tables

def TableExists(tablename):

 return tablename in get_tables()

def CreateTable (name, fields):
 logging.info("Database: Creating table %s with fields %s" % (name, fields))
 command = 'create table "%s" (' % name
 uniques = "UNIQUE("
 for field in fields:
  command = "%s %s," % (command, field)
 for item in fields[1:]:
  if uniques == "UNIQUE(":
   uniques = "%s%s" % (uniques, item.split(' ')[0])
  else:
   uniques = "%s, %s" % (uniques, item.split(' ')[0])
 uniques = "%s)" % uniques
 command = "%s, %s)" % (command[:-1], uniques)
# print command
 cur = NewCursor()
 cur.execute(command)
 cur.close()
 cur.connection.commit()
 return True


def SyncTable (buffer, table):
 logging.debug("Database: DBSync: Syncing table %s with buffer %s" % (table, buffer.name))
 cur = NewCursor()
 cur.execute('PRAGMA table_info("%s");' % table)
 fields = cur.fetchall()
 for (counter, i) in enumerate(fields):
  fields[counter] = "%s %s" % (i[1], i[2])
  if i[-1] == 1:
   fields[counter] = "%s primary key" % fields[counter]
 required = list(set(buffer.fields).difference(set(fields)))
 if required:
  logging.debug("Database: dbsync: Table %s requires aditional fields %s.  Adding." % (table, required))
  commands = []
  for column in required:
   command = 'ALTER TABLE "%s" ADD COLUMN %s;' % (table, column)
   commands.append(command)
  for item in commands:
   cur.execute(item)
  cur.connection.commit()
  cur.close()
  logging.debug("Database: dbsync: Synchronization completed successfully.")
  return True

def ListColumns(table):
 #Provided a table name, returns a list which represents the fields of the table
 result = []
 cur = NewCursor()
 cur.execute('PRAGMA table_info("%s");' % table)
 fields = cur.fetchall()
 for (counter, i) in enumerate(fields):
  result.append(i[1])
 cur.close()
 cur.connection.close()
 return result

def shutdown ():
 #Call this on app exit.  Vacuums up the database if required.
 logging.debug("Database: Deactivating database subsystem.")
 global VACUUM_REQUIRED
 if VACUUM_REQUIRED:
  logging.debug("Database: Performing database optomizations....")
  cur = NewCursor()
  cur.execute('VACUUM')
  cur.close()
  cur.connection.close()
 return True
