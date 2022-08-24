#!/bin/bash

##############################################################
#  ./send_job_Correction.sh <target> <binName> <binNdim>     #
#    <target> = (D, C, Fe, Pb)                               #
#    <binName>   = (0: Usual, SMoran; 1: No-integrate Zh)    #
#                                                            #
# EG: ./send_job_Correction.sh C 0 2                         #
#     ./send_job_Correction.sh Fe 1 3                        #
##############################################################

#####
# Input
###

INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}

#####
# Main
###

# set env
source ~/.bashrc

# set main dirs
REPODIR=${HOME}/work/AzimuthalAnalysis
OUTDIR=${REPODIR}/run/sh
TMPDIR=${OUTDIR}/tmp
mkdir -p ${OUTDIR} ${TMPDIR}

# setting jobname
jobname="GetCorr_${TARNAME}_B${BINNAME}_${BINNDIM}D"
jobfile="${TMPDIR}/${jobname}.sh"

echo ${jobname}

echo "#!/bin/bash"                                                         > ${jobfile}
echo "#SBATCH -A clas"                                                    >> ${jobfile}
echo "#SBATCH -J ${jobname}"                                              >> ${jobfile}
echo "#SBATCH -o ${TMPDIR}/${jobname}.out"                                >> ${jobfile}
echo "#SBATCH -e ${TMPDIR}/${jobname}.err"                                >> ${jobfile}
echo "#SBATCH --time=4:00:00"                                             >> ${jobfile} # 4hrs or 15min for test
echo "#SBATCH --mem-per-cpu=500M"                                         >> ${jobfile}
echo "#SBATCH --mail-user=claudio.sanmartinval@gmail.com"                 >> ${jobfile}
echo "#SBATCH --mail-type=BEGIN,END,FAIL"                                 >> ${jobfile}
echo ""                                                                   >> ${jobfile}
echo "source ${HOME}/.bashrc"                                             >> ${jobfile}
echo "cd ${REPODIR}/run"                                                  >> ${jobfile}
echo "root -l -b 'getCorrection.C(\"${TARNAME}\",${BINNAME},${BINNDIM})'" >> ${jobfile}

echo "Submitting job: ${jobfile}"
sbatch ${jobfile} # submit job!
