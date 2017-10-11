#!/bin/bash

rm temp-pass-fail.txt
rm pass-fail.txt

for round in `seq $1`
do
  echo "Performing test number: $round"
  ./bmi-uat.py --run prb-bmi-dev-import-rm-test 2>&1 >> temp-pass-fail.txt
done

cat temp-pass-fail.txt | grep failed | grep steps > pass-fail.txt



