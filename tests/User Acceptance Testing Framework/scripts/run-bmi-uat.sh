#!/bin/bash
       
if [ "$1" == "" ]; then

  # If empty list the test configurations
  ls config/
  
else

  # Configure the environment
  UAT_TESTS_DIR=`pwd`/config
  SCENARIO_CONFIG=config/tests-uat/$1
  export SCENARIO_CONFIG_DIR=`pwd`/${SCENARIO_CONFIG}/
  
  # Copy the configuration for the environment to test
  cp ${SCENARIO_CONFIG_DIR}bmi-config.sh $UAT_TESTS_DIR
  source config/bmi-config.sh

  # Cleanup previous test environment
  rm -rf $BDD_DIR

  # Continue configuring the environment
  source $SCENARIO_CONFIG/config
  export BDD_FEATURES_DIR=${BDD_DIR}/features/${BMI_RELEASE_NAME}
  
  # Prepare the behavior-driven tests
  mkdir --parent $BDD_FEATURES_DIR
  mkdir --parent $BDD_STEPS_DIR
  cp $SCENARIO_CONFIG/features/* $BDD_FEATURES_DIR
  cp $SCENARIO_CONFIG/steps/* $BDD_STEPS_DIR
  
  # Customize the template(s)
  source $SCENARIO_CONFIG/customize
  
  if [ ! -z "$2" ]; then
  
    # For RANDOMIZING
    $SCENARIO_CONFIG/scripts/create-random-test.sh $SCENARIO_CONFIG/scripts/    
  
    # Start the tests
    source ./scripts/source_initiate-acceptance-tests.sh $2
    
  else

    ENV_SETUP_SCRIPT=`cat ./scripts/setup_acceptance_test_scripts.cfg | grep $1 | cut -f2 -d':'`

    if [ ! -z "$ENV_SETUP_SCRIPT" ]; then

      source ./scripts/setup_acceptance_test_environment/$ENV_SETUP_SCRIPT

    else
    
      source ./scripts/setup_acceptance_test_environment/source_initiate-acceptance-tests.sh ""

    fi

  fi
    
fi

