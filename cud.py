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
#for i in arguments.keys():
# print i
# print ":"
# print arguments[i].value
# print "<br />"


b_error = 0
i_error_code = 0
s_html_output = ''

try:
    s_cql = st_arguments['cql']
    s_keyspace = st_arguments['keyspace']
    s_cluster = st_arguments['cluster']
    s_user = st_arguments['user']
    s_password = st_arguments['password']
except Exception:
    b_error = 1
    i_error_code = 100 # No params passed
    s_html_output = str(i_error_code)
    s_html_output = s_html_output +'\nError parameters not send\n\n'
    # Log into Apache's error log
    log.info(s_html_output)
    # Return via Tcp
    print s_html_output
    sys.exit()

try:
    cluster = Cluster([s_cluster])
    session = cluster.connect()
except Exception:
    b_error = 1
    i_error_code = 200 # Cannot connect
    s_html_output = str(i_error_code)
    s_html_output = s_html_output + '\nCannot connect to cluster\n\n'
    # Log into Apache's error log
    log.info(s_html_output)
    # Return via Tcp
    print s_html_output
    sys.exit()

rows = session.execute("SELECT keyspace_name FROM system.schema_keyspaces")
if KEYSPACE in [row[0] for row in rows]:
    log.info("dropping existing keyspace...")
    session.execute("DROP KEYSPACE " + KEYSPACE)

log.info("creating keyspace...")
session.execute("""
    CREATE KEYSPACE %s
    WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
    """ % KEYSPACE)

log.info("setting keyspace...")
session.set_keyspace(KEYSPACE)

log.info("creating table...")
session.execute("""
    CREATE TABLE mytable (
        thekey text,
        col1 text,
        col2 text,
        PRIMARY KEY (thekey, col1)
    )
    """)

query = SimpleStatement("""
    INSERT INTO mytable (thekey, col1, col2)
    VALUES (%(key)s, %(a)s, %(b)s)
    """, consistency_level=ConsistencyLevel.ONE)

prepared = session.prepare("""
    INSERT INTO mytable (thekey, col1, col2)
    VALUES (?, ?, ?)
    """)

for i in range(10):
    log.info("inserting row %d" % i)
    session.execute(query, dict(key="key%d" % i, a='a', b='b'))
    session.execute(prepared.bind(("key%d" % i, 'b', 'b')))

future = session.execute_async("SELECT * FROM mytable")
log.info("key\tcol1\tcol2")
log.info("---\t----\t----")

try:
    rows = future.result()
except Exception:
    log.exeception()

for row in rows:
    log.info('\t'.join(row))

session.execute("DROP KEYSPACE " + KEYSPACE)

#if __name__ == "__main__":
#    main()