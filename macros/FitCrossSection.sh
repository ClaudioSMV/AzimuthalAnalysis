#!/bin/bash

############################################################################
#         ./FitCrossSection.sh <target> <binName> <binNdim> <cuts>         #
#  <target>  = (D, C, Fe, Pb, DS) (DS: Run over D related to solid targs)  #
#  <binName> = (0: Usual, SMoran; 1: No-integrate Zh;                      #
#               2: Thin Zh; 3: Thin Pt; 4: Thin Zh and Pt;                 #
#               5: Thin Zh, coarse PhiPQ;                                  #
#               6: Thin Zh and Pt, coarse PhiPQ)                           #
#  <binNdim> = (1: All bins regular as in Binned Acc;                      #
#               2: Regular bins in Zh, Pt2, and PhiPQ;                     #
#               3: Regular bins in Pt2, and PhiPQ;)                        #
#  <cuts>    = Format "AA_BB_CC" (Empty is default)                        #
#  "Xf": Use Xf from data; "DS": Delta Sector != 0; "BS": rm Bad Sect;     #
#  "PF": Pi+ fiducial cut;                                                 #
#  "FE": Use FullError;                                                    #
#  "Zx": x-axis is Zh; "Px": x-axis is Pt2;                                #
#  "Fs": Add Sin(x) term in fit;                                           #
#  "Fd": Fit uses Fold; "LR": Fit uses both tails;                         #
#  "MD": Mix D info is ratios;                                             #
#        Add option: -O: To Overwrite files if created                     #
#                                                                          #
#  EG: ./FitCrossSection.sh C  0 2 Zx_FE_Fd                                #
#      ./FitCrossSection.sh Fe 1 3 Zx_LR                                   #
############################################################################

#####
# Input
###

INPUTARRAY=("$@")

TARNAME=${INPUTARRAY[0]}
BINNAME=${INPUTARRAY[1]}
BINNDIM=${INPUTARRAY[2]}
CUTINFO=${INPUTARRAY[3]}

#####
# Main
###
TAR_LIST=(${TARNAME})
if [[ ${TARNAME} == "DS" ]]; then
    TAR_LIST=('DC' 'DFe' 'DPb')
fi

#####
# Cuts
###
PREV_CUT="_"
CORR_CUT="_"
FITS_CUT="_"
PAR_NCUT="_"
PAR_RCUT="_"

### Before Corrected
if [[ $CUTINFO == *"Xf"* ]]; then
    PREV_CUT="${PREV_CUT}_Xf"
    CORR_CUT="${CORR_CUT}_Xf"
    FITS_CUT="${FITS_CUT}_Xf"
    PAR_NCUT="${PAR_NCUT}_Xf"
    PAR_RCUT="${PAR_RCUT}_Xf"
fi
if [[ $CUTINFO == *"DS"* ]]; then
    PREV_CUT="${PREV_CUT}_DS"
    CORR_CUT="${CORR_CUT}_DS"
    FITS_CUT="${FITS_CUT}_DS"
    PAR_NCUT="${PAR_NCUT}_DS"
    PAR_RCUT="${PAR_RCUT}_DS"
fi
if [[ $CUTINFO == *"BS"* ]]; then
    PREV_CUT="${PREV_CUT}_BS"
    CORR_CUT="${CORR_CUT}_BS"
    FITS_CUT="${FITS_CUT}_BS"
    PAR_NCUT="${PAR_NCUT}_BS"
    PAR_RCUT="${PAR_RCUT}_BS"
fi
if [[ $CUTINFO == *"PF"* ]]; then
    PREV_CUT="${PREV_CUT}_PF"
    CORR_CUT="${CORR_CUT}_PF"
    FITS_CUT="${FITS_CUT}_PF"
    PAR_NCUT="${PAR_NCUT}_PF"
    PAR_RCUT="${PAR_RCUT}_PF"
fi
if [[ $CUTINFO == *"FE"* ]]; then
    PREV_CUT="${PREV_CUT}_FE"
    CORR_CUT="${CORR_CUT}_FE"
    FITS_CUT="${FITS_CUT}_FE"
    PAR_NCUT="${PAR_NCUT}_FE"
    PAR_RCUT="${PAR_RCUT}_FE"
fi

### From Corrected
if [[ $CUTINFO == *"Zx"* ]]; then
    CORR_CUT="${CORR_CUT}_Zx"
    FITS_CUT="${FITS_CUT}_Zx"
    PAR_NCUT="${PAR_NCUT}_Zx"
    PAR_RCUT="${PAR_RCUT}_Zx"
elif [[ $CUTINFO == *"Px"* ]]; then
    CORR_CUT="${CORR_CUT}_Px"
    FITS_CUT="${FITS_CUT}_Px"
    PAR_NCUT="${PAR_NCUT}_Px"
    PAR_RCUT="${PAR_RCUT}_Px"
else
    echo "Remember to select a dependence as x-axis (Zh or Pt2)"
    exit
fi
if [[ $CUTINFO == *"Sh"* ]]; then
    CORR_CUT="${CORR_CUT}_Sh"
    FITS_CUT="${FITS_CUT}_Sh"
    PAR_NCUT="${PAR_NCUT}_Sh"
    PAR_RCUT="${PAR_RCUT}_Sh"
fi

### From Fit
if [[ $CUTINFO == *"Fs"* ]]; then
    FITS_CUT="${FITS_CUT}_Fs"
    PAR_NCUT="${PAR_NCUT}_Fs"
    PAR_RCUT="${PAR_RCUT}_Fs"
fi
if [[ $CUTINFO == *"Fd"* ]]; then
    FITS_CUT="${FITS_CUT}_Fd"
    PAR_NCUT="${PAR_NCUT}_Fd"
    PAR_RCUT="${PAR_RCUT}_Fd"
elif [[ $CUTINFO == *"LR"* ]]; then
    FITS_CUT="${FITS_CUT}_LR"
    PAR_NCUT="${PAR_NCUT}_LR"
    PAR_RCUT="${PAR_RCUT}_LR"
elif [[ $CUTINFO != *"Sh"* ]]; then
    echo "Remember to choose Fold (Fd) or Both wings (LR) method for the fit!"
    exit
fi

### From ParameterRatio
if [[ $CUTINFO == *"MD"* ]]; then
    PAR_RCUT="${PAR_RCUT}_MD"
fi

# Overwrite
OW=""
if [[ $CUTINFO == *"-O"* ]]; then
    OW="-O"
fi

# Draw ALL acceptance types (Reco, RecoMtch_mc, RecoMtch_re)
DA=""
if [[ $CUTINFO == *"-A"* ]]; then
    DA="-A"
fi

# echo $PREV_CUT
# echo $CORR_CUT
# echo $FITS_CUT
# echo $PAR_NCUT
# echo $PAR_RCUT

for t in "${TAR_LIST[@]}"; do
    python PlotCorrection.py        -D ${t}_${BINNAME}_${BINNDIM} -i $PREV_CUT -o $CORR_CUT -J $OW $DA
    python PlotFit.py               -D ${t}_${BINNAME}_${BINNDIM} -i $CORR_CUT -o $FITS_CUT -J $OW
    python GetParametersNorm.py     -D ${t}_${BINNAME}_${BINNDIM} -i $FITS_CUT -o $PAR_NCUT -J $OW
    python GetParametersRatio.py    -D ${t}_${BINNAME}_${BINNDIM} -i $FITS_CUT -o $PAR_RCUT -J $OW
done
