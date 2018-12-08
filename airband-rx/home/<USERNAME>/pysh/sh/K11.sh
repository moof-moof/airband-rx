#!/bin/bash
/usr/local/bin/rtl_fm -M am -f 127.6M -s 12k -g 40 -l 15 | play -r 12k -t raw -e s -b 16 -c 1 -V1 -
