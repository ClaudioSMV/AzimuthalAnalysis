from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,THStack,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
import math

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
ms.force_style()
# gStyle.SetPadRightMargin(2*ms.get_margin())
# gStyle.SetPadTopMargin(1.1*ms.get_margin())
# gStyle.SetLabelSize(ms.get_size()-10,"z")
gStyle.SetTitleXOffset(0.98)
gStyle.SetTitleYOffset(1.4)
gROOT.ForceStyle()

def Get_Chi2ndf(fit_funct):
    chisq = fit_funct.GetChisquare()
    ndf = fit_funct.GetNDF()
    if (ndf != 0):
        chi2ndf = chisq/ndf
    else:
        chi2ndf = 0

    return chi2ndf

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <target>_<binType>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

infoDict = ms.get_name_dict(dataset)
nameFormatted = ms.get_name_format(dataset, True)
this_binning = infoDict["BinningType"]
this_bin_dict = ms.all_dicts[this_binning]

## Cuts
input_cuts = options.inputCuts

## Input
inputPath = ms.get_output_folder("QualityCheck", input_cuts, isJLab, False) # "../output/"
inputROOT = this_file = "Quality_"+ms.get_name_format(dataset, True)+".root"
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = ms.get_plots_folder("AccValue", input_cuts, dataset, isJLab)


list_colors = ms.GetColors(True)

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

#############
## Acc values
#############

legend = TLegend(0.5, 0.7, 0.9, 0.9)
legend.SetBorderSize(0)
legend.SetTextFont(ms.get_font())
legend.SetTextSize(ms.get_size()-6)
legend.SetFillStyle(0)
# legend.SetTextAlign(22)

acc_Stack = THStack("Acc_Stack",";Acceptance;Counts")

acc_reco = inputfile.Get("hAccVal_Reconstru")
acc_remc = inputfile.Get("hAccVal_ReMtch_mc")
acc_rere = inputfile.Get("hAccVal_ReMtch_re")

acc_reco.Rebin(2)
acc_remc.Rebin(2)
acc_rere.Rebin(2)

acc_reco.SetLineColor(list_colors[1])
acc_remc.SetLineColor(list_colors[3])
acc_rere.SetLineColor(list_colors[4])

acc_Stack.Add(acc_reco)
legend.AddEntry(acc_reco, "Direct selection")
acc_Stack.Add(acc_rere)
legend.AddEntry(acc_rere, "Match use reco. vars")
acc_Stack.Add(acc_remc)
legend.AddEntry(acc_remc, "Match use gen. vars")

acc_Stack.Draw("")

acc_Stack.GetXaxis().SetRangeUser(0.0,0.6)
acc_Stack.Draw("nostack")
legend.Draw()

ms.DrawPreliminaryInfo("Acceptance values")
# ms.DrawTargetInfo(nameFormatted, "Simulation")
ms.DrawTopRight(nameFormatted, "Simulation")

name_png = ms.get_plots_file("SummaryValueAcc",dataset,"png")
canvas.SaveAs(outputPath+name_png)

name_pdf = ms.get_plots_file("SummaryValueAcc",dataset,"pdf")
canvas.SaveAs(outputPath+name_pdf)

canvas.Clear()


#############
## Empty bins
#############

legendEmpty = TLegend(0.58, 0.7, 0.9, 0.9)
legendEmpty.SetBorderSize(0)
legendEmpty.SetTextFont(ms.get_font())
legendEmpty.SetTextSize(ms.get_size()-6)
legendEmpty.SetFillStyle(0)

x_axis_title = ms.axis_label("I","LatexUnit")
accEmpty_Stack = THStack("AccEmpty_Stack",";%s;Counts"%x_axis_title)

accEmpty_reco = inputfile.Get("hPQEmpty_Reconstru")
accEmpty_remc = inputfile.Get("hPQEmpty_ReMtch_mc")
accEmpty_rere = inputfile.Get("hPQEmpty_ReMtch_re")

# accEmpty_reco.Rebin(2)
# accEmpty_remc.Rebin(2)
# accEmpty_rere.Rebin(2)

accEmpty_reco.SetLineColor(list_colors[1])
accEmpty_remc.SetLineColor(list_colors[3])
accEmpty_rere.SetLineColor(list_colors[4])

accEmpty_Stack.Add(accEmpty_reco)
legendEmpty.AddEntry(accEmpty_reco, "Direct selection")
accEmpty_Stack.Add(accEmpty_rere)
legendEmpty.AddEntry(accEmpty_rere, "Match use reco. vars")
accEmpty_Stack.Add(accEmpty_remc)
legendEmpty.AddEntry(accEmpty_remc, "Match use gen. vars")

accEmpty_Stack.Draw("nostack")
legendEmpty.Draw()

ms.DrawPreliminaryInfo("Null acceptance factors")
# ms.DrawTargetInfo(nameFormatted, "Simulation")
ms.DrawTopRight(nameFormatted, "Simulation")

name_png = ms.get_plots_file("SummaryEmptyAcc",dataset,"png")
canvas.SaveAs(outputPath+name_png)

name_pdf = ms.get_plots_file("SummaryEmptyAcc",dataset,"pdf")
canvas.SaveAs(outputPath+name_pdf)


canvas.Clear()
inputfile.Close()
