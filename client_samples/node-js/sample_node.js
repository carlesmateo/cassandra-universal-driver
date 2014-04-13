// need execute
// npm install xml2js
var parseString = require('xml2js').parseString;

var http = require('http');

var options = {
  host: '127.0.0.1',
  port: 80,
  path: '/cgi-bin//cud.py?format=xml&cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=SELECT+*+FROM+mytable'
};

http.get(options, function(resp){
  resp.on('data', function(xml){
   	parseString(xml, function (err, result) {
    	console.dir(result.response.status);

    	for (var i in result.response.data) {
		  val = result.response.data[i].row;
		  console.log(val);
		}
	});
  });
}).on("error", function(e){
  console.log("Got error: " + e.message);
});