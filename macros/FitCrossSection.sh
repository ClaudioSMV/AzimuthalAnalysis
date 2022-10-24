#!/bin/bash

###############################################################
#  ./FitCrossSection.sh <target> <binName> <binNdim> <x-axis> #
#  <target>  = (D, C, Fe, Pb, DS) (DS; Split D in solid targ) #
#  <binName> = (0: Usual, SMoran; 1: No-integrate Zh)         #
#  <x-axis>  = (P, Z) (Empty is default)                      #
#                                                             #
# EG: ./FitCrossSection.sh C 0 2                              #
#     ./FitCrossSection.sh Fe 1 3                             #
###############################################################

#####
# Input
###

INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}
AXISOPT=${INPUTARRAY[3]}

#####
# Main
###
TAR_LIST=(${TARNAME})
if [[ ${TARNAME} == "DS" ]]; then
    TAR_LIST=('DC' 'DFe' 'DPb')
fi

AXSNAME=""
if [[ -n ${AXISOPT} ]]; then
    AXSNAME=_${AXISOPT}
    AXISOPT=-${AXISOPT}
fi

for t in "${TAR_LIST[@]}"; do
    python PlotCorrection.py -D ${t}_${BINNAME}_${BINNDIM} -J ${AXISOPT}
    # python PlotFit_TwoTails.py -D ${t}_${BINNAME}_${BINNDIM} -J
    python PlotFit_FoldTails.py -D ${t}_${BINNAME}_${BINNDIM}${AXSNAME} -J
    # python GetParameters.py -D ${t}_${BINNAME}_${BINNDIM} -J
    # python GetParameters.py -D ${t}_${BINNAME}_${BINNDIM} -J -Z
    python GetParameters.py -D ${t}_${BINNAME}_${BINNDIM}${AXSNAME} -J -F
    python GetParametersNorm.py -D ${t}_${BINNAME}_${BINNDIM}${AXSNAME} -J -F
    # python GetParameters.py -D ${t}_${BINNAME}_${BINNDIM} -J -F -Z
    # python GetParameterRatio.py -D ${t}_${BINNAME}_${BINNDIM} -J
    python GetParameterRatio.py -D ${t}_${BINNAME}_${BINNDIM}${AXSNAME} -J -F
    # python GetParameterRatio.py -D ${t}_${BINNAME}_${BINNDIM} -J -F -m
done
