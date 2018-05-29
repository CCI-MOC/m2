#!/bin/bash

./banner "Preparing the BMI environment..."

# If it is a randomized test

if [ $1 -eq  $1 2>/dev/null ]; then
  
  TEST_NUMBER=$1

fi

# Install the libraries

pip install -e .
pip install python-cephlibs
pip install behave

cd $BMI_INSTANCE_DIR/ims

# Kill all Picasso and Einstein processes
./shutdown-bmi-servers.sh

# Start the servers
bin/picasso_server & 
bin/einstein_server &
sleep 1

./banner "Starting the Acceptance Tests..."

./run-acceptance-tests.sh | tee acceptance_tests_results.txt

./banner "Completion of Acceptance Tests!"

pass_fail=$((`cat acceptance_tests_results.txt  | cut -f2 -d',' | grep failed | cut -f2 -d' ' | sed ':a;N;$!ba;s/\n/+/g'`))

if (( $pass_fail > 0 )); then
  echo "  !!! BMI failed $pass_fail times the acceptance criteria - please fix accordingly. !!!"
  echo ""
  export PASS_FAIL=FAIL
else
  echo "  === BMI passed the acceptance criteria! === "
  echo ""
  export PASS_FAIL=PASS
fi

./shutdown-bmi-servers.sh && source return-back-to-acceptance-dir_SOURCE-THIS.sh $TEST_NUMBER $PASS_FAIL  


