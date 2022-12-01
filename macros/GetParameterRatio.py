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

def PropErrorDivision(v1, e1, v2, e2, cov=0):
    this_error = TMath.Abs(v1/v2)*TMath.Sqrt((e1/v1)*(e1/v1) + (e2/v2)*(e2/v2) - 2*cov/(v1*v2))
    return this_error

def GetMatrixElem(matrix, row, col):
    this_matrix = matrix.GetMatrixArray()
    index = col + 3*row
    return this_matrix[index]

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default does not)")
parser.add_option('-v', dest='verbose', action='store_true', default = False, help="Print values")
parser.add_option('-m', dest='mixD', action='store_true', default = False, help="Mix deuterium data from all solid targets")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

# saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
fold = options.fold
verbose = options.verbose
mixD = options.mixD

infoDict = myStyle.getNameFormattedDict(dataset) # ["Target", "BinningType", "NDims", "Cuts"]
nameFormatted = myStyle.getNameFormatted(dataset)

if ("D" in infoDict["Target"]):
    print("Can't get ratio of D. Try with a solid target.")
    exit()

solid_mix = "" if mixD else infoDict["Target"]
hadronic_bin_name = ""
if "Z" in infoDict["Cuts"]: hadronic_bin_name = "_Z"
if "P" in infoDict["Cuts"]: hadronic_bin_name = "_P"
# dataset_elemts = dataset.split("_")
dataset_D = "D%s_%s_%s%s"%(solid_mix,infoDict["BinningType"],infoDict["NDims"],hadronic_bin_name)
if options.JLabCluster: rootpath = "JLab_cluster"
ext_error = "_FullErr" if options.errorFull else ""

### Get D (liquid target) info and parameters
inputPath_D = myStyle.getOutputDir("Fit","D%s"%(solid_mix),rootpath)
nameFormatted_D = myStyle.getNameFormatted(dataset_D)
inputfile_D = TFile("%sFitFold_%s%s.root"%(inputPath_D,nameFormatted_D,ext_error),"READ") if fold else TFile("%sFitBothTails_%s%s.root"%(inputPath_D,nameFormatted_D,ext_error),"READ")

# list_solid_targets = ["C", "Fe", "Pb"]
list_func_names = ["crossSection"] if fold else ["crossSectionL", "crossSectionR"]
name_ext = "Fold" if len(list_func_names)==1 else "LR"

inputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

inputfile_solid = TFile("%sFitFold_%s%s.root"%(inputPath,nameFormatted,ext_error),"READ") if fold else TFile("%sFitBothTails_%s%s.root"%(inputPath,nameFormatted,ext_error),"READ")

list_of_hists = inputfile_solid.GetListOfKeys().Clone()
for elem in list_of_hists:
    if (elem.ReadObj().Class_Name() != "TH1D"): list_of_hists.Remove(elem)

ratio_th1_b_list = []
ratio_th1_c_list = []
for e,elem in enumerate(list_func_names):
    ratio_th1_b = TH1D("f_ratio_B%i"%e,";Bin;Ratio (b_{%s}/a_{%s}) / (b_{D}/a_{D})"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    ratio_th1_b_list.append(ratio_th1_b)

    ratio_th1_c = TH1D("f_ratio_C%i"%e,";Bin;Ratio (c_{%s}/a_{%s}) / (c_{D}/a_{D})"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    ratio_th1_c_list.append(ratio_th1_c)

print("")
print("Target %s"%infoDict["Target"])

index_h = 0
for i_h,h in enumerate(inputfile_solid.GetListOfKeys()):
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_solid = h.ReadObj()
        hist_name = h.GetName()
        hist_D = inputfile_D.Get(hist_name) # Corr_Reconstru_Q0N0Z0_fold

        bin_name = hist_name.split("_")[2] # Q0N0Z0

        # Get covariance matrix
        cov_matrix_X = inputfile_solid.Get("%s_covM"%(bin_name))
        cov_matrix_D = inputfile_D.Get("%s_covM"%(bin_name))

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

            ratio_th1_b_list[i_f].Fill(bin_name, 0.0)
            ratio_th1_c_list[i_f].Fill(bin_name, 0.0)

            # Get error propagated and fill B/A
            cov10_X = GetMatrixElem(cov_matrix_X, 0, 1) # Get Cov AB
            cov10_D = GetMatrixElem(cov_matrix_D, 0, 1) # Get Cov AB

            err10_X = PropErrorDivision(par1_X, err1_X, par0_X, err0_X, cov10_X)
            err10_D = PropErrorDivision(par1_D, err1_D, par0_D, err0_D, cov10_D)
            err1_XD = PropErrorDivision((par1_X/par0_X), err10_X, (par1_D/par0_D), err10_D)
            ratio_th1_b_list[i_f].SetBinContent(index_h+1, (par1_X/par0_X)/(par1_D/par0_D))
            ratio_th1_b_list[i_f].SetBinError(index_h+1, err1_XD)

            # Get error propagated and fill C/A
            cov20_X = GetMatrixElem(cov_matrix_X, 0, 2) # Get Cov AC
            cov20_D = GetMatrixElem(cov_matrix_D, 0, 2) # Get Cov AC

            err20_X = PropErrorDivision(par2_X, err2_X, par0_X, err0_X, cov20_X)
            err20_D = PropErrorDivision(par2_D, err2_D, par0_D, err0_D, cov20_D)
            err2_XD = PropErrorDivision((par2_X/par0_X), err20_X, (par2_D/par0_D), err20_D)
            ratio_th1_c_list[i_f].SetBinContent(index_h+1, (par2_X/par0_X)/(par2_D/par0_D))
            ratio_th1_c_list[i_f].SetBinError(index_h+1, err2_XD)
        index_h+=1

print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

### Ratio of the ratios b/a and c/a -> Solid target / D target
outputPath = myStyle.getOutputDir("ParameterRatio",infoDict["Target"],rootpath)
outputFile = TFile("%s%s_ParameterRatio_D%s_%s%s.root"%(outputPath,nameFormatted,solid_mix,name_ext,ext_error),"RECREATE")
# canvas.SetLogy(0)

ymin = 0.001
ymax = 1.2
for e,elem in enumerate(list_func_names):
    if ("L" in elem): name_ext = "L"
    elif ("R" in elem): name_ext = "R"

    hist_b = ratio_th1_b_list[e]
    hist_b.SetMinimum(ymin)
    hist_b.SetMaximum(2*ymax)

    hist_b.Write()
    hist_b.Draw("hist e")

    myStyle.DrawPreliminaryInfo("Parameters ratio D%s %s"%(solid_mix,name_ext))
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    canvas.SaveAs("%s%s-RatioOverD%s_%s_b%s.gif"%(outputPath,nameFormatted,solid_mix,name_ext,ext_error))
    canvas.Clear()

    hist_c = ratio_th1_c_list[e]
    hist_c.SetMinimum(ymin)
    hist_c.SetMaximum(2*ymax)

    hist_c.Write()
    hist_c.Draw("hist e")

    myStyle.DrawPreliminaryInfo("Parameters ratio D%s %s"%(solid_mix,name_ext))
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    canvas.SaveAs("%s%s-RatioOverD%s_%s_c%s.gif"%(outputPath,nameFormatted,solid_mix,name_ext,ext_error))
    canvas.Clear()

outputFile.Write()
outputFile.Close()

print("Made it to the end!")

inputfile_solid.Close()
inputfile_D.Close()
