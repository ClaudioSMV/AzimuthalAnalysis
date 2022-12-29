#!/bin/bash

###################################################################
#   ./send_job_Correction.sh <target> <binName> <binNdim> <cuts>  #
#   <target> = (D, C, Fe, Pb) *D runs over solid D info           #
#   <binName> = (0: Usual, SMoran; 1: No-integrate Zh;            #
#                2: Thin Zh; 3: Thin Pt; 4: Thin Zh and Pt;       #
#                5: Thin Zh, coarse PhiPQ;                        #
#                6: Thin Zh and Pt, coarse PhiPQ)                 #
#   <binNdim> = (1: All bins regular as in Binned Acc;            #
#                2: Regular bins in Zh, Pt2, and PhiPQ;           #
#                3: Regular bins in Pt2, and PhiPQ;)              #
#   <cuts> = aa_bb_... ("Xf": X Feynman; "FE": Full error)        #
#                                                                 #
# EG: ./send_job_Correction.sh C 2 1 FE                           #
#     ./send_job_Correction.sh Fe 3 1 Xf_FE                       #
###################################################################

#####
# Input
###

INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}
CUTLIST=${INPUTARRAY[3]}

#####
# Main
###

# set env
source ~/.bashrc

# set main dirs
# REPODIR=${HOME}/work/AzimuthalAnalysis
REPODIR=/volatile/clas/claseg2/csanmart/AzimuthalAnalysis
OUTDIR=${REPODIR}/run/sh
TMPDIR=${OUTDIR}/tmp
mkdir -p ${OUTDIR} ${TMPDIR}

# setting jobname
jobname="GetCorr_${TARNAME}_${BINNAME}B${BINNDIM}"
if [[ -n $CUTLIST ]]; then
    jobname="${jobname}_${CUTLIST}"
fi
jobfile="${TMPDIR}/${jobname}.sh"

echo ${jobname}

echo "#!/bin/bash"                                                                               > ${jobfile}
echo "#SBATCH -A clas"                                                                          >> ${jobfile}
echo "#SBATCH -J ${jobname}"                                                                    >> ${jobfile}
echo "#SBATCH -o ${TMPDIR}/${jobname}.out"                                                      >> ${jobfile}
echo "#SBATCH -e ${TMPDIR}/${jobname}.err"                                                      >> ${jobfile}
echo "#SBATCH --time=4:00:00"                                                                   >> ${jobfile} # 4hrs or 15min for test
echo "#SBATCH --mem-per-cpu=1G"                                                                 >> ${jobfile}
echo "#SBATCH --mail-user=claudio.sanmartinval@gmail.com"                                       >> ${jobfile}
echo "#SBATCH --mail-type=BEGIN,END,FAIL"                                                       >> ${jobfile}
echo ""                                                                                         >> ${jobfile}
echo "source ${HOME}/.bashrc"                                                                   >> ${jobfile}
echo "cd ${REPODIR}/run"                                                                        >> ${jobfile}
if [[ ${TARNAME} == "D" ]]; then
    echo "root -l -b 'getCorrection.C(\"DC\",${BINNAME},${BINNDIM}, \"${CUTLIST}\")'"           >> ${jobfile}
    echo "root -l -b 'getCorrection.C(\"DFe\",${BINNAME},${BINNDIM}, \"${CUTLIST}\")'"          >> ${jobfile}
    echo "root -l -b 'getCorrection.C(\"DPb\",${BINNAME},${BINNDIM}, \"${CUTLIST}\")'"          >> ${jobfile}
else
    echo "root -l -b 'getCorrection.C(\"${TARNAME}\",${BINNAME},${BINNDIM}, \"${CUTLIST}\")'"   >> ${jobfile}
fi

echo "Submitting job: ${jobfile}"
sbatch ${jobfile} # submit job!
