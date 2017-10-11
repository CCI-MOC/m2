#!/bin/bash

if [ "$1" == "" ]; then

  echo ""
  echo "Please choose one of the following configurations based on your environment: "
  echo ""
  ls scripts/prepare-environments | sed 's/\.sh//g'
  echo ""

elif [ ! -z "$1" ]; then

  if [ -z "`ls scripts/prepare-environments/${1}.sh`" ]; then
    
    echo "a"
    echo "You selected a configuration that is not available.  Please make sure the configuration exists, or create one."
    echo ""
    echo "The current available configurations are:"
    echo ""
    ls scripts/prepare-environments | sed 's/\.sh//g'
    echo ""
  else 
     scripts/prepare-environments/${1}.sh 
  fi

fi
