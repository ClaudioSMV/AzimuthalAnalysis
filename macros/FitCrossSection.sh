#!/bin/bash

############################################################################
#  ./FitCrossSection.sh <target> <binName> <binNdim> <x-axis> <ErrorType>  #
#     <target>  = (D, C, Fe, Pb, DS) (DS; Split D in solid targ)           #
#     <binName> = (0: Usual, SMoran; 1: No-integrate Zh;                   #
#                  2: Thin Zh;)                                            #
#     <binNdim> = (1: All bins regular as in Binned Acc;                   #
#                  2: Regular bins in Zh, Pt2, and PhiPQ;                  #
#                  3: Regular bins in Pt2, and PhiPQ;)                     #
#     <x-axis>  = (P, Z) (Empty is default)                                #
#     <ErrorType> = (FULL: Use FullError; empty (DEFAULT); )               #
#                                                                          #
# EG: ./FitCrossSection.sh C 0 2 Z EVT                                     #
#     ./FitCrossSection.sh Fe 1 3 P FULL                                   #
############################################################################

#####
# Input
###

INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}
AXISOPT=${INPUTARRAY[3]}
ERRORTP=${INPUTARRAY[4]}

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

if [[ ${ERRORTP} == "FULL" ]]; then
    ERRORTP="-e"
else
    ERRORTP=""
fi

for t in "${TAR_LIST[@]}"; do
    python PlotCorrection.py    -D ${t}_${BINNAME}_${BINNDIM}           -J ${AXISOPT} ${ERRORTP}
    # python PlotFit_TwoTails.py  -D ${t}_${BINNAME}_${BINNDIM}           -J
    python PlotFit_FoldTails.py -D ${t}_${BINNAME}_${BINNDIM}${AXSNAME} -J ${ERRORTP}
    # python GetParameters.py     -D ${t}_${BINNAME}_${BINNDIM}           -J
    # python GetParameters.py     -D ${t}_${BINNAME}_${BINNDIM}           -J -Z
    ### python GetParameters.py   -D ${t}_${BINNAME}_${BINNDIM}${AXSNAME} -J -F ${ERRORTP}
    python GetParametersNorm.py -D ${t}_${BINNAME}_${BINNDIM}${AXSNAME} -J -F ${ERRORTP}
    # python GetParameters.py     -D ${t}_${BINNAME}_${BINNDIM}           -J -F -Z
    # python GetParameterRatio.py -D ${t}_${BINNAME}_${BINNDIM}           -J
    python GetParameterRatio.py -D ${t}_${BINNAME}_${BINNDIM}${AXSNAME} -J -F ${ERRORTP}
    # python GetParameterRatio.py -D ${t}_${BINNAME}_${BINNDIM}           -J -F -m
done
