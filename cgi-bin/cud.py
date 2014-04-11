#!/usr/bin/env python

# Universal Cassandra Driver
# cassandradriver.com
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

st_arguments = cgi.FieldStorage()

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
    i_error_code = 0
    s_error_description = 'Data returned Ok'

    returnResponse(i_error_code, s_error_description, i_counter, s_data, s_format)
    return

def returnError(i_error_code, s_error_description, s_format = 'html'):
    i_counter = 0
    s_data = ''

    returnResponse(i_error_code, s_error_description, i_counter, s_data, s_format)
    return

def returnResponse(i_error_code, s_error_description, i_counter, s_data, s_format = 'html'):
    if s_format == 'xml':
        print "Content-Type: text/xml"
        print ""
        s_html_output = "<?xml version='1.0' standalone='yes'?>"
        s_html_output = s_html_output + '<response>' \
                                        '<status>' \
                                        '<error_code>' + str(i_error_code) + '</error_code>' \
                                        '<error_description>' + s_error_description + '</error_description>' \
                                        '<rows_returned>' + str(i_counter) + '</rows_returned>' \
                                        '</status>' \
                                        '<data>' + s_data + '</data>' \
                                        '</response>'
    else:
        print "Content-Type: text/html"
        print ""
        s_html_output = str(i_error_code)
        s_html_output = s_html_output + '\n' + s_error_description + '\n'
        s_html_output = s_html_output + str(i_counter) + '\n'
        s_html_output = s_html_output + str(s_data) + '\n'

    log.info(s_html_output)
    print s_html_output
    sys.exit()
    return

# First format of the response
try:
    s_format = getParam(st_arguments, 'format')
    if s_format == '':
        s_format = 'html'
except Exception:
    returnError(110, 'Problem with param format')

try:
    s_cql = getParam(st_arguments, 'cql')
    s_cluster = getParam(st_arguments, 'cluster')
    if s_cql == '' or s_cluster == '':
        returnError(100, 'Error parameters not send. Call with params: cql and cluster', s_format)
except Exception:
    returnError(100, 'Error parameters not send. Call with params: cql and cluster', s_format)

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
    returnError(200, 'Cannot connect to cluster ' + s_cluster + '.' + e.message, s_format)

if (b_use_keyspace == 1):
    #log.info("setting keyspace...")
    try:
        session.set_keyspace(s_keyspace)
    except:
        returnError(210, 'Keyspace ' + s_keyspace + ' does not exist', s_format)

# Samples:
# Create Keyspace test
# http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=&cql=CREATE%20KEYSPACE%20test%20WITH%20REPLICATION%20=%20{%20%27class%27:%20%27SimpleStrategy%27,%20%27replication_factor%27:%20%271%27%20}
# Create mytable
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=CREATE TABLE mytable (thekey text,col1 text,col2 text,PRIMARY KEY (thekey, col1))
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=CREATE TABLE mytable2 (thekey text,col1 text,col2 text,anumber int,PRIMARY KEY (thekey, col1))
# http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=CREATE+TABLE+IF+NOT+EXISTS+test+%28userid+int%2C+firstname+text%2C+lastname+text%2C+tele+set%3Ctext%3E%2C+emails+set%3Ctext%3E%2C+skills+list%3Ctext%3E%2C+todos+map%3Ctimestamp%2Ctext%3E%2C+PRIMARY+KEY+%28userid%29+%29%3B
# Insert to mytable, not UrlEncoded
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT INTO mytable (thekey, col1, col2)VALUES ('first', 'Carles Mateo', 'http://blog.carlesmateo.com')
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT INTO mytable2 (thekey, col1, col2, anumber)VALUES ('first', 'Carles Mateo', 'http://blog.carlesmateo.com', 7)
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT INTO test (userid,firstname,lastname) VALUES (1,'Carles','Mateo')
# UrlEncoded
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT+INTO+test+%28userid%2Cfirstname%2Clastname%29+VALUES+%281%2C%27Carles%27%2C%27Mateo%27%29

# Select from mytable
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=SELECT+*+FROM mytable

try:
    o_results = session.execute_async(s_cql)
except Exception as e:
    returnError(300, 'Error executing query. ' + e.message, s_format)

try:
    rows = o_results.result()
except Exception as e:
    returnError(310, 'Query returned result error. ' + e.message, s_format)

# Query returned values
i_counter = 0
try:
    #print rows

    if rows is not None:
        for row in rows:
            i_counter = i_counter + 1

            if i_counter == 1 and s_format == 'html':
                for key, value in vars(row).iteritems():
                    s_data = s_data + key + s_row_separator

                s_data = s_data + s_end_of_row

            if s_format == 'xml':
                s_data = s_data + '<row>'

            for key, value in vars(row).iteritems():
                # Convert to string numbers or other types
                if value is not None:
                    if s_format == 'xml':
                        s_data = s_data + '<' + key + '>' + str(value) + '</' + key + '>'
                    else:
                        s_data = s_data + str(value) + s_row_separator
                else:
                    if s_format == 'xml':
                        s_data = s_data + '<' + key + '>' + '</' + key + '>'
                    else:
                        s_data = s_data + s_row_separator

            if s_format == 'xml':
                s_data = s_data + '</row>'
            else:
                s_data = s_data + s_end_of_row
            #log.info('\t'.join(row))
except Exception as e:
    # No iterable data
    returnSuccess(i_counter, s_data, s_format)

returnSuccess(i_counter, s_data, s_format)
