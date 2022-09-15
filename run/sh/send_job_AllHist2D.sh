#!/bin/bash

#################################################
# ./send_job_AllHist2D.sh <vars>                #
#    <target> = (D, C, Fe, Pb)                  #
#    <vars> =  "KinVars", "Yh","ThetaPQ"        #
#                                               #
# EG: ./send_job_AllHist2D.sh C KinVars         #
#     ./send_job_AllHist2D.sh Fe ThetaPQ        #
#################################################

#####
# Input
###

INPUTARRAY=("$@")

#TARNAME=${INPUTARRAY[0]}
VARNAME=${INPUTARRAY[0]}

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
jobname="Hist2D_${VARNAME}"
jobfile="${TMPDIR}/${jobname}.sh"

echo ${jobname}

echo "#!/bin/bash"                                                         > ${jobfile}
echo "#SBATCH -A clas"                                                    >> ${jobfile}
echo "#SBATCH -J ${jobname}"                                              >> ${jobfile}
echo "#SBATCH -o ${TMPDIR}/${jobname}.out"                                >> ${jobfile}
echo "#SBATCH -e ${TMPDIR}/${jobname}.err"                                >> ${jobfile}
echo "#SBATCH --time=3:00:00"                                             >> ${jobfile} # 4hrs or 15min for test
echo "#SBATCH --mem-per-cpu=500M"                                         >> ${jobfile}
echo "#SBATCH --mail-user=claudio.sanmartinval@gmail.com"                 >> ${jobfile}
echo "#SBATCH --mail-type=BEGIN,END,FAIL"                                 >> ${jobfile}
echo ""                                                                   >> ${jobfile}
echo "source ${HOME}/.bashrc"                                             >> ${jobfile}
echo "cd ${REPODIR}/run"                                                  >> ${jobfile}

echo "-- Data --"                                                         >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"Fe\", true, \"${VARNAME}\")'"             >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"C\", true, \"${VARNAME}\")'"              >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"Pb\", true, \"${VARNAME}\")'"             >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"D\", true, \"${VARNAME}\")'"              >> ${jobfile}

echo "-- Simulations --"                                                  >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"Fe\", false, \"${VARNAME}\")'"            >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"C\", false, \"${VARNAME}\")'"             >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"Pb\", false, \"${VARNAME}\")'"            >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"D\", false, \"${VARNAME}\")'"             >> ${jobfile}

echo "Submitting job: ${jobfile}"
sbatch ${jobfile} # submit job!
