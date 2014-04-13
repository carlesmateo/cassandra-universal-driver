<html>
    <head>
        <meta charset="UTF-8">
        <title>PHP Cassandra Universal Driver Sample</title>
    </head>
    <body>
<?php

/**
 * Creator:      Carles Mateo
 * Date Created: 2014-04-07 13:46
 * Last Updater: Carles Mateo
 * Last Updated: 2014-04-08 18:38
 * Filename:     sample_www.php
 * Description:  Sample demo of using Cassandra Universal Driver with PHP from web
 * Version:      1.0
 */

$i_start_time = microtime(true);

$s_cql = 'SELECT * FROM mytable';
$s_cql_encoded = urlencode($s_cql);

$ch = curl_init("http://127.0.0.1/cgi-bin/cud.py?cluster=127.0.0.1&user=test&password=test&keyspace=test&cql=$s_cql_encoded");
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$s_results = curl_exec($ch);
curl_close($ch);

$i_finish_time_http = microtime(true);

echo 'Your original query:<br />';
echo '<pre>'.$s_cql.'</pre>';
echo '<br />';

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

    // Remove last empty row from explode
    if(empty($st_data[count($st_data)-1])) {
        unset($st_data[count($st_data)-1]);
    }

    echo 'Rows returned: '.$i_num_registers."<br /><br />";

    $i_counter = -1;
    foreach($st_data as $i_key=>$s_row) {
        if ($i_counter == -1) {
            // First row is for names of the rows
            $st_row_titles = explode($s_row_separator, $s_row);
        } else {
            $st_rows[] = explode($s_row_separator, $s_row);

        }
        $i_counter++;
    }

    // Print the results
    if ($i_counter>0) {
        // We have results to show
        echo '<table border="1">';
        $i_row_num = 0;
        foreach($st_rows as $i_key_row=>$st_row) {
            echo '<tr>';
            if ($i_row_num == 0) {
                echo '<th>Row</th>';
                foreach($st_row_titles as $i_num_column=>$s_cell) {
                    echo '<th>'.$s_cell.'</th>';
                }
                echo '</tr><tr>';
            }

            echo '<td>'.($i_row_num+1).'</td>';
            foreach($st_row as $i_num_column=>$s_cell) {
                echo '<td>'.$s_cell.'</td>';
            }

            echo '</tr>';
            $i_row_num++;
        }
        echo '</table>';
    }
    echo "<br />";


} else {
    echo 'There was an error executing the query: error code: '.$st_results[0].' error description: '.$st_results[1]."<br />";
}

$i_execution_time_http = $i_finish_time_http - $i_start_time;

$i_finish_time = microtime(true);
$i_execution_time = $i_finish_time-$i_start_time;

echo "Curl execution time: ".$i_execution_time_http."<br />";
echo "Total execution time: ".$i_execution_time."<br />";
?>
    </body>
</html>