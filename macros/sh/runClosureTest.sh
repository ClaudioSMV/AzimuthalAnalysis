#!/bin/bash

# Kill script if any macro ends in an error
set -e

################################################################################
##                               Input and help                               ##
################################################################################
INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}
CUTINFO=${INPUTARRAY[3]}
CUTINFO="_${CUTINFO}"
ACCFRAC=${INPUTARRAY[4]}

if [[ -z $TARNAME || ($TARNAME == "-h") ]]; then
    cat help_script.sh
    exit
fi

TAR_LIST=(${TARNAME})
if [[ ${TARNAME} == "All" ]]; then
    TAR_LIST=('D' 'C' 'Fe' 'Pb')
fi

################################################################################
##                                 Cut lists                                  ##
################################################################################
PREV_CLIST=('Xf' 'XT' 'DS' 'BS' 'PF' 'MM' 'M2' 'FE' 'AQ' 'Pe')
CORR_CLIST=('Zx' 'Px') # 'Sh')
# OPTS_CLIST=('-O' '-A')

ALL_CLIST=(${PREV_CLIST[@]} ${CORR_CLIST[@]})

PREV_CUT="_"
CORR_CUT="_"

################################################################################
##                                 Exit zone                                  ##
################################################################################
# Fraction of acceptance must be given
if [[ -z $ACCFRAC ]]; then
    echo "  No acceptance fraction number given! Try 50, for instance."
    exit
fi

################################################################################
##                            Fill cut selections                             ##
################################################################################
for cut in "${ALL_CLIST[@]}"; do
    PASS="F"
    # Check cut was called
    if [[ $CUTINFO == *$cut* ]]; then
        # Before Corrected
        if [[ " ${PREV_CLIST[@]} " =~ " ${cut} " || $PASS == "T" ]]; then
            PREV_CUT="${PREV_CUT}_${cut}"
            PASS="T"
        fi
        # From out Corrected
        if [[ " ${CORR_CLIST[@]} " =~ " ${cut} " || $PASS == "T" ]]; then
            CORR_CUT="${CORR_CUT}_${cut}"
            PASS="T"
        fi

        CUTINFO=${CUTINFO/_${cut}/}
    fi
done
# Check options
OPTS="-J -f $ACCFRAC"
# Overwrite
if [[ $CUTINFO == *"-O"* ]]; then
    OPTS="${OPTS} -O"
    CUTINFO=${CUTINFO/-O/}
fi
# Draw ALL acceptance/correction types (Reco, RecoMtch_mc, RecoMtch_re)
OPTCOR=""
if [[ $CUTINFO == *"-A"* ]]; then
    OPTCOR="-A"
    CUTINFO=${CUTINFO/-A/}
fi

if [[ -n $CUTINFO ]]; then
    echo "  There are cuts not defined or repeated: ${CUTINFO}"
    exit
fi

################################################################################
##                                   Debug                                    ##
################################################################################
# # Debug
# echo ${TAR_LIST[@]}
# echo $PREV_CUT
# echo $CORR_CUT
# echo $OPTS

################################################################################
##                                    Main                                    ##
################################################################################
cd ../
for t in "${TAR_LIST[@]}"; do
    echo -e "  >> Running over $t target\n"
    python Plot_ClosureTest.py  -D ${t}_${BINNAME}_${BINNDIM} -i $PREV_CUT\
                                -o $CORR_CUT $OPTS $OPTCOR
done
