#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Universal Cassandra Driver
# cassandradriver.com
# by Carles Mateo
# http://blog.carlesmateo.com

# Use with Python 2.7+
# Original Cassandra driver not supporting Python 3

import cgi
import cgitb
import logging
import sys

cgitb.enable() # Optional; for debugging only

__author__ = 'Carles Mateo'
__blog__ = 'http://blog.carlesmateo.com'

log = logging.getLogger()
log.setLevel('DEBUG')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

s_row_separator = u"||*||"
s_end_of_row = u"//*//"
s_data = u""

st_arguments = cgi.FieldStorage()

b_error = 0
i_error_code = 0
s_html_output = u""
b_use_keyspace = 1          # By default use keyspace
b_use_user_and_password = 1 # Not implemented yet

def get_param(st_arguments, s_param):
    if st_arguments.has_key(s_param):
        return str(st_arguments.getvalue(s_param))

    return ''

def return_success(i_counter, s_data, s_format = 'html'):
    i_error_code = 0
    s_error_description = 'Data returned Ok'

    return_response(i_error_code, s_error_description, i_counter, s_data, s_format)
    return

def return_error(i_error_code, s_error_description, s_format = 'html'):
    i_counter = 0
    s_data = ''

    return_response(i_error_code, s_error_description, i_counter, s_data, s_format)
    return

def return_response(i_error_code, s_error_description, i_counter, s_data, s_format = 'html'):

    if s_format == 'xml':
        print ("Content-Type: text/xml")
        print ("")
        s_html_output = u"<?xml version='1.0' encoding='utf-8' standalone='yes'?>"
        s_html_output = s_html_output + '<response>' \
                                        '<status>' \
                                        '<error_code>' + str(i_error_code) + '</error_code>' \
                                        '<error_description>' + '<![CDATA[' + s_error_description + ']]>' + '</error_description>' \
                                        '<rows_returned>' + str(i_counter) + '</rows_returned>' \
                                        '</status>' \
                                        '<data>' + s_data + '</data>' \
                                        '</response>'
    else:
        print("Content-Type: text/html; charset=utf-8")
        print("")
        s_html_output = str(i_error_code)
        s_html_output = s_html_output + '\n' + s_error_description + '\n'
        s_html_output = s_html_output + str(i_counter) + '\n'
        s_html_output = s_html_output + s_data + '\n'

    log.info(s_html_output)
    print(s_html_output.encode('utf-8'))
    sys.exit()
    return

def convert_to_string(s_input):
    # Convert other data types to string

    s_output = s_input

    try:
        if value is not None:

            if isinstance(s_input, unicode):
                # string unicode, do nothing
                return s_output

            if isinstance(s_input, (int, float, bool, set, list, tuple, dict)):
                # Convert to string
                s_output = str(s_input)
                return s_output

            # This is another type, try to convert
            s_output = str(input)
            return s_output

        else:
            # is none
            s_output = ""
            return s_output

    except Exception as e:
        # Were unable to convert to str, will return as empty string
        s_output = ""

    return s_output

def convert_to_utf8(s_input):
    return s_input.encode('utf-8')

def debugp(s_input, b_stop = 1):
    # Just for your tests
    print("Content-Type: text/html; charset=utf-8")
    print("")

    print (s_input)

    if b_stop == 1:
        sys.exit()

    return

# ********************
# Start of the program
# ********************

# Errors
# 100 'Error parameters not send. Call with params: cql and cluster'
# 110 'Problem with param format'
# 200 'Cannot connect to cluster ' + s_cluster + ' on port ' + s_port + '.' + e.message
# 210 'Keyspace ' + s_keyspace + ' does not exist'
# 300 'Error executing query. ' + e.message
# 310 'Query returned result error. ' + e.message


# First format of the response
s_format = get_param(st_arguments, 'format')
if s_format == '':
    s_format = 'html'

s_cql = get_param(st_arguments, 'cql')
s_cluster = get_param(st_arguments, 'cluster')
if s_cql == '' or s_cluster == '':
    return_error(100, 'Error parameters not send. Call with params: cql and cluster', s_format)

s_port = get_param(st_arguments, 'port')
if s_port == '':
    s_port = "9042" # default port

i_port = int(s_port)

s_keyspace = get_param(st_arguments, 'keyspace')
if s_keyspace == '':
    b_use_keyspace = 0

s_user = get_param(st_arguments, 'user')
s_password = get_param(st_arguments, 'password')
if s_user == '' or s_password == '':
    b_use_user_and_password = 0

try:
    cluster = Cluster([s_cluster], i_port)
    session = cluster.connect()
except Exception as e:
    return_error(200, 'Cannot connect to cluster ' + s_cluster + ' on port ' + s_port + '.' + e.message, s_format)

if (b_use_keyspace == 1):
    #log.info("setting keyspace...")
    try:
        session.set_keyspace(s_keyspace)
    except:
        return_error(210, 'Keyspace ' + s_keyspace + ' does not exist', s_format)

# Samples:
# Create Keyspace test
# http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=&cql=CREATE%20KEYSPACE%20test%20WITH%20REPLICATION%20=%20{%20%27class%27:%20%27SimpleStrategy%27,%20%27replication_factor%27:%20%271%27%20}
# Create mytable
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=CREATE TABLE mytable (thekey text,col1 text,col2 text,PRIMARY KEY (thekey, col1))
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=CREATE TABLE mytable2 (thekey text,col1 text,col2 text,anumber int,PRIMARY KEY (thekey, col1))
# http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=CREATE+TABLE+IF+NOT+EXISTS+test+%28userid+int%2C+firstname+text%2C+lastname+text%2C+tele+set%3Ctext%3E%2C+emails+set%3Ctext%3E%2C+skills+list%3Ctext%3E%2C+todos+map%3Ctimestamp%2Ctext%3E%2C+PRIMARY+KEY+%28userid%29+%29%3B
# Insert to mytable, not UrlEncoded
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT INTO mytable (thekey, col1, col2) VALUES ('first', 'Carles Mateo', 'http://blog.carlesmateo.com')
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT INTO mytable2 (thekey, col1, col2, anumber) VALUES ('first', 'Carles Mateo', 'http://blog.carlesmateo.com', 7)
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT INTO test (userid,firstname,lastname) VALUES (1,'Carles','Mateo')
# UrlEncoded
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=INSERT+INTO+test+%28userid%2Cfirstname%2Clastname%29+VALUES+%281%2C%27Carles%27%2C%27Mateo%27%29

# Select from mytable
# 127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=SELECT+*+FROM+mytable

try:
    o_results = session.execute_async(s_cql)
except Exception as e:
    return_error(300, 'Error executing query. ' + e.message, s_format)

try:
    rows = o_results.result()
except Exception as e:
    return_error(310, 'Query returned result error. ' + e.message, s_format)

# Query returned values
i_counter = 0
try:
    if rows is not None:
        for row in rows:
            #log.info('\t'.join(row))
            i_counter = i_counter + 1

            if i_counter == 1 and s_format == 'html':
                # first row is row titles
                for key, value in vars(row).iteritems():
                    s_data = s_data + key + s_row_separator

                s_data = s_data + s_end_of_row

            if s_format == 'xml':
                s_data = s_data + '<row>'

            for key, value in vars(row).iteritems():
                # Convert to string numbers or other types
                s_value = convert_to_string(value)
                if s_format == 'xml':
                    s_data = s_data + '<' + key + '>' + '<![CDATA[' + s_value + ']]>' + '</' + key + '>'
                else:
                    s_data = s_data + s_value
                    s_data = s_data + s_row_separator


            if s_format == 'xml':
                s_data = s_data + '</row>'
            else:
                s_data = s_data + s_end_of_row

except Exception as e:
    # No iterable data
    return_success(i_counter, s_data, s_format)

return_success(i_counter, s_data, s_format)
