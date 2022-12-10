#!/bin/bash

#########################################################################
#          ./RunAllFitAndSummary.sh <binName> <binNdim> <cuts>          #
#  <binName> = (0: Usual, SMoran; 1: No-integrate Zh;                   #
#               2: Thin Zh; 3: Thin Pt; 4: Thin Zh and Pt;              #
#               5: Thin Zh, coarse PhiPQ;                               #
#               6: Thin Zh and Pt, coarse PhiPQ)                        #
#  <binNdim> = (1: All bins regular as in Binned Acc;                   #
#               2: Regular bins in Zh, Pt2, and PhiPQ;                  #
#               3: Regular bins in Pt2, and PhiPQ;)                     #
#  <cuts>    = Format "AA_BB_CC" (Empty is default)                     #
#  "Xf": Use Xf from data; "FE": Use FullError; "Zx": x-axis is Zh;     #
#  "Px": x-axis is Pt2; "Fd": Fit uses Fold; "LR": Fit uses both tails; #
#  "MD": Mix D info is ratios;                                          #
#                                                                       #
#  EG: ./FitCrossSection.sh 0 2 Zx_FE_Fd                                #
#      ./FitCrossSection.sh 1 3 Zx_LR                                   #
#########################################################################

#####
# Input
###

INPUTARRAY=("$@")

BINNAME=${INPUTARRAY[0]}
BINNDIM=${INPUTARRAY[1]}
CUTINFO=${INPUTARRAY[2]}

#####
# Main
###

./FitCrossSection.sh DS ${BINNAME} ${BINNDIM} ${CUTINFO}
./FitCrossSection.sh Fe ${BINNAME} ${BINNDIM} ${CUTINFO}
./FitCrossSection.sh C  ${BINNAME} ${BINNDIM} ${CUTINFO}
./FitCrossSection.sh Pb ${BINNAME} ${BINNDIM} ${CUTINFO}

python Summary_ParametersNorm.py  -D ${BINNAME}_${BINNDIM} -i ${CUTINFO} -J -s
python Summary_ParametersRatio.py -D ${BINNAME}_${BINNDIM} -i ${CUTINFO} -J
