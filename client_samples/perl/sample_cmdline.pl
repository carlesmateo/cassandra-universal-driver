use strict;
use warnings;

# If you don't have LWP::Simple install it with:
# sudo perl -MCPAN -e'install "LWP::Simple"'
use LWP::Simple;
my $s_url = "http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=SELECT+*+FROM+mytable";
my $s_content = get($s_url);

print $s_content;
