#!/bin/bash

#####
# Input
###

INPUTARRAY=("$@")

BINNAME=${INPUTARRAY[0]}
BINNDIM=${INPUTARRAY[1]}
CUTINFO=${INPUTARRAY[2]}
WHATRUN=${INPUTARRAY[3]}

if [[ -z $BINNAME ]]; then
    cat ScriptHelp.sh
    exit
fi

#####
# Main
###

## X-axis dependency
CORR_XAXIS=('')
if [[ $CUTINFO == *"Zx"* ]]; then
    echo "Using only Zh as x-axis"
    # CORR_XAXIS=('Zx')
elif [[ $CUTINFO == *"Px"* ]]; then
    echo "Using only Pt2 as x-axis"
    # CORR_XAXIS=('Px')
else
    echo "Using Zh and Pt2 as x-axis"
    CORR_XAXIS=('_Zx' '_Px')
fi

FITMETH=('')
if [[ $CUTINFO == *"AllFit"* ]]; then
    echo "Running over all fit methods (Full, Fold, LR, Shift)"
    FITMETH=('_Ff' '_Fd' '_LR_Right' '_LR_Left' '_Sh')

    if [[ $CUTINFO == *"_AllFit"* ]]; then
        CUTINFO=${CUTINFO/_AllFit/}
    else
        CUTINFO=${CUTINFO/AllFit/}
    fi
elif [[ $CUTINFO != *"Ff"* && $CUTINFO != *"Fd"* && $CUTINFO != *"LR"* && $CUTINFO != *"Sh"* ]]; then
    echo "No fit method defined. Use: Ff, Fd, LR_Right, LR_Left, Sh or AllFit."
    exit
fi

if [[ $WHATRUN != *"D"* ]]; then
    for m in "${FITMETH[@]}"; do
        for x in "${CORR_XAXIS[@]}"; do
            THIS_CUT="${CUTINFO}${x}${m}"

            echo "" ; echo "Running ${THIS_CUT}" ; echo "" ; echo ""

            if [[ $WHATRUN == *"F"* || $WHATRUN == "" ]]; then
                ./FitCrossSection.sh DS ${BINNAME} ${BINNDIM} ${THIS_CUT}
                ./FitCrossSection.sh Fe ${BINNAME} ${BINNDIM} ${THIS_CUT}
                ./FitCrossSection.sh C  ${BINNAME} ${BINNDIM} ${THIS_CUT}
                ./FitCrossSection.sh Pb ${BINNAME} ${BINNDIM} ${THIS_CUT}
            fi

            if [[ $WHATRUN == *"S"* || $WHATRUN == "" ]]; then
                # ${CUTINFO/XX/} removes "XX" so that summary plots work!
                THIS_CUT=${THIS_CUT/-O/}
                THIS_CUT=${THIS_CUT/-A/}
                python Summary_ParametersNorm.py  -D ${BINNAME}_${BINNDIM} -i ${THIS_CUT} -J -s
                python Summary_ParametersNorm.py  -D ${BINNAME}_${BINNDIM} -i ${THIS_CUT} -J -a
                python Summary_ParametersRatio.py -D ${BINNAME}_${BINNDIM} -i ${THIS_CUT} -J
            fi
        done
    done
fi

if [[ ${#FITMETH[@]} -eq 5 || $WHATRUN == *"D"* ]]; then
    echo "" ; echo "Running summary with different fit methods" ; echo "" ; echo ""
    CUTINFO=${CUTINFO/-O/}
    CUTINFO=${CUTINFO/-A/}
    for x in "${CORR_XAXIS[@]}"; do
        python Summary_ParNorm_DiffFit.py  -D DFe_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J
        python Summary_ParNorm_DiffFit.py  -D DC_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J
        python Summary_ParNorm_DiffFit.py  -D DPb_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J

        python Summary_ParNorm_DiffFit.py  -D Fe_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J
        python Summary_ParRatio_DiffFit.py -D Fe_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J

        python Summary_ParNorm_DiffFit.py  -D C_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J
        python Summary_ParRatio_DiffFit.py -D C_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J

        python Summary_ParNorm_DiffFit.py  -D Pb_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J
        python Summary_ParRatio_DiffFit.py -D Pb_${BINNAME}_${BINNDIM} -i ${CUTINFO}${x} -J
    done
fi
