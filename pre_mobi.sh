#!/bin/bash

cat $1 | awk -F"\t|:| " '
BEGIN{

    OFS = "\t";

    sum_lon = 0;
    sum_lat = 0;

    num = 0;
    count = 1;

    pre_id = 0;
    pre_date = "";
    pre_hour = "";
}
{

    filename = "taxi_roma_hourly_"""count""".data"
    if (NR == 1){
        id = $1;
        hour = $3;
    }
    if (hour != $3){
        print pre_id, pre_date, pre_hour, sum_lon/num, sum_lat/num >> filename
        num = 0;
        sum_lon = 0;
        sum_lat = 0;
        hour = $3;
    }
    if (id != $1){
        id = $1;
        close(filename);
        count = count + 1;
    }

    pre_id = $1;
    pre_date = $2;
    pre_hour = $3;

    sum_lon += $6;
    sum_lat += $7;
    num += 1;

}
END{print "Processed in total """count""" taxis.";}'
