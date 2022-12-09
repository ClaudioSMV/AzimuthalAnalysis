#!/bin/bash

##############################################################
#     ./send_job_Acceptance.sh <target> <binName> <cuts>     #
#    <target> = (D, C, Fe, Pb)                               #
#    <binName> = (0: Usual, SMoran; 1: No-integrate Zh;      #
#                 2: Thin Zh; 3: Thin Pt; 4: Thin Zh and Pt; #
#                 5: Thin Zh, coarse PhiPQ;                  #
#                 6: Thin Zh and Pt, coarse PhiPQ)           #
#    <cuts> = aa_bb_... ("Xf": X Feynman;)                   #
#                                                            #
# EG: ./send_job_Acceptance.sh C 2                           #
#     ./send_job_Acceptance.sh Fe 3 Xf                       #
##############################################################

#####
# Input
###

INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
CUTLIST=${INPUTARRAY[2]}

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
jobname="GetAcc_${TARNAME}_${BINNAME}B"
if [[ -n $CUTLIST ]]; then
    jobname="${jobname}_${CUTLIST}"
fi
jobfile="${TMPDIR}/${jobname}.sh"

echo ${jobname}

echo "#!/bin/bash"                                                               > ${jobfile}
echo "#SBATCH -A clas"                                                          >> ${jobfile}
echo "#SBATCH -J ${jobname}"                                                    >> ${jobfile}
echo "#SBATCH -o ${TMPDIR}/${jobname}.out"                                      >> ${jobfile}
echo "#SBATCH -e ${TMPDIR}/${jobname}.err"                                      >> ${jobfile}
echo "#SBATCH --time=3:00:00"                                                   >> ${jobfile} # 4hrs or 15min for test
echo "#SBATCH --mem-per-cpu=500M"                                               >> ${jobfile}
echo "#SBATCH --mail-user=claudio.sanmartinval@gmail.com"                       >> ${jobfile}
echo "#SBATCH --mail-type=BEGIN,END,FAIL"                                       >> ${jobfile}
echo ""                                                                         >> ${jobfile}
echo "source ${HOME}/.bashrc"                                                   >> ${jobfile}
echo "cd ${REPODIR}/run"                                                        >> ${jobfile}
echo "root -l -b 'getAcceptance.C(\"${TARNAME}\",${BINNAME},\"${CUTLIST}\")'"   >> ${jobfile}

echo "Submitting job: ${jobfile}"
sbatch ${jobfile} # submit job!
