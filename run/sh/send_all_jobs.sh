#!/bin/bash

###########################################################
#      ./send_all_jobs.sh <method> <binName> <cuts>       #
#    <method> = (Acceptance, Correction, Closure Test)    #
#    <binName> = (0-10: uses Nu; 11: uses Xb              #
#    <cuts> = aa_bb_... ("Xf": X Feynman;)                #
#                                                         #
# EG: ./send_all_jobs.sh Acceptance 10                    #
#     ./send_all_jobs.sh Correction 11 Xf                 #
###########################################################

#####
# Input
###

INPUTARRAY=("$@")

USEMTHD=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
CUTLIST=${INPUTARRAY[2]}

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

if [[ -n $CUTLIST ]]; then
    echo "There are cuts not defined: ${CUTLIST}"
else
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
fi

