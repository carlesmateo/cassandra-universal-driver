<?php

$i_start_time = microtime(true);

$ch = curl_init("http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=SELECT+*+FROM+mytable");
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$s_results = curl_exec($ch);
curl_close($ch);

$i_finish_time_http = microtime(true);

$s_row_separator = '||*||';
$s_end_of_row    = '//*//';

$st_results = explode("\n", $s_results);
$st_data = Array();

if ($st_results[0] == 0) {
    // Ok
    $i_num_registers = $st_results[2];

    if ($i_num_registers > 0) {
        $st_data = explode($s_end_of_row, $st_results[3]);
    }

    echo 'Rows returned: '.$i_num_registers."\n";

    foreach($st_data as $i_key=>$s_row) {
        $st_row = explode($s_row_separator, $s_row);

        foreach($st_row as $i_key_row=>$s_cell) {
            echo $s_cell."\t";
        }
        echo "\n";
    }

} else {
    echo 'There was an error executing the query: error code: '.$st_results[0].' error description: '.$st_results[1]."\n";
}


$i_execution_time_http = $i_finish_time_http - $i_start_time;

$i_finish_time = microtime(true);
$i_execution_time = $i_finish_time-$i_start_time;

echo "Curl execution time: ".$i_execution_time_http."\n";
echo "Total execution time: ".$i_execution_time."\n";
