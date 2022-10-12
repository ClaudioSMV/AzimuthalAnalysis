from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle
import math
import numpy as np

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

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

# saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
if options.JLabCluster: rootpath = "JLab_cluster"

infoDict = myStyle.getNameFormattedDict(dataset)

inputPath = myStyle.getOutputDir("Correction",infoDict["Target"],rootpath)
nameFormatted = myStyle.getNameFormatted(dataset)
inputfile = TFile(inputPath+nameFormatted+".root","READ")

outputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

list_of_hists = inputfile.GetListOfKeys()

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

outputfile = TFile("%sFitFold_%s.root"%(outputPath,nameFormatted),"RECREATE")

for h in list_of_hists:
    if (h.ReadObj().Class_Name() == "TH1D"):
        if "Corr" in h.GetName():
            # if "PQ" in h.GetName(): continue
            # if not isData and "reco" in h.GetName(): continue

            # Name format is: Corr_Reconstructed_Q0N0
            tmp_txt = h.GetName().split("_")[2] # Q0N0

            var1 = tmp_txt[0] # Q
            var2 = tmp_txt[2] # N
            # type_hist = correct_prefix[tmp_txt[2]]

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

            hist_tmp.Fit("crossSection", "Q", "", fit_min_limit, 180.0)

            hist_tmp.Draw("FUNC same")

            hist_tmp.Write()

            myStyle.DrawPreliminaryInfo("Correction fit")
            myStyle.DrawTargetInfo(nameFormatted, "Data")
            myStyle.DrawBinInfo(tmp_txt)

            canvas.SaveAs(outputPath+"FitFold_"+nameFormatted+"_"+tmp_txt+".gif")
            canvas.Clear()

outputfile.Close()
