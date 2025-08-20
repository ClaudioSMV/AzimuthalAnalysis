
##########################################################################################
#  ----------------------------------  SCRIPT CALL  -----------------------------------  #
#                                                                                        #
##########################################################################################
#  ----------------------------  DEFINITION OF VARIABLES  -----------------------------  #
#                                                                                        #
#  <target>  = (D, C, Fe, Pb) + (DC, DFe, DPb)                                           #
#                                                                                        #
#  <Nbin> = (0: SMoran;  1: No Zh integrated;  2: Thin Zh;  3: Thin Pt;                  #
#            4: Thin Zh & Pt;  5: Thin Zh, coarse Phi (20 bins);  6: 5 + Thin Pt;        #
#            7: 6 but coarser Phi (15 bins);  8: 7 but up to Pt = 3.0;                   #
#            9: 8 but thinner initial Pt bins;  10: New (Zh,Pt,Phi) binning (8,7,13);    #
#            11: Same as 10 but with Xb instead of Nu;  )                                #
#  <binDim> = (0: All bins are REGULAR                                                   #
#              1: All bins use irregular as defined;                                     #
#              2: Regular bins in Zh, Pt2, and PhiPQ;                                    #
#              3: Regular bins in Pt2, and PhiPQ;  )                                     #
#  <CUTS> = Format "AA_BB_CC" (See list below)                                           #
#                                                                                        #
#  <fAcc> = Fraction of stats used in calculation of Acc (range: 0-100, default: 50)     #
#                                                                                        #
#  (WIP) <hist2dMeth> = ("KinVars", "XfVsYh", "ThetaPQ", "LabAngles",                    #
#                        "PQVsLab", "VsSector", "VsDeltaSector",                         #
#                        "VarsVsXb", "PiCherenkovCounter", "NpheVs")                     #
#                                                                                        #
#  --------------------------------------  CUTS  --------------------------------------  #
#                                                                                        #
#  "Xf": Use Xf>0 (CFR);  "XT": Use Xf<0 (TFR);  "DS": Delta Sector != 0;                #
#  "BS": rm Bad Sect;  "PF": Pi+ fiducial cut;  "MM": Mirror Match*;  "M2": MM2**;       #
#  "FE": Use FullError;  "AQ": Acc Quality < 10%;                                        #
#  "Pe": Removes events with NpheEl==Nphe;                                               #
#                                                                                        #
#  * Requires Nphe<25 for low momentum pi+ (It is NOT a real Mirror Matching)            #
#  ** Removes ALL low momentum pi+ (Not good idea)                                       #
#                                                                                        #
#  ------------------------------------  EXAMPLE  -------------------------------------  #
#                                                                                        #
#  EG: ./send_job_Acceptance.sh Fe 10                                                    #
#      ./send_job_Correction.sh C 10 1 FE_AQ                                             #
#                                                                                        #
#  ---------------------------------  From ~/run/sh  ----------------------------------  #
#                                                                                        #
#  send_job_Acceptance : <target> <Nbin> <cuts>                                          #
#  send_job_Correction : <target> <Nbin> <binDim> <cuts>                                 #
#   ** send_job_ClosureTest : <target> <Nbin> <binDim> <cuts> <fAcc> -> TO BE UPDATED ** #
#                                                                                        #
##########################################################################################
