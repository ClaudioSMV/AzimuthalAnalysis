from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle

###############################################
###############################################
###############   DEPRECATED!   ###############
###############################################
#####      Check PlotFit.py instead!      #####
###############################################
###############################################

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
myStyle.ForceStyle()

gStyle.SetStatX(1 - myStyle.GetMargin() - 0.005)
gStyle.SetStatY(2*myStyle.GetMargin() + 0.205)

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
if options.JLabCluster: rootpath = "JLab_cluster"
ext_error = "_FullErr" if options.errorFull else ""

infoDict = myStyle.getDictNameFormat(dataset)

inputPath = myStyle.getOutputDir("Correction",infoDict["Target"],rootpath)
nameFormatted = myStyle.getNameFormatted(dataset)
inputfile = TFile(inputPath+nameFormatted+ext_error+".root","READ")

outputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

list_of_hists = inputfile.GetListOfKeys()

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

outputfile = TFile("%sFitBothTails_%s.root"%(outputPath,nameFormatted),"RECREATE")

for h in list_of_hists:
    if (h.ReadObj().Class_Name() == "TH1D"):
        if "Corr" in h.GetName():
            # if "PQ" in h.GetName(): continue
            # if not isData and "reco" in h.GetName(): continue

            # Name format is: Corr_Reconstru_Q0N0
            tmp_txt = h.GetName().split("_")[2] # Q0N0

            var1 = tmp_txt[0] # Q
            var2 = tmp_txt[2] # N
            # type_hist = correct_prefix[tmp_txt[2]]

            hist = h.ReadObj()
            hist.SetMinimum(0.0001)
            ylim = hist.GetMaximum()*1.4
            hist.SetMaximum(ylim)

            ### Get limit of the fit just before the central peak
            ## Left (Negative)
            hist.GetXaxis().SetRangeUser(-45.0, 0.0)
            limit_bin_L = hist.GetMinimumBin()
            fit_min_limit_L = hist.GetBinCenter(limit_bin_L)
            hist.GetXaxis().UnZoom()

            ## Right (Positive)
            hist.GetXaxis().SetRangeUser(0.0, 45.0)
            limit_bin_R = hist.GetMinimumBin()
            fit_min_limit_R = hist.GetBinCenter(limit_bin_R)
            hist.GetXaxis().UnZoom()

            hist.GetXaxis().SetTitle("#phi_{PQ} (deg)")
            hist.GetYaxis().SetTitle("Counts")

            hist.Draw("hist axis")

            fit_funct_left  = TF1("crossSectionL","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)", -180.0,fit_min_limit_L)
            fit_funct_right = TF1("crossSectionR","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)",  fit_min_limit_R, 180.0)

            hist.Fit("crossSectionL", "Q", "",        -180.0,fit_min_limit_L)
            hist.Fit("crossSectionR", "Q+ sames", "", fit_min_limit_R, 180.0)

            cov_matrix_L = hist.Fit("crossSectionL", "MSQ", "", -180.0,fit_min_limit_L) # M: Uses IMPROVED TMinuit; S: Saves covariance matrix
            cov_matrix_R = hist.Fit("crossSectionR", "MSQ+", "", fit_min_limit_R, 180.0) # M: Uses IMPROVED TMinuit; S: Saves covariance matrix

            # cov_matrix_L.GetCorrelationMatrix().Write("%s_corrM0"%(tmp_txt))
            # cov_matrix_L.GetCovarianceMatrix().Write("%s_covM0"%(tmp_txt))
            cov_matrix_R.GetCorrelationMatrix().Write("%s_corrM"%(tmp_txt))
            cov_matrix_R.GetCovarianceMatrix().Write("%s_covM"%(tmp_txt))

            hist.Draw("FUNC same")

            hist.Write()

            myStyle.DrawPreliminaryInfo("Correction fit")
            myStyle.DrawTargetInfo(nameFormatted, "Data")
            myStyle.DrawBinInfo(tmp_txt, infoDict["BinningType"])

            str_FitL = TLatex(-15, 0.8*hist.GetBinContent(limit_bin_L), "#chi^2 / ndf = %.2f / %i"%(fit_funct_left.GetChisquare(), fit_funct_left.GetNDF()))
            str_FitL.SetTextAlign(33)
            str_FitL.SetTextSize(myStyle.GetSize()-6)
            str_FitL.Draw()

            str_FitR = TLatex(15, 0.8*hist.GetBinContent(limit_bin_R), "#chi^2 / ndf = %.2f / %i"%(fit_funct_right.GetChisquare(), fit_funct_right.GetNDF()))
            str_FitR.SetTextAlign(13)
            str_FitR.SetTextSize(myStyle.GetSize()-6)
            str_FitR.Draw()

            canvas.SaveAs(outputPath+"FitBothTails_"+nameFormatted+"_"+tmp_txt+".gif")
            canvas.Clear()

outputfile.Close()
