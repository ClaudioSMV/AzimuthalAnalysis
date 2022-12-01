from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle
import math
import numpy as np

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
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

# saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
if options.JLabCluster: rootpath = "JLab_cluster"
ext_error = "_FullErr" if options.errorFull else ""

infoDict = myStyle.getNameFormattedDict(dataset)

inputPath = myStyle.getOutputDir("Correction",infoDict["Target"],rootpath)
nameFormatted = myStyle.getNameFormatted(dataset)
inputfile = TFile(inputPath+nameFormatted+ext_error+".root","READ")

outputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

list_of_hists = inputfile.GetListOfKeys()

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

outputfile = TFile("%sFitFold_%s%s.root"%(outputPath,nameFormatted,ext_error),"RECREATE")

for h in list_of_hists:
    if (h.ReadObj().Class_Name() == "TH1D"):
        if "Corr" in h.GetName():
            # if "PQ" in h.GetName(): continue
            # if not isData and "reco" in h.GetName(): continue

            # Name format is: Corr_Reconstru_Q0N0
            tmp_txt = h.GetName().split("_")[2] # Q0N0Z0

            hist = h.ReadObj()
            Nbins = hist.GetXaxis().GetNbins()

            ## Fold two tails in one
            hist_tmp = TH1D("%s_fold"%(h.GetName()), ";#phi_{PQ} (deg);Counts", Nbins/2, 0.0,180.0)
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

            ### Get limit of the fit just before the central peak
            hist_tmp.GetXaxis().SetRangeUser(0.0, 45.0)
            limit_bin = hist_tmp.GetMinimumBin()
            fit_min_limit = hist_tmp.GetBinLowEdge(limit_bin)
            hist_tmp.GetXaxis().UnZoom()

            #print("Fit limit: %.2f (Bin %i)"%(fit_min_limit, limit_bin))

            hist_tmp.SetMinimum(0.0001)
            ylim = hist_tmp.GetMaximum()*1.4
            hist_tmp.SetMaximum(ylim)

            # hist.GetXaxis().SetTitle("#phi_{PQ} (deg)")
            # hist.GetYaxis().SetTitle("Counts")

            hist_tmp.Draw("hist axis")

            # fit_min_limit=40.0
            fit_funct = TF1("crossSection","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)",  fit_min_limit, 180.0)

            cov_matrix = hist_tmp.Fit("crossSection", "MSQ", "", fit_min_limit, 180.0) # M: Uses IMPROVED TMinuit; S: Saves covariance matrix
            # hist_tmp.Fit("crossSection", "WL MS", "", fit_min_limit, 180.0) # WL: Uses Weighted log likelihood method

            cov_matrix.GetCorrelationMatrix().Write("%s_corrM"%(tmp_txt))
            cov_matrix.GetCovarianceMatrix().Write("%s_covM"%(tmp_txt))

            hist_tmp.Draw("FUNC same")

            hist_tmp.Write()

            myStyle.DrawPreliminaryInfo("Correction fit")
            myStyle.DrawTargetInfo(nameFormatted, "Data")
            myStyle.DrawBinInfo(tmp_txt, infoDict["BinningType"])

            canvas.SaveAs(outputPath+"FitFold_"+nameFormatted+"_"+tmp_txt+ext_error+".gif")
            canvas.Clear()

outputfile.Close()
