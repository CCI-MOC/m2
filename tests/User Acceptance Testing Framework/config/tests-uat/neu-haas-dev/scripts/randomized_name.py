#!/usr/bin/python

import random
import sys
import time


def main():

    min_name_length = int(sys.argv[1])
    max_name_length = int(sys.argv[2])
    
    random.seed( int(time.time() % 60) )
    
    name_length = int( random.uniform(min_name_length, max_name_length) )
    name = ""
    
    # https://wiki.outscale.net/display/DOCU/Object+Storage+Unit+%28OSU%29+FAQ
    # 3 - 255 length
    # Alphanumeric
    # _
    # - 
    # no period
    #constrained_ascii_character_set = range(45, 45 + 1) + range(48, 57 + 1) + range(65, 90 + 1) + range(95, 95 + 1) + range(97, 122 + 1)

    # Use the ASCII values of only: 0-9 : . _ - A-Z a-z
    constrained_ascii_character_set = range(45, 46 + 1) + range(48, 58 + 1) + range(65, 90 + 1) + range(95, 95 + 1) + range(97, 122 + 1)
    
    # Longer character set with special symbols
    #constrained_ascii_character_set = range(33, 33 + 1) + range(35, 38 + 1) + range(40, 95 + 1) + range(97, 126 + 1)
    #print(constrained_ascii_character_set)
    
    for position_in_name in range(1, name_length+1):
        character_index = int( random.uniform(0, len(constrained_ascii_character_set)) )
        character_ascii_value = constrained_ascii_character_set[ character_index ]
        #print( character_ascii_value )
        name = name + chr( character_ascii_value )
    print( name )



# Insures that the starting function is the main function

if __name__ == "__main__":
    main()


