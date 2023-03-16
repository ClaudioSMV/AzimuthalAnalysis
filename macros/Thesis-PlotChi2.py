from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,THStack,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
import math

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
ms.ForceStyle()
# gStyle.SetPadRightMargin(2*ms.GetMargin())
# gStyle.SetPadTopMargin(1.1*ms.GetMargin())
# gStyle.SetLabelSize(ms.GetSize()-10,"z")
# gStyle.SetTitleYOffset(1.3)
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
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

infoDict = ms.getDictNameFormat(dataset)
nameFormatted = ms.getNameFormatted(dataset, True)
this_binning = infoDict["BinningType"]
this_bin_dict = ms.all_dicts[this_binning]

## Cuts
input_cuts = options.inputCuts
fit_type = ms.GetFitMethod(input_cuts)

## Input
inputPath = ms.getPlotsFolder("Fit", input_cuts, ms.getBinNameFormatted(dataset) +"/"+ infoDict["Target"], isJLab, False) # "../output/"
inputROOT = ms.getPlotsFile("Fit", dataset, "root", fit_type)
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = ms.getPlotsFolder("Fit_Chi2", input_cuts, "", isJLab)

### Define fit name
this_fit_name = "crossSectionR"
this_fit_num = 0
if ("Left" in input_cuts):
    this_fit_name = "crossSectionL"
    this_fit_num = 1

# th1_chi2 = TH1D("th1_chi2",";#chi^{2}/ndf;Counts",100,0,100)
list_values = []
max_chi = 10

for i_h,h in enumerate(inputfile.GetListOfKeys()): #list_of_hists):
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_targ = h.ReadObj()
        hist_name = h.GetName() # Corr_Reconstru_Q0N0Z0_type (type: Fd or LR)
        # print(hist_name)

        if ("Reconstru" not in hist_name):
            continue

        tmp_name = "_".join(h.GetName().split("_")[1:-2]) # Reconstru
        bin_name = hist_name.split("_")[-2] # Q0N0Z0

        input_fit = inputfile.Get(hist_name)
        chi2ndf_value = Get_Chi2ndf(input_fit.GetFunction(this_fit_name))

        if (chi2ndf_value > max_chi):
            max_chi = chi2ndf_value
        # th1_chi2.Fill(chi2ndf_value)
        list_values.append(chi2ndf_value)

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

max_x = int(round(max_chi)+1)
nbins = int(max_x/0.5)
print(" Using %i as x-axis limit with %i bins."%(max_x, nbins))

th1_chi2 = TH1D("th1_chi2",";#chi^{2}/ndf;Counts", nbins, 0.0, max_x)

for v in list_values:
    th1_chi2.Fill(v)

th1_chi2.GetYaxis().SetRangeUser(0.001, 1.1*th1_chi2.GetMaximum())

# tmp_hist = TH1D("tmp",";#chi^{2}/ndf;Counts", nbins, 0.0, max_x)
# tmp_hist.GetYaxis().SetRangeUser(0.001, 1.1*th1_chi2.GetMaximum())

# tmp_hist.Draw("AXIS")
th1_chi2.Draw("")

ms.DrawPreliminaryInfo("#chi^{2}/ndf from fit")

ms.DrawTargetInfo(nameFormatted, "Data")

ext_fit = ms.GetFitExtension(fit_type, this_fit_name)
name_png = ms.getPlotsFile("Chi2ndf",dataset,"png",ext_fit)
canvas.SaveAs(outputPath+name_png)

# name_pdf = ms.getPlotsFile("PvsNphe_%s"%(this_targ),"","pdf",out_DatOrSim)
# canvas.SaveAs(outputPath+name_pdf)

canvas.Clear()
inputfile.Close()
