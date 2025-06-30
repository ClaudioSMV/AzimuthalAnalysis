#!/bin/bash

#####
# Input
###

INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
CUTLIST=${INPUTARRAY[2]}

if [[ -z $TARNAME ]]; then
    cat help_send.sh
    exit
fi

#####
# Main
###

# set env
source ~/.bashrc

# set main dirs
SCRIPTDIR=${HOME}/work/AzimuthalAnalysis/run
# JOBDIR=/volatile/clas/claseg2/csanmart/acceptance-files
# OUTDIR=${REPODIR}/run/sh
JOBDIR=${SCRIPTDIR}/jobs
TMPDIR=${JOBDIR}/tmp
mkdir -p ${TMPDIR}

# setting jobname
jobname="Acceptance_${TARNAME}_${BINNAME}B"
if [[ -n $CUTLIST ]]; then
    jobname="${jobname}_${CUTLIST}"
fi
jobfile="${JOBDIR}/${jobname}.sh"

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
echo "loadClas12modules"                                                        >> ${jobfile}
echo "cd ${SCRIPTDIR}"                                                          >> ${jobfile}
echo "root -l -b 'getAcceptance.C(\"${TARNAME}\", ${BINNAME}, \"${CUTLIST}\")'" >> ${jobfile}

echo "Submitting job: ${jobfile}"
sbatch ${jobfile} # submit job!
