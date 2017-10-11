#!/usr/bin/python

import argparse
import os
from subprocess import check_output, CalledProcessError, STDOUT
import sys

def main(args=None):
    
    if len(args) == 0:
         args=['-h']
         
    parser = argparse.ArgumentParser(description='UAT for BMI')

    # Check has to be first in order to parse all other positional variables
    parser.add_argument('check', nargs='*',
                        help='Checks all previous test results for any failures')   
    
    parser.add_argument('clean', nargs='*',
                        help='Removes all the previous test results')   

    parser.add_argument('ls', nargs='*',
                        help='list the system configurations')    
    
    parser.add_argument('--randomize',
                        help='Number of times to run a randomized test')    
 
    parser.add_argument('--run',
                        help='Select the system configurations')
    
 
    args_parsed = parser.parse_args(args)
    
    check_args(args_parsed)
    
def check_args(args):
    
    if len(args.check) > 0 and args.check == ['ls']:
        os.system('echo')
        os.system('echo "The available configurations are: " ')
        os.system('echo')
        os.system('ls config/tests-uat')
        os.system('echo')


    if  len(args.check) > 0 and args.check == ['clean']:
        os.system('echo "Removing all previous test results..."')
        os.system('echo')
        os.system('rm -rf test-results')
          
          
    if  len(args.check) > 0 and args.check == ['check']:
        os.system('echo')
        try:
            number_of_failures_stdout = check_output('find test-results | grep FAIL | wc -l', stderr=STDOUT, shell=True)
        except CalledProcessError:
            pass
        number_of_failures = int( number_of_failures_stdout )
        if number_of_failures > 0:
            print "   Some tests failed, please fix accordingly!   "
            print ""
        else:
            print "   All tests passed!   "
            print ""
            
        
    if args.run is not None and args.randomize is not None:
        os.system('echo "Running "' + args.run + ' randomized ' + args.randomize + ' times...')
        # Store previous results in a timestamped directory
        os.system('TIMESTAMP=`date | sed -e \'s/ /_/g\' | sed \'s/__/_/g\'` && mkdir --parent test-results/$TIMESTAMP && mv test-results/*PASS test-results/$TIMESTAMP && mv test-results/*FAIL test-results/$TIMESTAMP')
        for round in range(1, (int(args.randomize) + 1) ):
            os.system('./scripts/run-bmi-uat.sh ' + args.run + ' ' + str(round) )
    elif args.run is not None:
        os.system('echo "Running "' + args.run + ' using the default configuration...')
        os.system('./scripts/run-bmi-uat.sh ' + args.run)
               
    
if __name__ == '__main__':
  main(sys.argv[1:])
  #print(sys.argv)

