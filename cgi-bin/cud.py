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

s_row_separator = "||*||"
s_end_of_row = "//*//"
s_data = ''

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

def returnSuccess(i_counter, s_data, s_format = 'html'):
    s_html_output = str(0)
    s_html_output = s_html_output + '\n' + 'Data returned Ok' + '\n'
    s_html_output = s_html_output + str(i_counter) + '\n'
    s_html_output = s_html_output + str(s_data) + '\n'
    log.info(s_html_output)
    print s_html_output
    sys.exit()
    return

def returnError(i_error_code, s_error_description, s_format = 'html'):
    s_html_output = str(i_error_code)
    s_html_output = s_html_output + '\n' + s_error_description + '\n0\n\n'
    log.info(s_html_output)
    print s_html_output
    sys.exit()
    return

try:
    s_cql = getParam(st_arguments, 'cql')
    s_cluster = getParam(st_arguments, 'cluster')
    if s_cql == '' or s_cluster == '':
        returnError(100, 'Error parameters not send. Call with params: cql and cluster')
except Exception:
    returnError(100, 'Error parameters not send. Call with params: cql and cluster')

try:
    s_keyspace = getParam(st_arguments, 'keyspace')
    if s_keyspace == '':
        b_use_keyspace = 0
except Exception:
    b_use_keyspace = 0

try:
    s_user = getParam(st_arguments, 'user')
    s_password = getParam(st_arguments, 'password')
    if s_user == '' or s_password == '':
        b_use_user_and_password = 0
except Exception:
    b_use_user_and_password = 0
    s_user = ''
    s_password = ''

try:
    cluster = Cluster([s_cluster])
    session = cluster.connect()
except Exception as e:
    returnError(200, 'Cannot connect to cluster ' + s_cluster + '.' + e.message)

if (b_use_keyspace == 1):
    #log.info("setting keyspace...")
    try:
        session.set_keyspace(s_keyspace)
    except:
        returnError(210, 'Keyspace ' + s_keyspace + ' does not exist')

# Samples:
# Create Keyspace test
# http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=&cql=CREATE%20KEYSPACE%20test%20WITH%20REPLICATION%20=%20{%20%27class%27:%20%27SimpleStrategy%27,%20%27replication_factor%27:%20%271%27%20}
# Create mytable
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=CREATE TABLE mytable (thekey text,col1 text,col2 text,PRIMARY KEY (thekey, col1))
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=CREATE TABLE mytable2 (thekey text,col1 text,col2 text,anumber int,PRIMARY KEY (thekey, col1))
# Insert to mytable
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT INTO mytable (thekey, col1, col2)VALUES ('first', 'Carles Mateo', 'http://blog.carlesmateo.com')
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT INTO mytable2 (thekey, col1, col2, anumber)VALUES ('first', 'Carles Mateo', 'http://blog.carlesmateo.com', 7)
# Select from mytable
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=SELECT * FROM mytable

try:
    o_results = session.execute_async(s_cql)
except Exception as e:
    returnError(300, 'Error executing query. ' + e.message )

try:
    rows = o_results.result()
except Exception as e:
    returnError(310, 'Query returned result error. ' + e.message)

# Query returned values
i_counter = 0
try:
    #print rows

    if rows is not None:
        for row in rows:
            i_counter = i_counter + 1

            if i_counter == 1:
                for key, value in vars(row).iteritems():
                    s_data = s_data + key + s_row_separator

                s_data = s_data + s_end_of_row

            for key, value in vars(row).iteritems():
                # Convert to string numbers or other types
                s_data = s_data + str(value) + s_row_separator

            #s_data = s_data + s_row_separator.join(row)
            s_data = s_data + s_end_of_row
            #log.info('\t'.join(row))
except Exception as e:
    # No iterable data
    returnSuccess(i_counter, s_data)

returnSuccess(i_counter, s_data)


#if __name__ == "__main__":
#    main()