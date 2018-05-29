#!/bin/bash

# Example: cat ./bdd/features/moc-0.5-release/end-to-end-acceptance-test.feature | sed -e 's/bmi-test-image/RANDOM-test-image/g' | sed -e 's/RANDOM-test-image-snapshot/RANDOM-snapshot-name/g'

SCENARIO_CONFIG_SCRIPTS_DIR=$1

RANDOM_IMAGE_NAME=`python ${SCENARIO_CONFIG_SCRIPTS_DIR}/randomized_name.py 10 15`
  
# Required or else the seed for python does not have enough seconds to work on
sleep $((1 + $RANDOM/10000))
RANDOM_SNAPSHOT_NAME=`python ${SCENARIO_CONFIG_SCRIPTS_DIR}/randomized_name.py 10 15`
  
while [[ "$RANDOM_IMAGE_NAME" == "$RANDOM_SNAPSHOT_NAME" ]]; do
  # Required or else the seed for python does not have enough seconds to work on
  sleep $((1 + $RANDOM/10000))
  RANDOM_SNAPSHOT_NAME=`python ${SCENARIO_CONFIG_SCRIPTS_DIR}/randomized_name.py 10 15`
done
	
#RANDOM_IMAGE_NAME=$1
#RANDOM_SNAPSHOT_NAME=$2

#echo ${RANDOM_IMAGE_NAME}
#echo ${RANDOM_SNAPSHOT_NAME}
 
cat $BDD_FEATURES_DIR/end-to-end-acceptance-test.feature | \
    sed -e "s/${BMI_SNAPSHOT_NAME}/${RANDOM_SNAPSHOT_NAME}/g" | \
    sed -e "s/${BMI_IMAGE_NAME}/${RANDOM_IMAGE_NAME}/g" > $BDD_FEATURES_DIR/random-end-to-end-acceptance-test.feature
    
rm $BDD_FEATURES_DIR/end-to-end-acceptance-test.feature
mv $BDD_FEATURES_DIR/random-end-to-end-acceptance-test.feature $BDD_FEATURES_DIR/end-to-end-acceptance-test.feature
