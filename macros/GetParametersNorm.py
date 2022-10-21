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

# gStyle.SetStatX(1 - myStyle.GetMargin() - 0.005)
# gStyle.SetStatY(2*myStyle.GetMargin() + 0.205)

def PropErrorDivision(v1, e1, v2, e2):
    this_error = TMath.Abs(v1/v2)*TMath.Sqrt((e1/v1)*(e1/v1) + (e2/v2)*(e2/v2)) # Assuming they both are uncorrelated
    return this_error

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default does not)")
parser.add_option('-v', dest='verbose', action='store_true', default = False, help="Print values")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

# saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
fold = options.fold
verbose = options.verbose

infoDict = myStyle.getNameFormattedDict(dataset) # ["Target", "BinningType", "NDims", "Cuts"]
nameFormatted = myStyle.getNameFormatted(dataset)

if options.JLabCluster: rootpath = "JLab_cluster"

# list_solid_targets = ["C", "Fe", "Pb"]
list_func_names = ["crossSection"] if fold else ["crossSectionL", "crossSectionR"]
name_ext = "Fold" if len(list_func_names)==1 else "LR"

inputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

inputfile = TFile("%sFitFold_%s.root"%(inputPath,nameFormatted),"READ") if fold else TFile("%sFitBothTails_%s.root"%(inputPath,nameFormatted),"READ")

list_of_hists = inputfile.GetListOfKeys()

th1_b_norm_pos_list = []
th1_b_norm_neg_list = []
th1_c_norm_pos_list = []
th1_c_norm_neg_list = []
for e,elem in enumerate(list_func_names):
    th1_b_norm_pos = TH1D("f_Norm_B%i_Pos"%e,";Bin;b_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    th1_b_norm_pos_list.append(th1_b_norm_pos)

    th1_b_norm_neg = TH1D("f_Norm_B%i_Neg"%e,";Bin;b_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    th1_b_norm_neg_list.append(th1_b_norm_neg)

    th1_c_norm_pos = TH1D("f_Norm_C%i_Pos"%e,";Bin;c_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    th1_c_norm_pos_list.append(th1_c_norm_pos)

    th1_c_norm_neg = TH1D("f_Norm_C%i_Neg"%e,";Bin;c_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    th1_c_norm_neg_list.append(th1_c_norm_neg)

print("")
print("Target %s"%infoDict["Target"])

for i_h,h in enumerate(list_of_hists):
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_targ = h.ReadObj()
        hist_name = h.GetName()

        bin_name = hist_name.split("_")[2]

        for i_f,f in enumerate(list_func_names):
            fit_targ = hist_targ.GetFunction(f)
            par0 = fit_targ.GetParameter(0)
            par1 = fit_targ.GetParameter(1)
            par2 = fit_targ.GetParameter(2)

            err0 = fit_targ.GetParError(0)
            err1 = fit_targ.GetParError(1)
            err2 = fit_targ.GetParError(2)

            if verbose:
                print("%s Fit: %s"%(hist_name, f))
                print("Solid     : (%6.2f, %5.2f, %5.2f)"%(par0, par1, par2))
                print("Normalized: (%6.2f, %5.2f, %5.2f)"%(par0/par0, par1/par0, par2/par0))
                print("")

            # Fill norm hists with the name (string as label per bin)
            th1_b_norm_pos_list[i_f].Fill(bin_name, 0.0)
            th1_b_norm_neg_list[i_f].Fill(bin_name, 0.0)
            th1_c_norm_pos_list[i_f].Fill(bin_name, 0.0)
            th1_c_norm_neg_list[i_f].Fill(bin_name, 0.0)

            # Get error propagated and fill B/A
            err10 = PropErrorDivision(par1, err1, par0, err0)
            if (par1/par0)>0:
                th1_b_norm_pos_list[i_f].SetBinContent(i_h+1, (par1/par0))
                th1_b_norm_pos_list[i_f].SetBinError(i_h+1, err10)
            else:
                th1_b_norm_neg_list[i_f].SetBinContent(i_h+1, abs(par1/par0))
                th1_b_norm_neg_list[i_f].SetBinError(i_h+1, err10)

            # Get error propagated and fill C/A
            err20 = PropErrorDivision(par2, err2, par0, err0)
            if (par2/par0)>0:
                th1_c_norm_pos_list[i_f].SetBinContent(i_h+1, (par2/par0))
                th1_c_norm_pos_list[i_f].SetBinError(i_h+1, err20)
            else:
                th1_c_norm_neg_list[i_f].SetBinContent(i_h+1, abs(par2/par0))
                th1_c_norm_neg_list[i_f].SetBinError(i_h+1, err20)


print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

### Ratio b/a and c/a per target
outputPath = myStyle.getOutputDir("Parameters",infoDict["Target"],rootpath)
outputFile = TFile("%s%s_ParametersNorm_%s.root"%(outputPath,nameFormatted,name_ext),"RECREATE")

ymin = 0.001
ymax = 1.2
# canvas.SetLogy(0)
for e,elem in enumerate(list_func_names):
    # sufix_name = "Fold"
    # if ("L" in elem): sufix_name = "L"
    # elif ("R" in elem): sufix_name = "R"

    if ("L" in elem): name_ext = "L"
    elif ("R" in elem): name_ext = "R"

    ## Ratio b/a
    legend_b = TLegend(1-myStyle.GetMargin()-0.35,1-myStyle.GetMargin()-0.12, 1-myStyle.GetMargin()-0.05,1-myStyle.GetMargin()-0.02)
    legend_b.SetBorderSize(0)
    # legend_b.SetFillColor(ROOT.kWhite)
    legend_b.SetTextFont(myStyle.GetFont())
    legend_b.SetTextSize(myStyle.GetSize()-8)
    legend_b.SetFillStyle(0)
    ## Positive ratios
    hist_b_pos = th1_b_norm_pos_list[e]
    hist_b_pos.SetMinimum(ymin)
    hist_b_pos.SetMaximum(ymax)

    hist_b_pos.SetLineWidth(2)
    hist_b_pos.SetLineColor(ROOT.kBlue)
    legend_b.AddEntry(hist_b_pos,"Positive ratio")

    hist_b_pos.Write()
    hist_b_pos.Draw("hist e")

    hist_b_neg = th1_b_norm_neg_list[e]

    hist_b_neg.SetLineWidth(2)
    hist_b_neg.SetLineColor(ROOT.kRed)
    legend_b.AddEntry(hist_b_neg,"Negative ratio")

    hist_b_neg.Write()
    hist_b_neg.Draw("hist e same")

    legend_b.Draw()
    myStyle.DrawPreliminaryInfo("Parameters normalized %s"%(name_ext))
    myStyle.DrawTargetInfo(nameFormatted, "Data")
    canvas.SaveAs("%s%s-ParNorm%s_b.gif"%(outputPath,nameFormatted,name_ext))
    canvas.Clear()

    ## Ratio c/a
    # legend_c = TLegend()
    legend_c = TLegend(1-myStyle.GetMargin()-0.35,1-myStyle.GetMargin()-0.12, 1-myStyle.GetMargin()-0.05,1-myStyle.GetMargin()-0.02)
    legend_c.SetBorderSize(0)
    # legend_c.SetFillColor(ROOT.kWhite)
    legend_c.SetTextFont(myStyle.GetFont())
    legend_c.SetTextSize(myStyle.GetSize()-8)
    legend_c.SetFillStyle(0)
    ## Positive ratios
    hist_c_pos = th1_c_norm_pos_list[e]
    hist_c_pos.SetMinimum(ymin)
    hist_c_pos.SetMaximum(ymax)

    hist_c_pos.SetLineWidth(2)
    hist_c_pos.SetLineColor(ROOT.kBlue)
    legend_c.AddEntry(hist_c_pos,"Positive ratio")

    hist_c_pos.Write()
    hist_c_pos.Draw("hist e")

    hist_c_neg = th1_c_norm_neg_list[e]

    hist_c_neg.SetLineWidth(2)
    hist_c_neg.SetLineColor(ROOT.kRed)
    legend_c.AddEntry(hist_c_neg,"Negative ratio")

    hist_c_neg.Write()
    hist_c_neg.Draw("hist e same")

    legend_c.Draw()
    myStyle.DrawPreliminaryInfo("Parameters normalized %s"%(name_ext))
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    canvas.SaveAs("%s%s-ParNorm%s_c.gif"%(outputPath,nameFormatted,name_ext))
    canvas.Clear()

outputFile.Write()
outputFile.Close()

print("Made it to the end!")

inputfile.Close()
