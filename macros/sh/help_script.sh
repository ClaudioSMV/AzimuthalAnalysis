
##########################################################################################
#  ----------------------------------  SCRIPT CALL  -----------------------------------  #
#                                                                                        #
##########################################################################################
#  ----------------------------  DEFINITION OF VARIABLES  -----------------------------  #
#                                                                                        #
#  <target> = (D, C, Fe, Pb) or (Solid, Liquid, All)*                                    #
#              * To run set of targets and get summary in run_analysis.sh                #
#  <Nbin> = (0: SMoran;  1: No Zh integrated;  2: Thin Zh;  3: Thin Pt;                  #
#            4: Thin Zh & Pt;  5: Thin Zh, coarse Phi (20 bins);  6: 5 + Thin Pt;        #
#            7: 6 but coarser Phi (15 bins);  8: 7 but up to Pt = 3.0;                   #
#            9: 8 but thinner initial Pt bins;  10: New (Zh,Pt,Phi) binning (8,7,13);    #
#            11: Same as 10 but with Xb instead of Nu;  )                                #
#  <binDim> = (1: All bins use irregular as defined;                                     #
#              2: Regular bins in Zh, Pt2, and PhiPQ;                                    #
#              3: Regular bins in Pt2, and PhiPQ;  )                                     #
#  <BINVARS> = Format "XYZ" (See instructions below)                                     #
#                                                                                        #
#  <CUTS> = Format "AA_BB_CC" (See list below)                                           #
#                                                                                        #
#  <FITMETHOD> = ("Fd": Fold method;  "Wg": Both sides separated (Left and Right);       #
#                 "Ff": Full method (direct fit);  "Sh": Shift, center at 180°;  )       #
#                                                                                        #
#  <fAcc> = Fraction of stats used in calculation of Acc (range: 0-100, default: 50)     #
#                                                                                        #
#  --------------------------------------  BIN  ---------------------------------------  #
#                                                                                        #
#  Bins are formatted using two or three variables of interest IN ORDER.                 #
#  The last variable is the x-axis of the summary plot! Ex. QNZ, QNP, QZ, etc.           #
#                                                                                        #
#  --------------------------------------  CUTS  --------------------------------------  #
#                                                                                        #
#  "Xf": Use Xf>0 (CFR);  "XT": Use Xf<0 (TFR);  "DS": Delta Sector != 0;                #
#  "BS": rm Bad Sect;  "PF": Pi+ fiducial cut;  "MM": Mirror Match*;  "M2": MM2**;       #
#  "FE": Use FullError;  "AQ": Acc Quality < 10%;                                        #
#  "Pe": Removes events with NpheEl==Nphe;  "Fs": Add Sin(x) term in fit;                #
#  "NP": Removes peak from fit;  "Nm": Normalize distribution BEFORE fit;                #
#  "MD": Mix D info is ratios;                                                           #
#                                                                                        #
#  * Requires Nphe<25 for low momentum pi+ (It is NOT a real Mirror Matching)            #
#  ** Removes ALL low momentum pi+ (Not good idea)                                       #
#                                                                                        #
#  ---------------------------------  EXTRA OPTIONS  ----------------------------------  #
#                                                                                        #
#  "-O": Overwrite files if already created;                                             #
#  "-A": Use all correction methods of acceptance calculation;                           #
#                                                                                        #
#  ------------------------------------  EXAMPLE  -------------------------------------  #
#                                                                                        #
#  EG: ./run_analysis.sh All 10 1 QNZ FE_AQ Fd                                           #
#      ** ./runClosureTest.sh  All  10  1  Zx  50 -> TO BE UPDATED **                    #
#                                                                                        #
#  ----------------------------------  From ~/macro  ----------------------------------  #
#                                                                                        #
#  run_analysis: <target> <Nbin> <binDim> <BINVARS> <CUTS> <FITMETHOD>                   #
#   ** runClosureTest    : <target> <Nbin> <binDim> <CUTS> <fAcc> -> TO BE UPDATED **    #
#                                                                                        #
##########################################################################################
