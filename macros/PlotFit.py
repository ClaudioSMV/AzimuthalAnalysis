from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle
from array import array

gROOT.SetBatch( True )
gStyle.SetOptFit(1)

## Defining Style
myStyle.ForceStyle()

gStyle.SetStatX(1 - myStyle.GetMargin() - 0.005)
gStyle.SetStatY(2*myStyle.GetMargin() + 0.205)

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")

parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default fits both tails separated)")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False, help="Overwrite if file already exists")
parser.add_option('-s', dest='useSin', action='store_true', default = False, help="Add a sin\phi term in the fit (expected to be negligible)")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

# Define use of Fold method
use_Fold = options.fold
if "Fold" in myStyle.getCutStrFromStr(options.outputCuts):
    use_Fold = True

useSin = options.useSin
if "Sin" in myStyle.getCutStrFromStr(options.outputCuts):
    useSin = True

use_Shift = False
# if shift:
#     plots_cuts+="_Sh"

if (("Shift" in myStyle.getCutsAsList(myStyle.getCutStrFromStr(options.outputCuts))) or ("Shift" in myStyle.getCutsAsList(myStyle.getCutStrFromStr(options.inputCuts)))):
    use_Shift = True
    print("  [Fit] Fit PhiPQ shifted, ranging in ~(0., 360.)")


### Define type of fit used
# [LR] is default
fit_type = "LR"

if (use_Fold and use_Shift):
    print("  [Fit] More than one fit method selected. Please, choose only one of the options!")
    exit()
# [Fold]
elif (use_Fold):
    fit_type = "Fd"
# [Shift]
elif (use_Shift):
    fit_type = "Sh"
# [LR]
# else: fit_type = "LR" # Default

infoDict = myStyle.getDictNameFormat(dataset)
nameFormatted = myStyle.getNameFormatted(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"
if useSin:
    plots_cuts+="_Fs"

plots_cuts+="_"+fit_type # Add Fold or LR extension


## Input
inputPath = myStyle.getPlotsFolder("Correction", input_cuts, myStyle.getBinNameFormatted(dataset) + "/" + infoDict["Target"], isJLab, False) # "../output/"
inputROOT = myStyle.getPlotsFile("Corrected", dataset, "root")
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = myStyle.getPlotsFolder("Fit", plots_cuts, myStyle.getBinNameFormatted(dataset) + "/" + infoDict["Target"], isJLab)
outputROOT = myStyle.getPlotsFile("Fit", dataset, "root", fit_type)
if (not options.Overwrite and os.path.exists(outputPath+outputROOT)):
    print("  [Fit] Fit already exists! Not overwriting it.")
    exit()

list_of_hists = inputfile.GetListOfKeys()

type_reco = ["Reconstru", "ReMtch_mc", "ReMtch_re"] # Corr_
type_reco_short = ["Reco", "RMmc", "RMre"]

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

outputfile = TFile(outputPath+outputROOT,"RECREATE")

phi_axis_title = myStyle.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"

for h in list_of_hists:
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_name = h.GetName() # Corr_Reconstru_Q0N0Z0
        if "Corr" in hist_name:

            # Name format is: Corr_Reconstru_Q0N0
            tmp_name = "_".join(hist_name.split("_")[1:-1]) # Reconstru
            tmp_txt = hist_name.split("_")[-1] # Q0N0Z0

            type_index = type_reco.index(tmp_name) # Index in ["Reconstru", "ReMtch_mc", "ReMtch_re"]

            # Get Histogram
            hist = h.ReadObj()

            Nbins = hist.GetXaxis().GetNbins()
            bin1 = hist.GetBinContent(1)
            bin2 = hist.GetBinContent(2)

            # print("  GetEntries: %i;  GetNbins: %i ;  Value bin1: %i; bin2: %i"%(hist.GetEntries(),Nbins, bin1, bin2))
            if (hist.GetEntries() == 0): # Maybe require a minimum number of entries?
                print("  [Fit] Histogram %s is empty! Fit is not possible."%hist_name)
                continue

            Nbins = hist.GetXaxis().GetNbins()

            # Define bin range of folded distribution [Fold]
            bin_zero = hist.FindBin(0.0)
            vect_limits = [0.0]
            for bt in range(bin_zero, Nbins+1):
                vect_limits.append(hist.GetBinLowEdge(bt+1))

            if use_Shift:
                hist_tmp = hist.Clone("%s_Sh"%(hist_name))
            else: # No shift PhiPQ
                if use_Fold:
                    ## Fold two tails in one
                    hist_tmp = TH1D("%s_Fd"%(hist_name), ";%s;Counts"%phi_axis_title, len(vect_limits)-1, array('d',vect_limits))
                    # hist_tmp.Sumw2()

                    for b in range(1, Nbins+1):
                        x_center = hist.GetBinCenter(b)
                        value = hist.GetBinContent(b)
                        error = hist.GetBinError(b)

                        this_bin = hist_tmp.FindBin(abs(x_center))

                        if (hist_tmp.GetBinContent(this_bin) > 1.0):
                            value+=hist_tmp.GetBinContent(this_bin)
                            error = TMath.Sqrt(hist_tmp.GetBinError(this_bin)*hist_tmp.GetBinError(this_bin) + error*error)

                        hist_tmp.SetBinContent(this_bin, value)
                        hist_tmp.SetBinError(this_bin, error)
                else:
                    hist_tmp = hist.Clone("%s_LR"%(hist_name))

            ### Get limit of the fit just before the central peak
            ## Left (Negative) [LR - Left]
            if ((not use_Fold) and (not use_Shift)):
                hist_tmp.GetXaxis().SetRangeUser(-45.0, 0.0)
                limit_bin_L = hist_tmp.GetMinimumBin()
                fit_max_limit_L = hist.GetBinLowEdge(limit_bin_L+1)
                hist.GetXaxis().UnZoom()
            else: # [Fold], [Shift]
                fit_max_limit_L = 0.0

            ## Right (Positive)
            if (use_Shift): # [Shift]
                # Set min of fit
                fit_min_limit_R = hist_tmp.GetBinLowEdge(2)

                # Set max of fit
                fit_max_limit_R = hist_tmp.GetBinLowEdge(Nbins)

            else: #  [LR - Right], [Fold]
                # Set min of fit
                hist_tmp.GetXaxis().SetRangeUser(0.0, 45.0)
                limit_bin_R = hist_tmp.GetMinimumBin()
                fit_min_limit_R = hist_tmp.GetBinLowEdge(limit_bin_R)
                hist_tmp.GetXaxis().UnZoom()

                # Set max of fit
                fit_max_limit_R = 180.

            # Odd binning
            if (((Nbins%2)==1) and (not use_Shift)):
                if (not use_Fold):
                    fit_max_limit_L = hist.GetBinLowEdge(bin_zero)
                fit_min_limit_R = hist.GetBinLowEdge(bin_zero+1)

            #print("Fit limit: %.2f (Bin %i)"%(fit_min_limit, limit_bin))

            hist_tmp.SetMinimum(0.0001)
            ylim = hist_tmp.GetMaximum()*1.4
            hist_tmp.SetMaximum(ylim)

            hist_tmp.GetXaxis().SetTitle(phi_axis_title)
            hist_tmp.GetYaxis().SetTitle("Counts")

            hist_tmp.Draw("hist axis")

            the_func = "[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)"
            if useSin:
                the_func+= "+ [3]*sin(TMath::Pi()*x/180.0)"

            # fit_funct_fold  = TF1("crossSectionF","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)",  fit_min_limit_R, 180.0)
            fit_funct_left  = TF1("crossSectionL",the_func, -180.0,fit_max_limit_L)
            fit_funct_right = TF1("crossSectionR",the_func,  fit_min_limit_R, fit_max_limit_R)

            ### Make fit and save covariance and correlation matrices
            cov_matrix_R = hist_tmp.Fit("crossSectionR", "MSQ", "", fit_min_limit_R, fit_max_limit_R) # M: Uses IMPROVED TMinuit; S: Saves covariance matrix
            # hist_tmp.Fit("crossSection", "WL MS", "", fit_min_limit, 180.0) # WL: Uses Weighted log likelihood method

            name_ext_cov = "%s_%s"%(tmp_txt, type_reco_short[type_index]) # "Q0N0Z0_Reco"

            cov_matrix_R.GetCorrelationMatrix().Write("corrM_%s"%(name_ext_cov)) # "corrM_Q0N0Z0_Reco"
            cov_matrix_R.GetCovarianceMatrix().Write("covM_%s"%(name_ext_cov)) # "covM_Q0N0Z0_Reco"

            # [LR - Left]
            # Save Left fit only when using LR fit method
            if ((not use_Fold) and (not use_Shift)):
                cov_matrix_L = hist_tmp.Fit("crossSectionL", "MSQ+", "", -180.0,fit_max_limit_L) # M: Uses IMPROVED TMinuit; S: Saves covariance matrix
                cov_matrix_L.GetCorrelationMatrix().Write("corrML_%s"%(name_ext_cov)) # "corrML_Q0N0Z0_Reco"
                cov_matrix_L.GetCovarianceMatrix().Write("covML_%s"%(name_ext_cov)) # "corrML_Q0N0Z0_Reco"

            hist_tmp.Draw("FUNC same")

            hist_tmp.Write()

            myStyle.DrawPreliminaryInfo("Correction fit")
            myStyle.DrawTargetInfo(nameFormatted, "Data")
            myStyle.DrawBinInfo(tmp_txt, infoDict["BinningType"])

            # [LR - Left]
            # Write ChiSquare/ndf when making two fits
            if ((not use_Fold) and (not use_Shift)):
                chisq_L = fit_funct_left.GetChisquare()
                ndf_L = fit_funct_left.GetNDF()
                if (ndf_L != 0):
                    str_FitL = TLatex(-15, 1.1*hist.GetMaximum(), "#chi^{2} / ndf = %.2f / %i = %.2f"%(chisq_L, ndf_L, chisq_L/ndf_L))
                else:
                    str_FitL = TLatex(-15, 1.1*hist.GetMaximum(), "#chi^{2} / ndf = %.2f / %i"%(chisq_L, ndf_L))
                str_FitL.SetTextAlign(33)
                str_FitL.SetTextSize(myStyle.GetSize()-6)
                str_FitL.Draw()

                chisq_R = fit_funct_right.GetChisquare()
                ndf_R = fit_funct_right.GetNDF()
                if (ndf_R != 0):
                    str_FitR = TLatex(15, 1.1*hist.GetMaximum(), "#chi^{2} / ndf = %.2f / %i = %.2f"%(chisq_R, ndf_R, chisq_R/ndf_R))
                else:
                    str_FitR = TLatex(15, 1.1*hist.GetMaximum(), "#chi^{2} / ndf = %.2f / %i"%(chisq_R, ndf_R))
                str_FitR.SetTextAlign(13)
                str_FitR.SetTextSize(myStyle.GetSize()-6)
                str_FitR.Draw()

            outputName = myStyle.getPlotsFile("Fit_"+tmp_name, dataset, "gif",tmp_txt)
            canvas.SaveAs(outputPath+outputName)
            canvas.Clear()

print("  [Fit] Fit parameters saved!")
outputfile.Close()
