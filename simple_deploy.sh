#!/bin/bash

# By Carles Mateo
# http://blog.carlesmateo.com

# Dir inside cassandra-universal-driver
s_dir_origin="cgi-bin/"
s_dir_destination="/usr/lib/cgi-bin/"
s_dir_origin_cassandra="cassandra"
s_dir_origin_php_samples="client_samples/php/"
s_dir_destination_www="/var/www/"

s_rsync_params="--verbose --recursive --perms --executability --acls --xattrs --times --compress --human-readable --progress --ignore-errors --safe-links"

s_cud_file="$s_dir_origin/cud.py"
s_cassandra_file="$s_dir_origin_cassandra/cluster.py"

echo "Simple deploy"
echo "============="
echo
echo "by Carles Mateo http://blog.carlesmateo.com"
echo "Manual at http://cassandradriver.com/manual"
echo
echo "If you installed all the requirements, this script does a fast deploy"
echo
echo "Checking for basic files..."
echo

# Checking that Carles Mateo's cud.py exists
if [ -f $s_cud_file ];
then
    echo "$s_cud_file exists. Ok"
else
    echo "$s_cud_file does not exists!. Cancelling"
    exit
fi

# Checking that the python driver from Datastax exists
# We check only one file and trust the rest of the files are there
if [ -f $s_cassandra_file ];
then
    echo "$s_cassandra_file exists. Ok"
else
    echo "$s_cassandra_file does not exists!. Cancelling"
    exit
fi

echo
echo "Copying Cassandra Universal Driver to $s_dir_destination"
echo
echo "1.- Copying cgi to $s_dir_destination"
echo

sudo rsync $s_rsync_params $s_dir_origin $s_dir_destination

echo
echo "2.- Copying cassandra original drivers to $s_dir_destination"
echo
sudo rsync $s_rsync_params $s_dir_origin_cassandra $s_dir_destination

echo
echo "3.- Copying PHP samples to $s_dir_destination_www"
echo
sudo rsync $s_rsync_params $s_dir_origin_php_samples $s_dir_destination_www

echo
echo "Finished. Test it with http://127.0.0.1/sample_www_form.php"
echo