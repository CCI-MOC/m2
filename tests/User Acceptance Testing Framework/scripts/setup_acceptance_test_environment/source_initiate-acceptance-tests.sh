#!/bin/bash

./scripts/banner "Preparing the Acceptance Test environment..."

# If it is a randomized test

if [ $1 -eq  $1 2>/dev/null ]; then
  
  TEST_NUMBER=$1

fi

# Preparing the environment

mkdir $BMI_INSTANCE_DIR
cd $BMI_INSTANCE_DIR
rm -rf ims

git clone -b dev https://github.com/CCI-MOC/ims

cd ims

# Copying the required files that will be needed for subsequent stages

cp $ACCEPTANCE_TESTS_SRC_DIR/scripts/banner .
cp $ACCEPTANCE_TESTS_SRC_DIR/scripts/perform-acceptance-tests.sh .
cp $ACCEPTANCE_TESTS_SRC_DIR/scripts/run-acceptance-tests.sh .
cp $ACCEPTANCE_TESTS_SRC_DIR/scripts/shutdown-bmi-servers.sh .
cp $ACCEPTANCE_TESTS_SRC_DIR/scripts/rollback.py .
cp $ACCEPTANCE_TESTS_SRC_DIR/scripts/return-back-to-acceptance-dir_SOURCE-THIS.sh .
cp $ACCEPTANCE_TESTS_SRC_DIR/scripts/remove-image-and-snapshots.sh .
mkdir scripts
cp $ACCEPTANCE_TESTS_SRC_DIR/scripts/cleanup-first-pass.sh scripts/
cp $SCENARIO_CONFIG_DIR/config ./config-interactive-session
cp $UAT_TESTS_DIR/bmi-config.sh .
cp $SCENARIO_CONFIG_DIR/steps/bmi_config.py .
cp -r $ACCEPTANCE_TESTS_SRC_DIR/bdd tests

if [ ! -z  "`ls $SCENARIO_CONFIG_DIR/customize-after-git-clone`" ]; then
  
  cp $SCENARIO_CONFIG_DIR/customize-after-git-clone .

  # Customize in the instance after git-cloning
  source customize-after-git-clone

fi

virtualenv . 
source bin/activate

source perform-acceptance-tests.sh $TEST_NUMBER 2> /dev/null

