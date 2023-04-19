
###################################################################
# ------------------------- SCRIPT CALL ------------------------- #
#                                                                 #
# ------------------------- From ~/macro ------------------------ #
#                                                                 #
# FitCrossSection      : <target> <binN> <binDim> <cuts>          #
#                                                                 #
# RunAllFitAndSummary  : <binN> <binDim> <cuts> <run>             #
# RunAllClosureTest    : <binN> <binDim> <cuts> <fAcc>            #
# RunAllHist2D         : <method> <cuts> <binN>                   #
#                                                                 #
# ------------------------ From ~/run/sh ------------------------ #
#                                                                 #
# send_all_jobs        : <method> <binN> <cuts>                   #
# send_job_Acceptance  : <target> <binN> <cuts>                   #
# send_job_AllHist2D   : <hist2dMeth> <cuts> <binDim>*            #
# send_job_ClosureTest : <target> <binN> <binDim> <fAcc> <cuts>   #
# send_job_Correction  : <target> <binN> <binDim> <cuts>          #
#                                                                 #
#  * Optional, depends on the method                              #
###################################################################
# ------------------- DEFINITION OF VARIABLES ------------------- #
#  <target>  = (D, C, Fe, Pb, DS*)                                #
#              * Available in FitCrossSection.sh only,            #
#                runs over D per solid target                     #
#  <binN> = (0: SMoran;  1: No Zh integrated;                     #
#            2: Thin Zh;  3: Thin Pt;  4: Thin Zh & Pt;           #
#            5: Thin Zh, coarse Phi (20 bins);                    #
#            6: 5 + Thin Pt;  7: 6 but coarser Phi (15 bins);     #
#            8: 7 but up to Pt = 3.0;                             #
#            9: 8 but thinner initial Pt bins;                    #
#            10: New (Zh,Pt,Phi) binning (8,7,13);                #
#            11: Same as 10 but with Xb instead of Nu; )          #
#  <binDim> = (1: All bins use irregular as defined;              #
#              2: Regular bins in Zh, Pt2, and PhiPQ;             #
#              3: Regular bins in Pt2, and PhiPQ;)                #
#  <cuts>    = Format "AA_BB_CC" (See list below)                 #
#                                                                 #
#  <run>     = "" (empty): Both Fit and Summary;                  #
#              "F": Run FitCrossSection over all targets;         #
#              "S": Only get Summary;                             #
#              "D": Summary with different methods;               #
#  <fAcc>    = Fraction of stats used in calculation of Acc       #
#              (from 0-100, ex: 50, 70...)                        #
#  <method>  = (Acceptance, Correction, Closure Test)             #
#                                                                 #
#  <hist2dMeth> = ("KinVars", "XfVsYh", "ThetaPQ", "LabAngles",   #
#               "PQVsLab", "VsSector", "VsDeltaSector",           #
#               "VarsVsXb", "PiCherenkovCounter", "NpheVs")       #
#                                                                 #
# ---------------------------- CUTS ----------------------------- #
#  "Xf": Use Xf>0 (CFR);   "XT": Use Xf<0 (TFR);                  #
#  "DS": Delta Sector != 0;   "BS": rm Bad Sect;                  #
#  "PF": Pi+ fiducial cut;   "MM": Mirror Match*;   "M2": MM2**;  #
#  "FE": Use FullError;   "AQ": Acc Quality < 10%;                #
#  "Pe": Removes events with NpheEl==Nphe;                        #
#  "Zx": x-axis is Zh;   "Px": x-axis is Pt2;                     #
#  "Fs": Add Sin(x) term in fit;   "NP": Removes peak from fit;   #
#  "MD": Mix D info is ratios;                                    #
#                                                                 #
#  * Not really, but requires Nphe<25 for low momentum pi+        #
#  ** Directly removes all low momentum pi+ (Not good idea)       #
# ----------------------------- FIT ----------------------------- #
#  "Fd": Fold method;   "LR": Both tails Left and Right;          #
#  "Ff": Full method (direct);   "Sh": Shift, center at 180;      #
#  "AllFit": Use all fit methods*;                                #
#                                                                 #
#  * Available in RunAllFitAndSummary.sh only                     #
# ------------------------ EXTRA OPTIONS ------------------------ #
#  "-O": To Overwrite files if created;                           #
#  "-A": Use all ways of Acc calculation;                         #
#                                                                 #
#  EG: ./FitCrossSection.sh C  0 2 Zx_FE_Fd                       #
#      ./RunAllHist2D.sh DeltaSector Zx_FE_Fd 10                  #
###################################################################

