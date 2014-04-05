#!/usr/bin/env python

# Universal Cassandra Driver
# by Carles Mateo
# http://blog.carlesmateo.com

import cgi
import cgitb
import logging
import sys

cgitb.enable() # Optional; for debugging only

__author__ = 'carles.mateo@gmail.com'
__blog__ = 'http://blog.carlesmateo.com'

log = logging.getLogger()
log.setLevel('DEBUG')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

KEYSPACE = "testkeyspace"

#def main():
print "Content-Type: text/html"
print ""

st_arguments = cgi.FieldStorage()
#for i in st_arguments.keys():
# print i
# print ":"
# print st_arguments[i].value
# print "<br />"

b_error = 0
i_error_code = 0
s_html_output = ''
b_use_keyspace = 1
b_use_user_and_password = 1

#TODO: port

def getParam(st_arguments, s_param):
    if st_arguments.has_key(s_param):
        return str(st_arguments.getvalue(s_param))

    return ''

def returnError(i_error_code, s_error_description, s_format):
    s_html_output = str(i_error_code)
    s_html_output = s_html_output + '\n' + s_error_description + '\n\n'
    log.info(s_html_output)
    print s_html_output
    sys.exit()

try:
    s_cql = getParam(st_arguments, 'cql')
    s_cluster = getParam(st_arguments, 'cluster')
    if s_cql == '' || s_cluster == '':
        returnError(i_error_code, 'Error parameters not send. Call with params: cql and cluster')
except Exception:
    returnError(i_error_code, 'Error parameters not send. Call with params: cql and cluster')

try:
    s_keyspace = getParam(st_arguments, 'keyspace')
    if s_keyspace == '':
        b_use_keyspace = 0
except Exception:
    b_use_keyspace = 0

try:
    s_user = getParam(st_arguments, 'user')
    s_password = getParam(st_arguments, 'password')
    if s_user == '' || s_password == '':
        b_use_user_and_password = 0
except Exception:
    b_use_user_and_password = 0
    s_user = ''
    s_password = ''

try:
    cluster = Cluster([s_cluster])
    session = cluster.connect()
except Exception:
    returnError(200, 'Cannot connect to cluster '+s_cluster)

if (b_use_keyspace == 1):
    #log.info("setting keyspace...")
    try:
        session.set_keyspace(s_keyspace)
    except:
        returnError(210, 'Keyspace ' + s_keyspace + ' does not exist'')

# Samples:
# Create Keyspace test
# http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=&cql=CREATE%20KEYSPACE%20test%20WITH%20REPLICATION%20=%20{%20%27class%27:%20%27SimpleStrategy%27,%20%27replication_factor%27:%20%271%27%20}


o_results = session.execute(s_cql)

try:
    rows = o_results.result()
except Exception:
    returnError(300, 'Error executing query')

for row in rows:
    log.info('\t'.join(row))

#if __name__ == "__main__":
#    main()