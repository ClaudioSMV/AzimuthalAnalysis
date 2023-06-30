#!/bin/bash

#####
# Input
###

INPUTARRAY=("$@")

BINNAME=${INPUTARRAY[0]}
BINNDIM=${INPUTARRAY[1]}
CUTINFO=${INPUTARRAY[2]}
FRACACC=${INPUTARRAY[3]}

if [[ -z $BINNAME ]]; then
    cat ScriptHelp.sh
    exit
fi


#####
# Cuts
###
PREV_CUT="_"
CORR_CUT="_"

### Before Corrected
if [[ $CUTINFO == *"Xf"* ]]; then
    PREV_CUT="${PREV_CUT}_Xf"
    CORR_CUT="${CORR_CUT}_Xf"
fi
if [[ $CUTINFO == *"DS"* ]]; then
    PREV_CUT="${PREV_CUT}_DS"
    CORR_CUT="${CORR_CUT}_DS"
fi
if [[ $CUTINFO == *"BS"* ]]; then
    PREV_CUT="${PREV_CUT}_BS"
    CORR_CUT="${CORR_CUT}_BS"
fi
if [[ $CUTINFO == *"PF"* ]]; then
    PREV_CUT="${PREV_CUT}_PF"
    CORR_CUT="${CORR_CUT}_PF"
fi
if [[ $CUTINFO == *"MM"* ]]; then
    PREV_CUT="${PREV_CUT}_MM"
    CORR_CUT="${CORR_CUT}_MM"
fi
if [[ $CUTINFO == *"FE"* ]]; then
    PREV_CUT="${PREV_CUT}_FE"
    CORR_CUT="${CORR_CUT}_FE"
fi
if [[ $CUTINFO == *"AQ"* ]]; then
    PREV_CUT="${PREV_CUT}_AQ"
    CORR_CUT="${CORR_CUT}_AQ"
fi

### From Corrected
if [[ $CUTINFO == *"Zx"* ]]; then
    CORR_CUT="${CORR_CUT}_Zx"
elif [[ $CUTINFO == *"Px"* ]]; then
    CORR_CUT="${CORR_CUT}_Px"
else
    echo "Remember to select Zh or Pt2 as x-axis (Zx or Px)"
    exit
fi


#####
# Main
###

python PlotClosureTest.py -D Fe_${BINNAME}_${BINNDIM} -i ${PREV_CUT} -o ${CORR_CUT} -f ${FRACACC} -J
python PlotClosureTest.py -D C_${BINNAME}_${BINNDIM}  -i ${PREV_CUT} -o ${CORR_CUT} -f ${FRACACC} -J
python PlotClosureTest.py -D Pb_${BINNAME}_${BINNDIM} -i ${PREV_CUT} -o ${CORR_CUT} -f ${FRACACC} -J
python PlotClosureTest.py -D D_${BINNAME}_${BINNDIM}  -i ${PREV_CUT} -o ${CORR_CUT} -f ${FRACACC} -J

