#!/bin/bash

#########################################################################
#       ./RunAllFitAndSummary.sh <binName> <binNdim> <cuts> <run>       #
#  <binName> = (0: Usual, SMoran; 1: No-integrate Zh;                   #
#               2: Thin Zh; 3: Thin Pt; 4: Thin Zh and Pt;              #
#               5: Thin Zh, coarse PhiPQ;                               #
#               6: Thin Zh and Pt, coarse PhiPQ)                        #
#  <binNdim> = (1: All bins regular as in Binned Acc;                   #
#               2: Regular bins in Zh, Pt2, and PhiPQ;                  #
#               3: Regular bins in Pt2, and PhiPQ;)                     #
#  <cuts>    = Format "AA_BB_CC" (Empty is default)                     #
#  ** AllFit runs over all 4 fit methods                                #
#                                                                       #
#  "Xf": Use Xf from data; "DS": Delta Sector != 0; "BS": rm Bad Sect;  #
#  "PF": Pi+ fiducial cut; "MM": Mirror Match;                          #
#  "FE": Use FullError; "AQ": Acc Quality < 10%;                        #
#  "Zx": x-axis is Zh; "Px": x-axis is Pt2; "Sh": Shift reco distrib    #
#  "Fs": Add Sin(x) term in fit;                                        #
#  "Fd": Fit uses Fold; "LR": Fit uses both tails; "Ff": Full fit       #
#  "Left" or "Right" if "LR" is under use;                              #
#  "MD": Mix D info is ratios;                                          #
#        Add option: -O: To Overwrite files if created                  #
#  <run>     = "" (empty): Both Fit and Summary; "F": Get Fits;         #
#              "S": Only get Summary; "D": Get Diff summary;            #
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
WHATRUN=${INPUTARRAY[3]}

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
    CUTINFO=${CUTINFO/AllFit/}
elif [[ $CUTINFO != *"Ff"* && $CUTINFO != *"Fd"* && $CUTINFO != *"LR"* && $CUTINFO != *"Sh"* ]]; then
    echo "No fit method defined. Use: Ff, Fd, LR_Right, LR_Left, Sh or AllFit."
    exit
fi

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

if [[ ${#FITMETH[@]} -eq 5 || $WHATRUN == *"D"* ]]; then
    echo "" ; echo "Running summary with different fit methods" ; echo "" ; echo ""
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
