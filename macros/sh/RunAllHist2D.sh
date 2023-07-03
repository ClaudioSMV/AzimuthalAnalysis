#!/bin/bash

#####
# Input
###

INPUTARRAY=("$@")

METNAME=${INPUTARRAY[0]}
CUTINFO=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}

if [[ -z $METNAME ]]; then # empty string
    echo "Choose one method for 2D hists"; # : DeltaSector, CherenkovCounter
    cat ScriptHelp.sh
    exit
fi

#####
# Main
###

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
