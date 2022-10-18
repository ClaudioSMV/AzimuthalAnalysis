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
dataset_elemts = dataset.split("_")
dataset_D = "D_%s_%s"%(dataset_elemts[1],dataset_elemts[2])
if options.JLabCluster: rootpath = "JLab_cluster"
fold = options.fold
verbose = options.verbose

### Get D (liquid target) info and parameters
inputPath_D = myStyle.getOutputDir("Fit","D",rootpath)
nameFormatted_D = myStyle.getNameFormatted(dataset_D)
inputfile_D = TFile("%sFitFold_%s.root"%(inputPath_D,nameFormatted_D),"READ") if fold else TFile("%sFitBothTails_%s.root"%(inputPath_D,nameFormatted_D),"READ")

# list_solid_targets = ["C", "Fe", "Pb"]
list_func_names = ["crossSection"] if fold else ["crossSectionL", "crossSectionR"]
name_ext = "Fold" if len(list_func_names)==1 else "LR"

infoDict = myStyle.getNameFormattedDict(dataset)

nameFormatted = myStyle.getNameFormatted(dataset)
inputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

inputfile_solid = TFile("%sFitFold_%s.root"%(inputPath,nameFormatted),"READ") if fold else TFile("%sFitBothTails_%s.root"%(inputPath,nameFormatted),"READ")

list_of_hists = inputfile_solid.GetListOfKeys()

ratio_th1_b_list = []
ratio_th1_c_list = []
ratio_th1_b_pos_solid_list = []
ratio_th1_c_pos_solid_list = []
ratio_th1_b_neg_solid_list = []
ratio_th1_c_neg_solid_list = []
for e,elem in enumerate(list_func_names):
    ratio_th1_b = TH1D("f_XD_b%i"%e,";Bin;Ratio (b_{%s}/a_{%s}) / (b_{D}/a_{D})"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    ratio_th1_b_list.append(ratio_th1_b)

    ratio_th1_c = TH1D("f_XD_c%i"%e,";Bin;Ratio (c_{%s}/a_{%s}) / (c_{D}/a_{D})"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    ratio_th1_c_list.append(ratio_th1_c)

    ratio_th1_b_pos_solid = TH1D("f_X_b%i_Pos"%e,";Bin;b_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    ratio_th1_b_pos_solid_list.append(ratio_th1_b_pos_solid)

    ratio_th1_c_pos_solid = TH1D("f_X_c%i_Pos"%e,";Bin;c_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    ratio_th1_c_pos_solid_list.append(ratio_th1_c_pos_solid)

    ratio_th1_b_neg_solid = TH1D("f_X_b%i_Neg"%e,";Bin;b_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    ratio_th1_b_neg_solid_list.append(ratio_th1_b_neg_solid)

    ratio_th1_c_neg_solid = TH1D("f_X_c%i_Neg"%e,";Bin;c_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    ratio_th1_c_neg_solid_list.append(ratio_th1_c_neg_solid)

print("")
print("Target %s"%infoDict["Target"])

for i_h,h in enumerate(list_of_hists):
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_solid = h.ReadObj()
        hist_name = h.GetName()
        hist_D = inputfile_D.Get(hist_name)

        bin_name = hist_name.split("_")[2]

        for i_f,f in enumerate(list_func_names):
            fit_solid = hist_solid.GetFunction(f)
            par0_X = fit_solid.GetParameter(0)
            par1_X = fit_solid.GetParameter(1)
            par2_X = fit_solid.GetParameter(2)

            err0_X = fit_solid.GetParError(0)
            err1_X = fit_solid.GetParError(1)
            err2_X = fit_solid.GetParError(2)

            fit_D = hist_D.GetFunction(f)
            par0_D = fit_D.GetParameter(0)
            par1_D = fit_D.GetParameter(1)
            par2_D = fit_D.GetParameter(2)

            err0_D = fit_D.GetParError(0)
            err1_D = fit_D.GetParError(1)
            err2_D = fit_D.GetParError(2)

            if verbose:
                print("%s Fit: %s"%(hist_name, f))
                print("Solid: (%6.2f, %5.2f, %5.2f)"%(par0_X, par1_X, par2_X))
                print("       (%6.2f, %5.2f, %5.2f)"%(par0_X/par0_X, par1_X/par0_X, par2_X/par0_X))
                print("Liquid: (%6.2f, %5.2f, %5.2f)"%(par0_D, par1_D, par2_D))
                print("        (%6.2f, %5.2f, %5.2f)"%(par0_D/par0_D, par1_D/par0_D, par2_D/par0_D))
                print("Ratio: (%5.2f, %5.2f, %5.2f)"%(par0_X/par0_D, par1_X/par1_D, par2_X/par2_D))
                print("       (%5.2f, %5.2f, %5.2f)"%( (par0_X/par0_X)/(par0_D/par0_D) , (par1_X/par0_X)/(par1_D/par0_D) , (par2_X/par0_X)/(par2_D/par0_D)))
                print("")

            ratio_th1_b_pos_solid_list[i_f].Fill(bin_name, 0.0)
            ratio_th1_b_neg_solid_list[i_f].Fill(bin_name, 0.0)
            ratio_th1_c_pos_solid_list[i_f].Fill(bin_name, 0.0)
            ratio_th1_c_neg_solid_list[i_f].Fill(bin_name, 0.0)

            err10_X = PropErrorDivision(par1_X, err1_X, par0_X, err0_X)
            if (par1_X/par0_X)>0:
                ratio_th1_b_pos_solid_list[i_f].SetBinContent(i_h+1, (par1_X/par0_X))
                ratio_th1_b_pos_solid_list[i_f].SetBinError(i_h+1, err10_X)
            else:
                ratio_th1_b_neg_solid_list[i_f].SetBinContent(i_h+1, abs(par1_X/par0_X))
                ratio_th1_b_neg_solid_list[i_f].SetBinError(i_h+1, err10_X)

            err20_X = PropErrorDivision(par2_X, err2_X, par0_X, err0_X)
            if (par2_X/par0_X)>0:
                ratio_th1_c_pos_solid_list[i_f].SetBinContent(i_h+1, (par2_X/par0_X))
                ratio_th1_c_pos_solid_list[i_f].SetBinError(i_h+1, err20_X)
            else:
                ratio_th1_c_neg_solid_list[i_f].SetBinContent(i_h+1, abs(par2_X/par0_X))
                ratio_th1_c_neg_solid_list[i_f].SetBinError(i_h+1, err20_X)

            ratio_th1_b_list[i_f].Fill(bin_name, 0.0)
            ratio_th1_c_list[i_f].Fill(bin_name, 0.0)

            err10_D = PropErrorDivision(par1_D, err1_D, par0_D, err0_D)
            err1_XD = PropErrorDivision((par1_X/par0_X), err10_X, (par1_D/par0_D), err10_D)
            ratio_th1_b_list[i_f].SetBinContent(i_h+1, (par1_X/par0_X)/(par1_D/par0_D))
            ratio_th1_b_list[i_f].SetBinError(i_h+1, err1_XD)

            err20_D = PropErrorDivision(par2_D, err2_D, par0_D, err0_D)
            err2_XD = PropErrorDivision((par2_X/par0_X), err20_X, (par2_D/par0_D), err20_D)
            ratio_th1_c_list[i_f].SetBinContent(i_h+1, (par2_X/par0_X)/(par2_D/par0_D))
            ratio_th1_c_list[i_f].SetBinError(i_h+1, err2_XD)

print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

### Ratio b/a and c/a per target
outputPath = myStyle.getOutputDir("ParameterRatio",infoDict["Target"],rootpath)
outputFile = TFile("%s%s_ParameterRatio_%s.root"%(outputPath,nameFormatted,name_ext),"RECREATE")

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
    hist_b_pos = ratio_th1_b_pos_solid_list[e]
    hist_b_pos.SetMinimum(ymin)
    hist_b_pos.SetMaximum(ymax)

    hist_b_pos.SetLineWidth(2)
    hist_b_pos.SetLineColor(ROOT.kBlue)
    legend_b.AddEntry(hist_b_pos,"Positive ratio")

    hist_b_pos.Write()
    hist_b_pos.Draw("hist e")

    hist_b_neg = ratio_th1_b_neg_solid_list[e]

    hist_b_neg.SetLineWidth(2)
    hist_b_neg.SetLineColor(ROOT.kRed)
    legend_b.AddEntry(hist_b_neg,"Negative ratio")

    hist_b_neg.Write()
    hist_b_neg.Draw("hist e same")

    legend_b.Draw()
    myStyle.DrawPreliminaryInfo("Parameters ratio %s"%name_ext)
    myStyle.DrawTargetInfo(nameFormatted, "Data")
    canvas.SaveAs("%s%s-Ratio%s_b.gif"%(outputPath,nameFormatted,name_ext))
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
    hist_c_pos = ratio_th1_c_pos_solid_list[e]
    hist_c_pos.SetMinimum(ymin)
    hist_c_pos.SetMaximum(ymax)

    hist_c_pos.SetLineWidth(2)
    hist_c_pos.SetLineColor(ROOT.kBlue)
    legend_c.AddEntry(hist_c_pos,"Positive ratio")

    hist_c_pos.Write()
    hist_c_pos.Draw("hist e")

    hist_c_neg = ratio_th1_c_neg_solid_list[e]

    hist_c_neg.SetLineWidth(2)
    hist_c_neg.SetLineColor(ROOT.kRed)
    legend_c.AddEntry(hist_c_neg,"Negative ratio")

    hist_c_neg.Write()
    hist_c_neg.Draw("hist e same")

    legend_c.Draw()
    myStyle.DrawPreliminaryInfo("Parameters ratio %s"%name_ext)
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    canvas.SaveAs("%s%s-Ratio%s_c.gif"%(outputPath,nameFormatted,name_ext))
    canvas.Clear()

### Ratio of the ratios b/a and c/a -> Solid target / D target
if "D" not in dataset:
    # canvas.SetLogy(0)
    for e,elem in enumerate(list_func_names):
        # sufix_name = "Fold"
        # if ("L" in elem): sufix_name = "L"
        # elif ("R" in elem): sufix_name = "R"

        if ("L" in elem): name_ext = "L"
        elif ("R" in elem): name_ext = "R"

        hist_b = ratio_th1_b_list[e]
        hist_b.SetMinimum(ymin)
        hist_b.SetMaximum(2*ymax)

        hist_b.Write()
        hist_b.Draw("hist e")

        myStyle.DrawPreliminaryInfo("Parameters ratio %s"%name_ext)
        myStyle.DrawTargetInfo(nameFormatted, "Data")

        canvas.SaveAs("%s%s-RatioOverD_%s_b.gif"%(outputPath,nameFormatted,name_ext))
        canvas.Clear()

        hist_c = ratio_th1_c_list[e]
        hist_c.SetMinimum(ymin)
        hist_c.SetMaximum(2*ymax)

        hist_c.Write()
        hist_c.Draw("hist e")

        myStyle.DrawPreliminaryInfo("Parameters ratio %s"%name_ext)
        myStyle.DrawTargetInfo(nameFormatted, "Data")

        canvas.SaveAs("%s%s-RatioOverD_%s_c.gif"%(outputPath,nameFormatted,name_ext))
        canvas.Clear()

print("Made it to the end!")

outputFile.Write()
outputFile.Close()
inputfile_solid.Close()
inputfile_D.Close()
