
# Check that the first parameter is not empty, which would indicate a randomized test
# Otherwise exit the interactive session
if [ ! -z $1 ]; then
	if [ $1 -eq  $1 2>/dev/null ]; then
	 
	  TEST_NUMBER=$1
	  PASS_FAIL=$2
	  
	  #echo $ACCEPTANCE_TESTS_SRC_DIR
	  
	  if [ ! -z  "$ACCEPTANCE_TESTS_SRC_DIR" ]; then
	    mkdir --parent $ACCEPTANCE_TESTS_SRC_DIR/test-results/${TEST_NUMBER}-${PASS_FAIL}
	    cp -r ./tests/bdd/* $ACCEPTANCE_TESTS_SRC_DIR/test-results/${TEST_NUMBER}-${PASS_FAIL}
	  fi
	fi
fi

# Deactivate virtualenv
deactivate

if [ ! -z  "$ACCEPTANCE_TESTS_SRC_DIR" ]; then
  cd $ACCEPTANCE_TESTS_SRC_DIR
else
  cd $ORIG_DIR
fi
