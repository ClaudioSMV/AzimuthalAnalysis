#!/bin/bash

##############################################################
#  ./FitCrossSection.sh <target> <binName> <binNdim>         #
#    <target> = (D, C, Fe, Pb)                               #
#    <binName>   = (0: Usual, SMoran; 1: No-integrate Zh)    #
#                                                            #
# EG: ./FitCrossSection.sh C 0 2                             #
#     ./FitCrossSection.sh Fe 1 3                            #
##############################################################

#####
# Input
###

INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}

#####
# Main
###

python PlotCorrection.py -D ${TARNAME}_${BINNAME}_${BINNDIM} -J
python PlotFit_TwoTails.py -D ${TARNAME}_${BINNAME}_${BINNDIM} -J
python PlotFit_FoldTails.py -D ${TARNAME}_${BINNAME}_${BINNDIM} -J
python GetParameterRatio.py -D ${TARNAME}_${BINNAME}_${BINNDIM} -J
python GetParameterRatio.py -D ${TARNAME}_${BINNAME}_${BINNDIM} -J -F
