from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,THStack,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as mS
import math

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
mS.ForceStyle()
gStyle.SetPadRightMargin(2*mS.GetMargin())
gStyle.SetPadTopMargin(1.1*mS.GetMargin())
gStyle.SetLabelSize(mS.GetSize()-10,"z")
gStyle.SetTitleYOffset(1.3)
gROOT.ForceStyle()

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

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

# drawLines = options.drawLines
isData = options.isData

this_targ = dataset
# infoDict = mS.getDictNameFormat(dataset)
# nameFormatted = mS.getNameFormatted(dataset, True)
# this_binning = infoDict["BinningType"]
# this_bin_dict = mS.all_dicts[this_binning]

## Cuts
input_cuts = options.inputCuts

## Input
inputPath = mS.getOutputFolder("Hist2D", input_cuts, isJLab, False) # "../output/"
inputPath += "CC_NpheVsP_"+this_targ+"_"
inputPath += "data.root" if isData else "hsim.root"
inputfile = TFile(inputPath,"READ")

## Output
outputPath = mS.getPlotsFolder("Hist2D/CherenkovCounter", input_cuts, "", isJLab)


### Set input hists
list_names = ["hist2D_Nphe_P_Pi", "hist2D_Nphe_P_Pi_MassCut"]
ext_name = ["", "MassCut"]

# ### Set output hists
# phi_axis_title = mS.axis_label('I',"LatexUnit")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

for n,nm in enumerate(list_names):
    hist2D = inputfile.Get(nm)

    # ROOT.TGaxis.SetExponentOffset(-0.06, 0.0, "y")
    hist2D.GetZaxis().SetMaxDigits(3)

    hist2D.Draw("colz")

    mS.DrawPreliminaryInfo("P_{#pi^{+}} vs N_{phe} map")
    dataOrSim = "Data" if isData else "Simulation"
    out_DatOrSim = "Data" if isData else "HSim"

    mS.DrawTargetInfo(this_targ, dataOrSim)

    name_png = mS.getPlotsFile("PvsNphe%s_%s"%(ext_name[n], this_targ),"","png",out_DatOrSim)
    canvas.SaveAs(outputPath+name_png)

    # name_pdf = mS.getPlotsFile("PvsNphe_%s"%(this_targ),"","pdf",out_DatOrSim)
    # canvas.SaveAs(outputPath+name_pdf)

    canvas.Clear()
