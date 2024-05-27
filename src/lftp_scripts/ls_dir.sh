#!/bin/bash

# Check if the correct number of arguments were passed
if [ "$#" -ne 5 ]; then
  echo "Usage: $0 <host> <port> <username> <password> <directory to clear>"
  exit 1
fi

# Assign arguments to variables
HOST=$1
PORT=$2
USER=$3
PASS=$4
DIR=$5

lftp -u $USER,$PASS -p $PORT ftps://$HOST << EOF

set ssl:verify-certificate no
cd $DIR && ls && cd ..
bye
EOF