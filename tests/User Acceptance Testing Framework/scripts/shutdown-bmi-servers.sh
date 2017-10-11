#!/bin/bash

#PICASSO_ID=`ps -Af | grep picasso_server | grep $HOME | cut -f6 -d' '`
#EINSTEIN_IDS=`ps -Af | grep einstein_server | grep $HOME | cut -f6 -d' '`

#PICASSO_ID=`pgrep -a picasso_server | grep pgrosu | cut -f1 -d' '`
#EINSTEIN_IDS=`pgrep -a einstein_server | grep pgrosu | cut -f1 -d' '`

PICASSO_ID=`pgrep -a picasso_server | grep $BMI_INSTANCE_DIR | cut -f1 -d' '`
EINSTEIN_IDS=`pgrep -a einstein_server | grep $BMI_INSTANCE_DIR | cut -f1 -d' '`

# If the IDs variables are not empty, then kill those processes
if [ ! -z "$PICASSO_ID" ]; then
  kill -9 $PICASSO_ID 
  #wait $PICASSO_ID 2>/dev/null
fi

if [ ! -z "$EINSTEIN_IDS" ]; then
  kill -9 $EINSTEIN_IDS 
  #wait $EINSTEIN_IDS 2>/dev/null 
fi



