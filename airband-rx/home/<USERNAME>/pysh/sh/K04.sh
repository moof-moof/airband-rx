#!/bin/bash
/usr/local/bin/rtl_fm -M am -f 118.5M -s 12k -g 25 -l 15 | play -r 12k -t raw -e s -b 16 -c 1 -V1 -
