from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
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
# gStyle.SetLabelSize(ms.get_size()-10,"z")
# gROOT.ForceStyle()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

infoDict = ms.get_name_dict(dataset)
# nameFormatted = ms.get_name_format(dataset,True)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

## Input
inputPath = ms.get_output_fullpath("Acceptance", dataset, input_cuts, isJLab, False) # "../output/"
inputfile = TFile(inputPath,"READ")

## Output
outputPath = ms.get_plots_folder("Resolution", plots_cuts, dataset, isJLab)
# outputROOT = ms.get_plots_file("Resolution", dataset, "root")

list_vars = ["Q2", "Nu", "Xb", "Zh", "Pt2", "PhiPQ"]

fit_limits = {  "Q2": [-0.9,1.1], "Nu": [-1.1,0.8], "Xb": [-0.8,1.0],
                "Zh": [-0.9,1.0], "Pt2": [-0.8,0.8], "PhiPQ": [-1.1,1.1]}

### Fit from res<var> histograms (<var> - <mc_var>)
canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
gStyle.SetOptFit()

for this_var in list_vars:
    # Skip Xb or Nu when not in the file
    if (not inputfile.Get("res%s"%this_var)):
        continue

    this_key = ms.varname2key[this_var]
    this_axis = ms.axis_label(this_key, "LatexUnit")
    this_ltex = ms.axis_label(this_key, "Latex")
    this_unit = ms.axis_label(this_key, "Unit")

    # Hist 1D
    fmin = fit_limits[this_var][0]
    fmax = fit_limits[this_var][1]

    this_res_hist = inputfile.Get("res%s"%this_var)

    myMean = this_res_hist.GetMean()
    myRMS  = this_res_hist.GetRMS()
    fit = TF1('fit','gaus',myMean+fmin*myRMS,myMean+fmax*myRMS)
    this_res_hist.Fit(fit,"Q","",myMean+fmin*myRMS,myMean+fmax*myRMS)

    this_res_hist.GetXaxis().SetTitle("{0} - mc_{0} {1}".format(this_ltex, this_unit))
    this_res_hist.Draw("hist e")
    fit.Draw("same")

    ms.draw_preliminary("Resolution")
    ms.draw_targetinfo(infoDict["Target"], "Simulation")

    outputName = ms.get_plots_file("Resolution1D", dataset, "png",this_var)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()

    # Hisy 2D-Projection
    this_migr_2d = inputfile.Get("histMigrationMatrix%s"%this_var)
    Nbins = this_migr_2d.GetXaxis().GetNbins()

    res_vs_X = TH1D("ResolutionVsX%s"%this_var, "Resolution Vs X;True %s;Resolution %s"%(this_axis,this_unit), Nbins, this_migr_2d.GetXaxis().GetXmin(), this_migr_2d.GetXaxis().GetXmax())

    for b in range(0, Nbins+1):
        totalEvents = this_migr_2d.GetEntries()
        tmpHist = this_migr_2d.ProjectionY("py",b,b)
        myMean = tmpHist.GetMean()
        myRMS = tmpHist.GetRMS()
        myRMSError = tmpHist.GetRMSError()
        nEvents = tmpHist.GetEntries()
        fitlow = myMean - 1.3*myRMS
        fithigh = myMean + 1.3*myRMS
        value = myRMS
        error = myRMSError

        minEvtsCut = totalEvents/Nbins

        if (nEvents > 0.05*minEvtsCut):
            fit = TF1('fit','gaus',fitlow,fithigh)
            tmpHist.Fit(fit,"Q", "", fitlow, fithigh)
            myMPV = fit.GetParameter(1)
            mySigma = fit.GetParameter(2)
            mySigmaError = fit.GetParError(2)
            value = mySigma
            error = mySigmaError
            
            # ##For Debugging
            # if (True):
            #     tmpHist.Draw("hist")
            #     fit.Draw("same")
            #     canvas.SaveAs("%sq_%s_%i.png"%(outputPath,this_var,b))
            #     print ("Bin : " + str(b) + " (%s = %.3f"%(this_var,this_migr_2d.GetXaxis().GetBinCenter(b)) +") -> Resolution: %.3f +/- %.3f"%(value, error))

        else:
            print("Bin %i doesn't have enough statistics."%b)
            value = 0.0
            error = 0.0

        res_vs_X.SetBinContent(b,value)
        res_vs_X.SetBinError(b,error)

    res_vs_X.GetYaxis().SetRangeUser(0.0, 1.2*res_vs_X.GetMaximum())
    res_vs_X.Draw("hist e")
    ms.draw_preliminary("Resolution vs x")
    ms.draw_targetinfo(infoDict["Target"], "Simulation")

    outputName = ms.get_plots_file("ResolutionVsX", dataset, "png",this_var)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()

inputfile.Close()
