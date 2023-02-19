#!/bin/bash

#########################################################################
#       ./RunAllClosureTest.sh <binName> <binNdim> <cuts> <fracAcc>     #
#  <binName> = (0: Usual, SMoran; 1: No-integrate Zh;                   #
#               2: Thin Zh; 3: Thin Pt; 4: Thin Zh and Pt;              #
#               5: Thin Zh, coarse PhiPQ;                               #
#               6: Thin Zh and Pt, coarse PhiPQ)                        #
#  <binNdim> = (1: All bins regular as in Binned Acc;                   #
#               2: Regular bins in Zh, Pt2, and PhiPQ;                  #
#               3: Regular bins in Pt2, and PhiPQ;)                     #
#  <cuts>    = Format "AA_BB_CC" (Empty is default)                     #
#  "Xf": Use Xf from data; "DS": Delta Sector != 0; "BS": rm Bad Sect;  #
#  "PF": Pi+ fiducial cut;                                              #
#  "FE": Use FullError;                                                 #
#  "Zx": x-axis is Zh; "Px": x-axis is Pt2;                             #
#  <fracAcc> = Fraction of stats used in calculation of Acc (50, 70...) #
#                                                                       #
#  EG: ./RunAllClosureTest.sh 0 2 Zx_FE 50                              #
#      ./RunAllClosureTest.sh 1 3 Px 70                                 #
#########################################################################

#####
# Input
###

INPUTARRAY=("$@")

BINNAME=${INPUTARRAY[0]}
BINNDIM=${INPUTARRAY[1]}
CUTINFO=${INPUTARRAY[2]}
FRACACC=${INPUTARRAY[3]}


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
if [[ $CUTINFO == *"FE"* ]]; then
    PREV_CUT="${PREV_CUT}_FE"
    CORR_CUT="${CORR_CUT}_FE"
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
python PlotClosureTest.py -D C_${BINNAME}_${BINNDIM} -i ${PREV_CUT} -o ${CORR_CUT} -f ${FRACACC} -J
python PlotClosureTest.py -D Pb_${BINNAME}_${BINNDIM} -i ${PREV_CUT} -o ${CORR_CUT} -f ${FRACACC} -J
python PlotClosureTest.py -D D_${BINNAME}_${BINNDIM} -i ${PREV_CUT} -o ${CORR_CUT} -f ${FRACACC} -J

