#!/bin/bash

# Kill script if any macro ends in an error
set -e

##########################################################################################
##                                    Input and help                                    ##
##########################################################################################
INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}
BINVARS=${INPUTARRAY[3]}
CUTINFO=${INPUTARRAY[4]}
FITMETH=${INPUTARRAY[5]}

if [[ -z $TARNAME || ($TARNAME == "-h") ]]; then
    cat help_script.sh
    exit
fi

TAR_LIST=(${TARNAME})
SUMMARY_SET=('L' 'S')
if [[ ${TARNAME} == "S" || ${TARNAME} == "Solid" ]]; then
    TAR_LIST=('C' 'Fe' 'Pb') # 'D'
    SUMMARY_SET=('S')
elif [[ ${TARNAME} == "DS" || ${TARNAME} == "Liquid" ]]; then
    TAR_LIST=('DC' 'DFe' 'DPb')
    SUMMARY_SET=('L')
elif [[ ${TARNAME} == "All" ]]; then
    TAR_LIST=('DC' 'DFe' 'DPb' 'C' 'Fe' 'Pb')
else
    SUMMARY_SET=()
fi

OPTS=""
if [[ $CUTINFO == *"-O"* ]]; then # Overwrite
    OPTS="${OPTS} -O"
    CUTINFO=${CUTINFO/-O/}
fi
OPTS_CORR="" # Save ALL correction methods (Reco, RecoMtch_mc, RecoMtch_re)
if [[ $CUTINFO == *"-A"* ]]; then
    OPTS_CORR="-A"
    CUTINFO=${CUTINFO/-A/}
fi
if [[ $FITMETH == "Sh" ]]; then
    OPTS_CORR="${OPTS_CORR} -s"
fi

##########################################################################################
##                                         Main                                         ##
##########################################################################################
cd ../
for t in "${TAR_LIST[@]}"; do
    echo -e "  >> Getting parameters of $t target\n"
    # echo "Plot_Correction.py   -D ${t}_${BINNAME}_${BINNDIM} -B $BINVARS -C $CUTINFO $OPTS $OPTS_CORR"
    # echo "Plot_Fit.py          -D ${t}_${BINNAME}_${BINNDIM} -B $BINVARS -C $CUTINFO $OPTS -F $FITMETH"
    # echo "Get_Parameters.py    -D ${t}_${BINNAME}_${BINNDIM} -B $BINVARS -C $CUTINFO $OPTS -F $FITMETH"

    python Plot_Correction.py   -D ${t}_${BINNAME}_${BINNDIM} -B $BINVARS -C $CUTINFO\
                                $OPTS $OPTS_CORR
    python Plot_Fit.py          -D ${t}_${BINNAME}_${BINNDIM} -B $BINVARS -C $CUTINFO\
                                $OPTS -F $FITMETH
    python Get_Parameters.py    -D ${t}_${BINNAME}_${BINNDIM} -B $BINVARS -C $CUTINFO\
                                $OPTS -F $FITMETH
done

for SET in "${SUMMARY_SET[@]}"; do
    echo -e "  >> Getting asymmetry summary plots\n"
    # echo "Plot_Summary.py -D ${BINNAME}_${BINNDIM} -B $BINVARS -C $CUTINFO -F $FITMETH -S $SET"

    python Plot_Summary.py -D ${BINNAME}_${BINNDIM} -B $BINVARS -C $CUTINFO -F $FITMETH\
                            -S $SET
done
