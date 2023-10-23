
################################################################################
# ------------------------------- SCRIPT CALL -------------------------------- #
#                                                                              #
################################################################################
# ------------------------- DEFINITION OF VARIABLES -------------------------- #
#  <target>  = (D, C, Fe, Pb) + (S or Solid, DS or Liquid, All)*               #
#              * Available in runAnalysis.sh only                              #
#  <binN> = (0: SMoran;  1: No Zh integrated;                                  #
#            2: Thin Zh;  3: Thin Pt;  4: Thin Zh & Pt;                        #
#            5: Thin Zh, coarse Phi (20 bins);                                 #
#            6: 5 + Thin Pt;  7: 6 but coarser Phi (15 bins);                  #
#            8: 7 but up to Pt = 3.0;                                          #
#            9: 8 but thinner initial Pt bins;                                 #
#            10: New (Zh,Pt,Phi) binning (8,7,13);                             #
#            11: Same as 10 but with Xb instead of Nu; )                       #
#  <binDim> = (1: All bins use irregular as defined;                           #
#              2: Regular bins in Zh, Pt2, and PhiPQ;                          #
#              3: Regular bins in Pt2, and PhiPQ;)                             #
#  <cuts>    = Format "AA_BB_CC" (See list below)                              #
#                                                                              #
#  <fAcc>    = Fraction of stats used in calculation of Acc                    #
#              (from 0-100, ex: 50, 70...)                                     #
#  <plotHist2d> = "DeltaSector", "CherenkovCounter", "NpheVs";                 #
#                                                                              #
# ----------------------------------- CUTS ----------------------------------- #
#  "Xf": Use Xf>0 (CFR);   "XT": Use Xf<0 (TFR);                               #
#  "DS": Delta Sector != 0;   "BS": rm Bad Sect;                               #
#  "PF": Pi+ fiducial cut;   "MM": Mirror Match*;   "M2": MM2**;               #
#  "FE": Use FullError;   "AQ": Acc Quality < 10%;                             #
#  "Pe": Removes events with NpheEl==Nphe;                                     #
#  "Zx": x-axis is Zh;   "Px": x-axis is Pt2;                                  #
#  "Fs": Add Sin(x) term in fit;   "NP": Removes peak from fit;                #
#  "Nm": Normalize distribution BEFORE fit;                                    #
#  "MD": Mix D info is ratios;                                                 #
#                                                                              #
#  * Requires Nphe<25 for low momentum pi+ (It is NOT a                        #
#    real Mirror Matching)                                                     #
#  ** Removes ALL low momentum pi+ (Not good idea)                             #
# ----------------------------------- FIT ------------------------------------ #
#  "Fd": Fold method;   "LR": Both tails Left and Right;                       #
#  "Ff": Full method (direct);   "Sh": Shift, center at 180°;                  #
#                                                                              #
# ------------------------------ EXTRA OPTIONS ------------------------------- #
#  "-O": Overwrite files if already created;                                   #
#  "-A": Use all Acc/Corr types of calculate acceptance;                       #
#                                                                              #
# --------------------------------- EXAMPLE ---------------------------------- #
#  EG: ./runAnalysis.sh  All  10  1  Zx_FE_AQ_Fd_sl                            #
#      ./runClosureTest.sh  All  10  1  Zx  50                                 #
#      ./RunAllHist2D.sh DeltaSector Zx_FE_Fd 10                               #
#                                                                              #
# ------------------------------- From ~/macro ------------------------------- #
#                                                                              #
# runAnalysis       : <target> <binN> <binDim> <cuts>                          #
# runClosureTest    : <target> <binN> <binDim> <cuts> <fAcc>                   #
#                                                                              #
################################################################################

