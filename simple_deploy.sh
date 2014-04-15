#!/bin/bash

# By Carles Mateo
# blog.carlesmateo.com

# Dir inside cassandra-universal-driver
s_dir_origin="cgi-bin/"
s_dir_destination="/usr/lib/cgi-bin/"
s_dir_cassandra="cassandra/"
s_dir_origin_php_samples="client_samples/php/"
s_dir_destination_www="/var/www/"
s_rsync_params="--verbose --recursive --perms --executability --acls --xattrs --times --compress --human-readable --progress --ignore-errors --safe-links"

echo "Simple deploy"
echo "============="
echo
echo "by Carles Mateo http://blog.carlesmateo.com"
echo
echo "Copying Cassandra Universal Driver to $s_dir_destination"
echo
echo "1.- Copying cgi to $s_dir_destination"
echo

sudo rsync $s_rsync_params $s_dir_origin $s_dir_destination

echo
echo "2.- Copying cassandra original drivers to $s_dir_destination"
echo
sudo rsync $s_rsync_params $s_dir_cassandra $s_dir_destination

echo
echo "3.- Copying PHP samples to $s_dir_destination_www"
echo
sudo rsync $s_rsync_params $s_dir_origin_php_samples $s_dir_destination

echo
echo "Finished"
echo