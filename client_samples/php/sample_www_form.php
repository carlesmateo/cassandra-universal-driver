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

if (isset($_POST['cluster'])) {
    $s_cluster = $_POST['cluster'];
} else {
    // Default keyspace
    $s_cluster = '127.0.0.1';
}

if (isset($_POST['keyspace'])) {
    $s_keyspace = $_POST['keyspace'];
} else {
    // Default keyspace
    $s_keyspace = 'test';
}

if (isset($_POST['format']) && $_POST['format'] == 'html') {
    $s_format = 'html';
} else {
    // Default case
    $s_format = 'xml';
}

?><html>
    <head>
        <meta charset="UTF-8">
        <title>PHP Cassandra Universal Driver Sample</title>
    </head>
    <body>
    <form name="form_cql" method="POST" action="">
    Cluster: <input type="text" name="cluster" value="<?php echo $s_cluster; ?>" /><br />
    Keyspace: <input type="text" name="keyspace" value="<?php echo $s_keyspace; ?>" /> (empty if you plan to create one)<br />
    CQL: <textarea name="cql" rows="4" cols="50"></textarea><br />
    Format: <input type="radio" name="format" value="html" <?php if ($s_format == 'html') { echo 'checked'; } ?>> html
    <input type="radio" name="format" value="xml" <?php if ($s_format == 'xml') { echo 'checked'; } ?>> xml<br />
    <br />
    <input type="submit" />
    </form>
<?php

if (isset($_POST['cql'])) {
    $s_cql = $_POST['cql'];
    $s_cql_encoded = urlencode($s_cql);

    $i_start_time = microtime(true);

    $s_cud_request = "http://127.0.0.1/cgi-bin/cud.py?format=$s_format&cluster=$s_cluster&user=test&password=test&keyspace=$s_keyspace&cql=$s_cql_encoded";

    if ($s_format == 'html') {
        $ch = curl_init($s_cud_request);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $s_results = curl_exec($ch);
        curl_close($ch);
    } else {
        $o_xml = simplexml_load_file($s_cud_request);
    }

    $i_finish_time_http = microtime(true);

    echo 'Your original query:<br />';
    echo '<pre>'.$s_cql.'</pre>';
    echo '<br />';

    if ($s_format == 'xml') {
        $s_error_code = $o_xml->status->error_code;
        $s_error_description = $o_xml->status->error_description;
    } else {
        $st_results = explode("\n", $s_results);
        $st_data = Array();

        $s_error_code = $st_results[0];
        $s_error_description = $st_results[1];
    }

    $s_row_separator = '||*||';
    $s_end_of_row    = '//*//';

    if ($s_error_code == '0') {
        // Ok
        if ($s_format == 'xml') {
            $i_num_registers = intval((string) $o_xml->status->rows_returned);
        } else {
            $i_num_registers = intval((string) $st_results[2]);
        }

        if ($s_format == 'html' && $i_num_registers > 0) {
            $st_data = explode($s_end_of_row, $st_results[3]);

            // Remove last empty row from explode
            if(empty($st_data[count($st_data)-1])) {
                unset($st_data[count($st_data)-1]);
            }

        }

        echo 'Rows returned: '.$i_num_registers."<br /><br />";

        $st_row_titles = Array();
        $st_rows = Array();

        if ($s_format == 'xml') {
            if ($i_num_registers > 0) {
                $i_counter == 0;

                $o_data = $o_xml->data;
                foreach($o_data->row as $s_row=>$o_row) {
                    foreach($o_row as $s_key=>$s_value) {
                        if ($i_counter == 0) {
                            // Take the column name from the XML structure
                            $st_row_titles[] = (string) $s_key;
                        }

                        // Take the data
                        $st_rows[$i_counter][$s_key] = (string) $s_value;

                    }

                    $i_counter++;
                }
            }

        } else {
            // Format html
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
        echo 'There was an error executing the query: error code: '.$s_error_code.' error description: '.$s_error_description."<br />";
    }

    $i_execution_time_http = $i_finish_time_http - $i_start_time;

    $i_finish_time = microtime(true);
    $i_execution_time = $i_finish_time-$i_start_time;

    echo 'Original response from driver:<br />';
    if ($s_format == 'xml') {
        var_dump($o_xml);
    } else {
        echo $s_results;
    }

    echo '<hr />';

    echo "Curl execution time: ".$i_execution_time_http."<br />";
    echo "Total execution time: ".$i_execution_time."<br />";

}


?>
    </body>
</html>