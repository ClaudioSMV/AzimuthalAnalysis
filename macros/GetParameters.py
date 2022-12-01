from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
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
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default does not)")
parser.add_option('-v', dest='verbose', action='store_true', default = False, help="Print values")
parser.add_option('-Z', dest='zoom', action='store_true', default = False, help="Zoom y-axis range (useful for solid target)")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

# saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
dataset_elemts = dataset.split("_")
if options.JLabCluster: rootpath = "JLab_cluster"
fold = options.fold
verbose = options.verbose
zoom = options.zoom

zoom_ext = "" if not zoom else "z"

# list_solid_targets = ["C", "Fe", "Pb"]
list_func_names = ["crossSection"] if fold else ["crossSectionL", "crossSectionR"]
name_ext = "Fold" if len(list_func_names)==1 else "LR"

infoDict = myStyle.getNameFormattedDict(dataset)

nameFormatted = myStyle.getNameFormatted(dataset)
inputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

inputfile = TFile("%sFitFold_%s.root"%(inputPath,nameFormatted),"READ") if fold else TFile("%sFitBothTails_%s.root"%(inputPath,nameFormatted),"READ")

list_of_hists = inputfile.GetListOfKeys().Clone()
for elem in list_of_hists:
    if (elem.ReadObj().Class_Name() != "TH1D"): list_of_hists.Remove(elem)

parameter_A_list = []
parameter_B_list = []
parameter_C_list = []

for e,elem in enumerate(list_func_names):
    parameter_A_hist = TH1D("par_A%i"%e,";Bin;Parameter A [?]", list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    parameter_A_list.append(parameter_A_hist)

    parameter_B_hist = TH1D("par_B%i"%e,";Bin;Parameter B [?]", list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    parameter_B_list.append(parameter_B_hist)

    parameter_C_hist = TH1D("par_C%i"%e,";Bin;Parameter C [?]", list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    parameter_C_list.append(parameter_C_hist)

print("")
print("Target %s"%infoDict["Target"])

index_h = 0
for i_h,h in enumerate(inputfile.GetListOfKeys()):
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_target = h.ReadObj()
        hist_name = h.GetName() # Corr_Reconstru_Q0N0

        bin_name = hist_name.split("_")[2] # Q0N0

        for i_f,f in enumerate(list_func_names):
            this_fit = hist_target.GetFunction(f)
            par0 = this_fit.GetParameter(0)
            par1 = this_fit.GetParameter(1)
            par2 = this_fit.GetParameter(2)

            err0 = this_fit.GetParError(0)
            err1 = this_fit.GetParError(1)
            err2 = this_fit.GetParError(2)

            if verbose:
                print("%s Fit: %s"%(hist_name, f))
                print("Parameters: (%6.2f, %5.2f, %5.2f)"%(par0, par1, par2))
                print("Errors    : (%6.2f, %5.2f, %5.2f)"%(err0, err1, err2))
                print("")

            parameter_A_list[i_f].Fill(bin_name, 0.0)
            parameter_B_list[i_f].Fill(bin_name, 0.0)
            parameter_C_list[i_f].Fill(bin_name, 0.0)

            parameter_A_list[i_f].SetBinContent(index_h+1, par0)
            parameter_B_list[i_f].SetBinContent(index_h+1, par1)
            parameter_C_list[i_f].SetBinContent(index_h+1, par2)

            parameter_A_list[i_f].SetBinError(index_h+1, err0)
            parameter_B_list[i_f].SetBinError(index_h+1, err1)
            parameter_C_list[i_f].SetBinError(index_h+1, err2)
        index_h+=1

print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

### Save parameters
outputPath = myStyle.getOutputDir("Parameters",infoDict["Target"],rootpath)
outputFile = TFile("%s%s_Parameters_%s.root"%(outputPath,nameFormatted,name_ext),"RECREATE")

# canvas.SetLogy(1)
for e,elem in enumerate(list_func_names):
    # sufix_name = "Fold"
    if ("L" in elem): name_ext = "L"
    elif ("R" in elem): name_ext = "R"

    # legend = TLegend(1-myStyle.GetMargin()-0.35,1-myStyle.GetMargin()-0.12, 1-myStyle.GetMargin()-0.05,1-myStyle.GetMargin()-0.02)
    # legend.SetBorderSize(0)
    # # legend.SetFillColor(ROOT.kWhite)
    # legend.SetTextFont(myStyle.GetFont())
    # legend.SetTextSize(myStyle.GetSize()-8)
    # legend.SetFillStyle(0)
    
    min_A = 0.0
    max_A = 14.0e5 if "Fold" in name_ext else  7.0e5
    min_B =-12.0e4 if "Fold" in name_ext else -6.0e4
    max_B =  0.2   if "Fold" in name_ext else  0.1
    min_C = -4.0e4 if "Fold" in name_ext else -2.0e4
    max_C = 10.0e3 if "Fold" in name_ext else  5.0e3

    if zoom and (infoDict["Target"]!="D"):
        # min_A = 0.0
        max_A = 4.0e5 if "Fold" in name_ext else  2.0e5
        min_B =-3.0e4 if "Fold" in name_ext else -1.5e4
        max_B = 0.2   if "Fold" in name_ext else  0.1
        min_C =-5.0e3 if "Fold" in name_ext else -2.5e3
        max_C = 4.0e3 if "Fold" in name_ext else  2.0e3

    ## Save A
    hist_A = parameter_A_list[e]
    hist_A.SetMinimum(min_A)
    hist_A.SetMaximum(max_A)

    hist_A.SetLineWidth(2)
    # hist_A.SetLineColor(ROOT.kBlue)
    # legend.AddEntry(hist_A,"Positive ratio")
    hist_A.Write()
    hist_A.Draw("hist e")

    myStyle.DrawPreliminaryInfo("Parameter A %s"%name_ext)
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    # hist_b_neg = ratio_th1_b_neg_solid_list[e]

    # hist_b_neg.SetLineWidth(2)
    # hist_b_neg.SetLineColor(ROOT.kRed)
    # legend.AddEntry(hist_b_neg,"Negative ratio")

    # hist_b_neg.Draw("hist same")

    # legend.Draw()

    canvas.SaveAs("%s%s-ParameterA_%s%s.gif"%(outputPath,nameFormatted,zoom_ext,name_ext))
    canvas.Clear()
    # legend.Clear()

    ## Save B
    hist_B = parameter_B_list[e]
    hist_B.SetMinimum(min_B)
    hist_B.SetMaximum(max_B)

    hist_B.SetLineWidth(2)
    # hist_B.SetLineColor(ROOT.kBlue)
    hist_B.Write()
    hist_B.Draw("hist e")

    myStyle.DrawPreliminaryInfo("Parameter B %s"%name_ext)
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    canvas.SaveAs("%s%s-ParameterB_%s%s.gif"%(outputPath,nameFormatted,zoom_ext,name_ext))
    canvas.Clear()

    ## Save C
    hist_C = parameter_C_list[e]
    hist_C.SetMinimum(min_C)
    hist_C.SetMaximum(max_C)

    hist_C.SetLineWidth(2)
    # hist_C.SetLineColor(ROOT.kBlue)
    hist_C.Write()
    hist_C.Draw("hist e")

    myStyle.DrawPreliminaryInfo("Parameter C %s"%name_ext)
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    canvas.SaveAs("%s%s-ParameterC_%s%s.gif"%(outputPath,nameFormatted,zoom_ext,name_ext))
    canvas.Clear()

print("Made it to the end!")

outputFile.Write()
outputFile.Close()
inputfile.Close()
