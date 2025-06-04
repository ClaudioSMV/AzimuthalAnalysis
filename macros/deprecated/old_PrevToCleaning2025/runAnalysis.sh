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
BININFO=${INPUTARRAY[3]}
CUTINFO=${INPUTARRAY[4]}
CUTINFO="_${CUTINFO}"

if [[ -z $TARNAME || ($TARNAME == "-h") ]]; then
    cat help_script.sh
    exit
fi

TAR_LIST=(${TARNAME})
SUMMARY_SET=('sl' 'lq')
if [[ ${TARNAME} == "S" || ${TARNAME} == "Solid" ]]; then
    TAR_LIST=('C' 'Fe' 'Pb') # 'D'
    SUMMARY_SET=('sl')
elif [[ ${TARNAME} == "DS" || ${TARNAME} == "Liquid" ]]; then
    TAR_LIST=('DC' 'DFe' 'DPb')
    SUMMARY_SET=('lq')
elif [[ ${TARNAME} == "All" ]]; then
    TAR_LIST=('DC' 'DFe' 'DPb' 'C' 'Fe' 'Pb')
else
    SUMMARY_SET=()
fi

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

################################################################################
##                                   Debug                                    ##
################################################################################
# echo ${TAR_LIST[@]}
# echo $OPTS

################################################################################
##                                    Main                                    ##
################################################################################
cd ../
for t in "${TAR_LIST[@]}"; do
    echo -e "  >> Getting parameters of $t target\n"
    python Plot_Correction.py   -D ${t}_${BINNAME}_${BINNDIM} -i $CUTINFO\
                                $OPTS $OPTCOR -b $BININFO
    python Plot_Fit.py          -D ${t}_${BINNAME}_${BINNDIM} -i $CUTINFO\
                                $OPTS -b $BININFO
    python Get_Parameters.py    -D ${t}_${BINNAME}_${BINNDIM} -i $CUTINFO\
                                $OPTS -b $BININFO
done

for target_set in "${SUMMARY_SET[@]}"; do
    echo -e "  >> Getting asymmetry summary plots\n"
    python Plot_Summary.py -D ${BINNAME}_${BINNDIM} -i ${CUTINFO}_${target_set}\
                            $OPTS -b $BININFO
done

if [[ ${TARNAME} == "All" ]]; then
    echo -e "  >> Getting ratio summary plots\n"
    python Plot_Summary.py -D ${BINNAME}_${BINNDIM} -i ${CUTINFO}_sl\
                            $OPTS -b $BININFO -r
fi
