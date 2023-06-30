#!/bin/bash

#####
# Input
###
INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}
CUTINFO=${INPUTARRAY[3]}
CUTINFO="_${CUTINFO}"

if [[ -z $TARNAME ]]; then
    cat ScriptHelp.sh
    exit
fi

#####
# Main
###
TAR_LIST=(${TARNAME})
if [[ ${TARNAME} == "S" ]]; then
    TAR_LIST=('C' 'Fe' 'Pb') # 'D'
elif [[ ${TARNAME} == "DS" ]]; then
    TAR_LIST=('DC' 'DFe' 'DPb')
elif [[ ${TARNAME} == "All" ]]; then
    TAR_LIST=('DC' 'DFe' 'DPb' 'C' 'Fe' 'Pb')
fi

#####
# Lists
###
PREV_CLIST=('Xf' 'XT' 'DS' 'BS' 'PF' 'MM' 'M2' 'FE' 'AQ' 'Pe')
CORR_CLIST=('Zx' 'Px' 'Sh')
FITS_CLIST=('Fs' 'NP')
METH_CLIST=('Fd' 'LR' 'Ff' 'Sh')
SUMM_CLIST=('MD')
# OPTS_CLIST=('-O' '-A')

ALL_CLIST=(${PREV_CLIST[@]} ${CORR_CLIST[@]} ${FITS_CLIST[@]} ${METH_CLIST[@]}\
           ${SUMM_CLIST[@]})

#####
# Cuts
###
PREV_CUT="_"
CORR_CUT="_"
FITS_CUT="_"
SUMM_CUT="_"

# Check at least one fit method is used!
GOTMETH="F"
for method in "${METH_CLIST[@]}"; do
    if [[ $CUTINFO == *$method* ]]; then
        GOTMETH="T"
    fi
done
if [[ $GOTMETH == "F" ]]; then
    echo "  No fit method provided! Use one from the list: (${METH_CLIST[*]})"
    exit
fi

# Fill cut selection
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
        # From out Fit or Fit methods
        if [[ " ${FITS_CLIST[@]} " =~ " ${cut} " || $PASS == "T" ]]; then
            FITS_CUT="${FITS_CUT}_${cut}"
            PASS="T"
        elif [[ " ${METH_CLIST[@]} " =~ " ${cut} " || $PASS == "T" ]]; then
            FITS_CUT="${FITS_CUT}_${cut}"
            PASS="T"
        fi
        # Summary
        if [[ " ${SUMM_CLIST[@]} " =~ " ${cut} " || $PASS == "T" ]]; then
            SUMM_CUT="${SUMM_CUT}_${cut}"
            PASS="T"
        fi

        CUTINFO=${CUTINFO/_${cut}/}
    fi
done

# Check options
OPTS="-J"
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

# Debug
# echo ${TAR_LIST[@]}
# echo $PREV_CUT
# echo $CORR_CUT
# echo $FITS_CUT
# echo $SUMM_CUT
# echo $OPTS

# Run python macros
cd ../
for t in "${TAR_LIST[@]}"; do
    # python PlotCorrection2.py   -D ${t}_${BINNAME}_${BINNDIM} -i $PREV_CUT\
    #                             -o $CORR_CUT $OPTS $OPTCOR
    # python PlotFit2.py          -D ${t}_${BINNAME}_${BINNDIM} -i $CORR_CUT\
    #                             -o $FITS_CUT $OPTS
    # python PlotParameters2.py   -D ${t}_${BINNAME}_${BINNDIM} -i $FITS_CUT\
    #                             -o $FITS_CUT $OPTS -t par
    python PlotParameters2.py   -D ${t}_${BINNAME}_${BINNDIM} -i $FITS_CUT\
                                -o $FITS_CUT $OPTS -t norm
done

if [[ ${TARNAME} == "All" ]]; then
    echo "  >> Getting ratios"
    STLIST=('C' 'Fe' 'Pb')
    for t in "${STLIST[@]}"; do
        python PlotParameters2.py   -D ${t}_${BINNAME}_${BINNDIM} -i $FITS_CUT\
                                    -o $FITS_CUT $OPTS -t ratio
    done
fi
