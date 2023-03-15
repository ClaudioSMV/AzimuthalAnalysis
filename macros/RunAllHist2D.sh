#!/bin/bash

#########################################################
#      ./RunAllHist2D.sh <method> <cuts> <binName>      #
#  <method>  = "DeltaSector", "CherenkovCounter"        #
#  <cuts>    = Format "AA_BB_CC" (Empty is default)     #
#  <binName> = (0-10: nu; 11: xb)                       #
#                                                       #
#  "Xf": Use Xf from data; "DS": Delta Sector != 0;     #
#  "BS": rm Bad Sect;                                   #
#  "PF": Pi+ fiducial cut; "MM": Mirror Match;          #
#  "FE": Use FullError; "AQ": Acc Quality < 10%;        #
#                                                       #
#  EG: ./RunAllHist2D.sh DeltaSector Zx_FE_Fd 10        #
#      ./RunAllHist2D.sh CherenkovCounter Zx_LR 10      #
#########################################################

#####
# Input
###

INPUTARRAY=("$@")

METNAME=${INPUTARRAY[0]}
CUTINFO=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}

#####
# Main
###

if [[ -z $METNAME ]]; then # empty string
    echo "Choose one method: DeltaSector, CherenkovCounter";
    exit
fi

if [[ -n $CUTINFO ]]; then # not empty string
    CUTINFO="-i ${CUTINFO}"
fi

if [[ -n $BINNDIM ]]; then # not empty string
    BINNDIM="_${BINNDIM}"
fi


echo "" ;
echo "  Running ${METNAME}" ;

if [[ -n $CUTINFO ]]; then # not empty string
    echo "  with cuts ${CUTINFO}";
else
    echo "  without cuts";
fi
echo "" ; echo ""

# Data
python PlotHist2D_${METNAME}.py -D Fe${BINNDIM}  -J -d ${CUTINFO}
python PlotHist2D_${METNAME}.py -D C${BINNDIM}   -J -d ${CUTINFO}
python PlotHist2D_${METNAME}.py -D Pb${BINNDIM}  -J -d ${CUTINFO}
python PlotHist2D_${METNAME}.py -D DFe${BINNDIM} -J -d ${CUTINFO}
python PlotHist2D_${METNAME}.py -D DC${BINNDIM}  -J -d ${CUTINFO}
python PlotHist2D_${METNAME}.py -D DPb${BINNDIM} -J -d ${CUTINFO}

# HSim
python PlotHist2D_${METNAME}.py -D Fe${BINNDIM} -J ${CUTINFO}
python PlotHist2D_${METNAME}.py -D C${BINNDIM}  -J ${CUTINFO}
python PlotHist2D_${METNAME}.py -D Pb${BINNDIM} -J ${CUTINFO}
python PlotHist2D_${METNAME}.py -D D${BINNDIM}  -J ${CUTINFO}
