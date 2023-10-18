
######################################################################
# -------------------------- SCRIPT CALL --------------------------- #
#                                                                    #
######################################################################
# -------------------- DEFINITION OF VARIABLES --------------------- #
#  <target>  = (D, C, Fe, Pb, DS*)                                   #
#              * Available in FitCrossSection.sh only,               #
#                runs over D per solid target                        #
#  <binN> = (0: SMoran;  1: No Zh integrated;                        #
#            2: Thin Zh;  3: Thin Pt;  4: Thin Zh & Pt;              #
#            5: Thin Zh, coarse Phi (20 bins);                       #
#            6: 5 + Thin Pt;  7: 6 but coarser Phi (15 bins);        #
#            8: 7 but up to Pt = 3.0;                                #
#            9: 8 but thinner initial Pt bins;                       #
#            10: New (Zh,Pt,Phi) binning (8,7,13);                   #
#            11: Same as 10 but with Xb instead of Nu; )             #
#  <binDim> = (1: All bins use irregular as defined;                 #
#              2: Regular bins in Zh, Pt2, and PhiPQ;                #
#              3: Regular bins in Pt2, and PhiPQ;)                   #
#  <cuts>    = Format "AA_BB_CC" (See list below)                    #
#                                                                    #
#  <fAcc>    = Fraction of stats used in calculation of Acc          #
#              (from 0-100, ex: 50, 70...)                           #
#                                                                    #
#  <jobtype>  = (Acceptance, Correction, Closure Test)               #
#                                                                    #
#  <hist2dMeth> = ("KinVars", "XfVsYh", "ThetaPQ", "LabAngles",      #
#               "PQVsLab", "VsSector", "VsDeltaSector",              #
#               "VarsVsXb", "PiCherenkovCounter", "NpheVs")          #
#                                                                    #
# ----------------------------- CUTS ------------------------------- #
#  "Xf": Use Xf>0 (CFR);   "XT": Use Xf<0 (TFR);                     #
#  "DS": Delta Sector != 0;   "BS": rm Bad Sect;                     #
#  "PF": Pi+ fiducial cut;   "MM": Mirror Match*;   "M2": MM2**;     #
#  "FE": Use FullError;   "AQ": Acc Quality < 10%;                   #
#  "Pe": Removes events with NpheEl==Nphe;                           #
#                                                                    #
#  * Requires Nphe<25 for low momentum pi+ (It is NOT a              #
#    real Mirror Matching)                                           #
#  ** Removes ALL low momentum pi+ (Not good idea)                   #
#                                                                    #
# ---------------------------- EXAMPLE ----------------------------- #
#  EG: ./send_all_jobs.sh Acceptance 10 Xf_PF                        #
#      ./send_job_AllHist2D.sh NpheVs Xf                             #
#                                                                    #
# ------------------------- From ~/run/sh -------------------------- #
#                                                                    #
# send_all_jobs        : <jobtype> <binN> <cuts>                     #
# send_job_Acceptance  : <target> <binN> <cuts>                      #
# send_job_AllHist2D   : <hist2dMeth> <cuts> <binDim>*               #
# send_job_ClosureTest : <target> <binN> <binDim> <fAcc> <cuts>      #
# send_job_Correction  : <target> <binN> <binDim> <cuts>             #
#                                                                    #
#  * Optional, depends on the method                                 #
######################################################################

