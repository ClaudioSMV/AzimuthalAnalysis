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

# gStyle.SetStatX(2*myStyle.GetMargin() + 0.005 + gStyle.GetStatW())
# gStyle.SetStatY(1 - myStyle.GetMargin() - 0.005)

gStyle.SetStatX(1 - myStyle.GetMargin() - 0.005)
gStyle.SetStatY(2*myStyle.GetMargin() + 0.205)

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default does not)")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

# saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
dataset_elemts = dataset.split("_")
if (len(dataset_elemts)==3):
    dataset = "%s_%s"%(dataset_elemts[1],dataset_elemts[2])
if options.JLabCluster: rootpath = "JLab_cluster"
fold = options.fold

### Get D (liquid target) info and parameters
inputPath_D = myStyle.getOutputDir("Fit","D",rootpath)
nameFormatted_D = myStyle.getNameFormatted("_%s"%dataset)
inputfile_D = TFile("%sFitFold_D%s.root"%(inputPath_D,nameFormatted_D),"READ") if fold else TFile("%sFitBothTails_D%s.root"%(inputPath_D,nameFormatted_D),"READ")

list_solid_targets = ["C", "Fe", "Pb"]
list_func_names = ["crossSection"] if fold else ["crossSectionL", "crossSectionR"]

for t in list_solid_targets:
    infoDict = myStyle.getNameFormattedDict("%s_%s"%(t, dataset))

    nameFormatted = myStyle.getNameFormatted("%s_%s"%(t, dataset))
    inputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

    inputfile_solid = TFile("%sFitFold_%s.root"%(inputPath,nameFormatted),"READ") if fold else TFile("%sFitBothTails_%s.root"%(inputPath,nameFormatted),"READ")

    list_of_hists = inputfile_solid.GetListOfKeys()

    print("")
    print("Target %s"%t)

    for h in list_of_hists:
        if (h.ReadObj().Class_Name() == "TH1D"):
            hist_solid = h.ReadObj()
            hist_D = inputfile_D.Get(h.GetName())

            for f in list_func_names:
                fit_solid = hist_solid.GetFunction(f)
                par0_X = fit_solid.GetParameter(0)
                par1_X = fit_solid.GetParameter(1)
                par2_X = fit_solid.GetParameter(2)

                fit_D = hist_D.GetFunction(f)
                par0_D = fit_D.GetParameter(0)
                par1_D = fit_D.GetParameter(1)
                par2_D = fit_D.GetParameter(2)

                print("%s Fit: %s"%(h.GetName(), f))
                print("Solid: (%6.2f, %5.2f, %5.2f)"%(par0_X, par1_X, par2_X))
                print("Liquid: (%6.2f, %5.2f, %5.2f)"%(par0_D, par1_D, par2_D))
                print("Ratio: (%5.2f, %5.2f, %5.2f)"%(par0_X/par0_D, par1_X/par1_D, par2_X/par2_D))
                print("")

    inputfile_solid.Close()
    print("")

inputfile_D.Close()



# infoDict = myStyle.getNameFormattedDict(dataset)

# # inputPath = myStyle.getInputFile("Correction",dataset,rootpath) # Corrected_Fe_B0_2D.root
# # inputfile = TFile(inputPath,"READ")

# nameFormatted = myStyle.getNameFormatted(dataset)
# inputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

# inputfile_solid = TFile("%sFitFold_%s.root"%(inputPath,nameFormatted),"READ") if fold else TFile("%sFitBothTails_%s.root"%(inputPath,nameFormatted),"READ")




# inputPath = myStyle.getOutputDir("Correction",infoDict["Target"],rootpath)
# nameFormatted = myStyle.getNameFormatted(dataset)
# inputfile = TFile(inputPath+nameFormatted+".root","READ")

# outputPath = myStyle.getOutputDir("Fit",infoDict["Target"],rootpath)

# list_of_hists = inputfile.GetListOfKeys()

# canvas = TCanvas("cv","cv",1000,800)
# gStyle.SetOptStat(0)

# outputfile = TFile("%sFitBothTails_%s.root"%(outputPath,nameFormatted),"RECREATE")

# for h in list_of_hists:
#     if (h.ReadObj().Class_Name() == "TH1D"):
#         if "Corr" in h.GetName():
#             # if "PQ" in h.GetName(): continue
#             # if not isData and "reco" in h.GetName(): continue

#             # Name format is: Corr_Reconstructed_Q0N0
#             tmp_txt = h.GetName().split("_")[2] # Q0N0

#             var1 = tmp_txt[0] # Q
#             var2 = tmp_txt[2] # N
#             # type_hist = correct_prefix[tmp_txt[2]]

#             hist = h.ReadObj()
#             hist.SetMinimum(0.0001)
#             ylim = hist.GetMaximum()*1.4
#             hist.SetMaximum(ylim)

#             ### Get limit of the fit just before the central peak
#             ## Left (Negative)
#             hist.GetXaxis().SetRangeUser(-45.0, 0.0)
#             limit_bin_L = hist.GetMinimumBin()
#             fit_min_limit_L = hist.GetBinCenter(limit_bin_L)
#             hist.GetXaxis().UnZoom()

#             ## Right (Positive)
#             hist.GetXaxis().SetRangeUser(0.0, 45.0)
#             limit_bin_R = hist.GetMinimumBin()
#             fit_min_limit_R = hist.GetBinCenter(limit_bin_R)
#             hist.GetXaxis().UnZoom()

#             hist.GetXaxis().SetTitle("#phi_{PQ} (deg)")
#             hist.GetYaxis().SetTitle("Counts")

#             hist.Draw("hist axis")

#             fit_funct_left  = TF1("crossSectionL","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)", -180.0,fit_min_limit_L)
#             fit_funct_right = TF1("crossSectionR","[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)",  fit_min_limit_R, 180.0)

#             hist.Fit("crossSectionL", "Q", "",        -180.0,fit_min_limit_L)
#             hist.Fit("crossSectionR", "Q+ sames", "", fit_min_limit_R, 180.0)

#             hist.Draw("FUNC same")

#             hist.Write()

#             myStyle.DrawPreliminaryInfo("Correction fit")
#             myStyle.DrawTargetInfo(nameFormatted, "Data")
#             myStyle.DrawBinInfo(tmp_txt)

#             #### UPDATE ADDING CHI-SQUARE AND GOODNESS OF FIT!

#             canvas.SaveAs(outputPath+"FitBothTails_"+nameFormatted+"_"+tmp_txt+".gif")
#             canvas.Clear()

# outputfile.Close()
