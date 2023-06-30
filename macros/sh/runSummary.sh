#!/bin/bash

#####
# Input
###
INPUTARRAY=("$@")

BINNAME=${INPUTARRAY[0]}
BINNDIM=${INPUTARRAY[1]}
CUTINFO=${INPUTARRAY[2]}
WHATRUN=${INPUTARRAY[3]}

if [[ -z $BINNAME ]]; then
    cat ScriptHelp.sh
    exit
fi

#####
# Main
###