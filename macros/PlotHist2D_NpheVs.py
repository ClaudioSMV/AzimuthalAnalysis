from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,THStack,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
import math

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
ms.force_style(True)
# gStyle.SetPadRightMargin(2*ms.get_margin())
# gStyle.SetPadTopMargin(1.1*ms.get_margin())
# gStyle.SetLabelSize(ms.get_size()-10,"z")
# gStyle.SetTitleYOffset(1.3)
# gROOT.ForceStyle()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
# parser.add_option('-l', dest='drawLines', action='store_true', default = False, help="Draw lines to see bins")
parser.add_option('-d', dest='isData', action='store_true', default = False, help="HSim: False (default); Data: True")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
rootpath = options.rootpath
isJLab = options.JLabCluster

# drawLines = options.drawLines
isData = options.isData
this_targ = dataset

## Cuts
input_cuts = options.inputCuts

## Input
inputPath = ms.get_output_folder("Hist2D", input_cuts, isJLab, False) # "../output/"
inputPath += "NpheVs_"+this_targ+"_"
inputPath += "data.root" if isData else "hsim.root"
inputfile = TFile(inputPath,"READ")

## Output
outputPath = ms.get_plots_folder("Hist2D/NpheVs", input_cuts, dataset, isJLab)

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

for i_h,h in enumerate(inputfile.GetListOfKeys()):
    if ((h.ReadObj().Class_Name() == "TH2D")): #  and ("Corr_Reconstru" in h.GetName())
        # hist_target = h.ReadObj()
        hist_name = h.GetName() # hist2D_Nphe_vsThetaLabEl
        hist2D = inputfile.Get(hist_name)

        list_name = hist_name.split("_vs") # hist2D_Nphe , ThetaLabEl
        nameXvar = list_name[1]
        nameYvar = list_name[0].split("_")[1] # Nphe

        hist2D.GetZaxis().SetMaxDigits(3)
        hist2D.Draw("colz")

        # ms.DrawPreliminaryInfo("P_{#pi^{+}} vs N_{phe} map")
        ms.DrawPreliminaryInfo(hist2D.GetTitle())
        dataOrSim = "Data" if isData else "Simulation"
        out_DatOrSim = "Data" if isData else "HSim"

        ms.DrawTargetInfo(this_targ, dataOrSim)

        name_png = ms.get_plots_file("%sVS%s_%s"%(nameYvar,nameXvar, this_targ),"","png",out_DatOrSim)
        canvas.SaveAs(outputPath+name_png)

        # name_pdf = ms.get_plots_file("PvsNphe_%s"%(this_targ),"","pdf",out_DatOrSim)
        # canvas.SaveAs(outputPath+name_pdf)

        canvas.Clear()
