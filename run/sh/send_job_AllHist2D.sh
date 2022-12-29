#!/bin/bash

#####################################################
#       ./send_job_AllHist2D.sh <vars> <nAcc>       #
#    <target> = (D, C, Fe, Pb)                      #
#    <vars> = "KinVars", "XfVsYh", "ThetaPQ",       #
#             "LabAngles", "PQVsLab"                #
#    <nAcc> = nBin Acceptance (for corrected plots) #
#                                                   #
# EG: ./send_job_AllHist2D.sh KinVars               #
#     ./send_job_AllHist2D.sh ThetaPQ               #
#####################################################

#####
# Input
###

INPUTARRAY=("$@")

VARNAME=${INPUTARRAY[0]}
NBINACC=${INPUTARRAY[1]}

#####
# Main
###

# set env
source ~/.bashrc

# set main dirs
REPODIR=/volatile/clas/claseg2/csanmart/AzimuthalAnalysis
OUTDIR=${REPODIR}/run/sh
TMPDIR=${OUTDIR}/tmp
mkdir -p ${OUTDIR} ${TMPDIR}

if [[ $NBINACC == "" ]]; then
    NBINACC="-1"
fi

# setting jobname
jobname="Hist2D_${VARNAME}"
jobfile="${TMPDIR}/${jobname}.sh"

echo ${jobname}

echo "#!/bin/bash"                                                          > ${jobfile}
echo "#SBATCH -A clas"                                                     >> ${jobfile}
echo "#SBATCH -J ${jobname}"                                               >> ${jobfile}
echo "#SBATCH -o ${TMPDIR}/${jobname}.out"                                 >> ${jobfile}
echo "#SBATCH -e ${TMPDIR}/${jobname}.err"                                 >> ${jobfile}
echo "#SBATCH --time=3:00:00"                                              >> ${jobfile} # 4hrs or 15min for test
echo "#SBATCH --mem-per-cpu=500M"                                          >> ${jobfile}
echo "#SBATCH --mail-user=claudio.sanmartinval@gmail.com"                  >> ${jobfile}
echo "#SBATCH --mail-type=BEGIN,END,FAIL"                                  >> ${jobfile}
echo ""                                                                    >> ${jobfile}
echo "source ${HOME}/.bashrc"                                              >> ${jobfile}
echo "cd ${REPODIR}/run"                                                   >> ${jobfile}

echo "-- Data --"                                                          >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"Fe\", true, \"${VARNAME}\",${NBINACC})'"   >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"C\", true, \"${VARNAME}\",${NBINACC})'"    >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"Pb\", true, \"${VARNAME}\",${NBINACC})'"   >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"DFe\", true, \"${VARNAME}\",${NBINACC})'"  >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"DC\", true, \"${VARNAME}\",${NBINACC})'"   >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"DPb\", true, \"${VARNAME}\",${NBINACC})'"  >> ${jobfile}

echo "-- Simulations --"                                                   >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"Fe\", false, \"${VARNAME}\",${NBINACC})'"  >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"C\", false, \"${VARNAME}\",${NBINACC})'"   >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"Pb\", false, \"${VARNAME}\",${NBINACC})'"  >> ${jobfile}
echo "root -l -b 'getHist2D.C(\"D\", false, \"${VARNAME}\",${NBINACC})'"   >> ${jobfile}

echo "Submitting job: ${jobfile}"
sbatch ${jobfile} # submit job!
