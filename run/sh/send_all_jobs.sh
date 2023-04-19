#!/bin/bash

#####
# Input
###

INPUTARRAY=("$@")

USEMTHD=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
CUTLIST=${INPUTARRAY[2]}

if [[ -z $USEMTHD ]]; then
    cat ../../macros/ScriptHelp.sh
    exit
fi

#####
# Main
###

#####
# Cuts
###
ACC_CUT=""
COR_CUT=""

UND=""

### Acceptance cuts
if [[ $CUTLIST == *"Xf"* ]]; then
    ACC_CUT="${ACC_CUT}${UND}Xf"
    COR_CUT="${COR_CUT}${UND}Xf"

    CUTLIST=${CUTLIST/${UND}Xf/}
    UND="_"
fi
if [[ $CUTLIST == *"XT"* ]]; then
    ACC_CUT="${ACC_CUT}${UND}XT"
    COR_CUT="${COR_CUT}${UND}XT"

    CUTLIST=${CUTLIST/${UND}XT/}
    UND="_"
fi
if [[ $CUTLIST == *"DS"* ]]; then
    ACC_CUT="${ACC_CUT}${UND}DS"
    COR_CUT="${COR_CUT}${UND}DS"

    CUTLIST=${CUTLIST/${UND}DS/}
    UND="_"
fi
if [[ $CUTLIST == *"BS"* ]]; then
    ACC_CUT="${ACC_CUT}${UND}BS"
    COR_CUT="${COR_CUT}${UND}BS"

    CUTLIST=${CUTLIST/${UND}BS/}
    UND="_"
fi
if [[ $CUTLIST == *"PF"* ]]; then
    ACC_CUT="${ACC_CUT}${UND}PF"
    COR_CUT="${COR_CUT}${UND}PF"

    CUTLIST=${CUTLIST/${UND}PF/}
    UND="_"
fi
if [[ $CUTLIST == *"MM"* ]]; then
    ACC_CUT="${ACC_CUT}${UND}MM"
    COR_CUT="${COR_CUT}${UND}MM"

    CUTLIST=${CUTLIST/${UND}MM/}
    UND="_"
fi
if [[ $CUTLIST == *"M2"* ]]; then
    ACC_CUT="${ACC_CUT}${UND}M2"
    COR_CUT="${COR_CUT}${UND}M2"

    CUTLIST=${CUTLIST/${UND}M2/}
    UND="_"
fi

### Correction cuts
if [[ $CUTLIST == *"FE"* ]]; then
    COR_CUT="${COR_CUT}${UND}FE"

    CUTLIST=${CUTLIST/${UND}FE/}
    UND="_"
fi
if [[ $CUTLIST == *"AQ"* ]]; then
    COR_CUT="${COR_CUT}${UND}AQ"

    CUTLIST=${CUTLIST/${UND}AQ/}
    UND="_"
fi
if [[ $CUTLIST == *"Pe"* ]]; then
    COR_CUT="${COR_CUT}${UND}Pe"

    CUTLIST=${CUTLIST/${UND}Pe/}
    UND="_"
fi

if [[ -n $CUTLIST ]]; then
    echo "There are cuts not defined: ${CUTLIST}"
    exit
fi

### Send jobs!
if [[ $USEMTHD == *"Acc"* ]]; then
    ./send_job_Acceptance.sh C  ${BINNAME} ${ACC_CUT}
    ./send_job_Acceptance.sh Fe ${BINNAME} ${ACC_CUT}
    ./send_job_Acceptance.sh Pb ${BINNAME} ${ACC_CUT}
    ./send_job_Acceptance.sh D  ${BINNAME} ${ACC_CUT}
elif [[ $USEMTHD == *"Corr"* ]]; then
    ./send_job_Correction.sh C  ${BINNAME} 1 ${COR_CUT}
    ./send_job_Correction.sh Fe ${BINNAME} 1 ${COR_CUT}
    ./send_job_Correction.sh Pb ${BINNAME} 1 ${COR_CUT}
    ./send_job_Correction.sh D  ${BINNAME} 1 ${COR_CUT}
elif [[ $USEMTHD == *"Closure"* ]]; then
    ./send_job_ClosureTest.sh C  ${BINNAME} 1 50 ${COR_CUT}
    ./send_job_ClosureTest.sh Fe ${BINNAME} 1 50 ${COR_CUT}
    ./send_job_ClosureTest.sh Pb ${BINNAME} 1 50 ${COR_CUT}
    ./send_job_ClosureTest.sh D  ${BINNAME} 1 50 ${COR_CUT}
else
    echo "No correct method found! Write it correctly!"
    exit
fi
