from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle

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

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

useFold = options.fold
if "Fold" in myStyle.getCutStrFromStr(options.outputCuts):
    useFold = True
fit_type = "Fd" if useFold else "LR"

infoDict = myStyle.getDictNameFormat(dataset)
nameFormatted = myStyle.getNameFormatted(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"

plots_cuts+="_"+fit_type # Add Fold or LR extension


## Input
inputPath = myStyle.getPlotsFolder("Correction", input_cuts, infoDict["Target"], isJLab, False) # "../output/"
inputROOT = myStyle.getPlotsFile("Corrected", dataset, "root")
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = myStyle.getPlotsFolder("Fit", plots_cuts, infoDict["Target"], isJLab)
outputROOT = myStyle.getPlotsFile("Fit", dataset, "root", fit_type)

list_of_hists = inputfile.GetListOfKeys()

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

outputfile = TFile(outputPath+outputROOT,"RECREATE")
# # FitBothTails_

for h in list_of_hists:
    if (h.ReadObj().Class_Name() == "TH1D"):
        if "Corr" in h.GetName(): ## ADD SUPPORT FOR ALL CORRECTIONS!
            # if "PQ" in h.GetName(): continue
            # if not isData and "reco" in h.GetName(): continue

            # Name format is: Corr_Reconstru_Q0N0
            tmp_name = "_".join(h.GetName().split("_")[1:-1]) # Reconstru
            tmp_txt = h.GetName().split("_")[-1] # Q0N0Z0

            hist = h.ReadObj()
            Nbins = hist.GetXaxis().GetNbins()

            if useFold:
                ## Fold two tails in one
                hist_tmp = TH1D("%s_Fd"%(h.GetName()), ";#phi_{PQ} (deg);Counts", Nbins/2, 0.0,180.0)
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
                hist_tmp = hist.Clone("%s_LR"%(h.GetName()))

            ### Get limit of the fit just before the central peak
            ## Left (Negative)
            if not useFold:
                hist_tmp.GetXaxis().SetRangeUser(-45.0, 0.0)
                limit_bin_L = hist_tmp.GetMinimumBin()
                fit_min_limit_L = hist.GetBinLowEdge(limit_bin_L+1)
                hist.GetXaxis().UnZoom()
            else:
                fit_min_limit_L = 0.0

            ## Right (Positive)
            hist_tmp.GetXaxis().SetRangeUser(0.0, 45.0)
            limit_bin_R = hist_tmp.GetMinimumBin()
            fit_min_limit_R = hist_tmp.GetBinLowEdge(limit_bin_R)
            hist_tmp.GetXaxis().UnZoom()

            #print("Fit limit: %.2f (Bin %i)"%(fit_min_limit, limit_bin))

            hist_tmp.SetMinimum(0.0001)
            ylim = hist_tmp.GetMaximum()*1.4
            hist_tmp.SetMaximum(ylim)

            hist_tmp.GetXaxis().SetTitle("#phi_{PQ} (deg)")
            hist_tmp.GetYaxis().SetTitle("Counts")

            hist_tmp.Draw("hist axis")

            # fit_funct_fold  = TF1("crossSectionF","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)",  fit_min_limit_R, 180.0)
            fit_funct_left  = TF1("crossSectionL","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)", -180.0,fit_min_limit_L)
            fit_funct_right = TF1("crossSectionR","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)",  fit_min_limit_R, 180.0)

            cov_matrix_R = hist_tmp.Fit("crossSectionR", "MSQ", "", fit_min_limit_R, 180.0) # M: Uses IMPROVED TMinuit; S: Saves covariance matrix
            # hist_tmp.Fit("crossSection", "WL MS", "", fit_min_limit, 180.0) # WL: Uses Weighted log likelihood method
            cov_matrix_R.GetCorrelationMatrix().Write("%s_corrM"%(tmp_txt))
            cov_matrix_R.GetCovarianceMatrix().Write("%s_covM"%(tmp_txt))

            if not useFold:
                cov_matrix_L = hist_tmp.Fit("crossSectionL", "MSQ+", "", -180.0,fit_min_limit_L) # M: Uses IMPROVED TMinuit; S: Saves covariance matrix
                cov_matrix_L.GetCorrelationMatrix().Write("%s_corrML"%(tmp_txt))
                cov_matrix_L.GetCovarianceMatrix().Write("%s_covML"%(tmp_txt))

            hist_tmp.Draw("FUNC same")

            hist_tmp.Write()

            myStyle.DrawPreliminaryInfo("Correction fit")
            myStyle.DrawTargetInfo(nameFormatted, "Data")
            myStyle.DrawBinInfo(tmp_txt, infoDict["BinningType"])

            if not useFold:
                str_FitL = TLatex(-15, 0.8*hist.GetBinContent(limit_bin_L), "#chi^2 / ndf = %.2f / %i"%(fit_funct_left.GetChisquare(), fit_funct_left.GetNDF()))
                str_FitL.SetTextAlign(33)
                str_FitL.SetTextSize(myStyle.GetSize()-6)
                str_FitL.Draw()

                str_FitR = TLatex(15, 0.8*hist.GetBinContent(limit_bin_R), "#chi^2 / ndf = %.2f / %i"%(fit_funct_right.GetChisquare(), fit_funct_right.GetNDF()))
                str_FitR.SetTextAlign(13)
                str_FitR.SetTextSize(myStyle.GetSize()-6)
                str_FitR.Draw()

            outputName = myStyle.getPlotsFile("Fit_"+tmp_name, dataset, "gif",tmp_txt)
            canvas.SaveAs(outputPath+outputName)
            canvas.Clear()

print("Fit parameters saved!")
outputfile.Close()