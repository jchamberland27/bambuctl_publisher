#!/bin/bash

# Check if the correct number of arguments were passed
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <host> <port> <username> <password>"
  exit 1
fi

# Assign arguments to variables
HOST=$1
PORT=$2
USER=$3
PASS=$4

lftp -u $USER,$PASS -p $PORT ftps://$HOST << EOF

set ssl:verify-certificate no
glob -a rm *.gcode
glob -a rm *.3mf
bye
EOF