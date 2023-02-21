from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle
import math

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
myStyle.ForceStyle()
# gStyle.SetPadRightMargin(2*myStyle.GetMargin())
# gStyle.SetLabelSize(myStyle.GetSize()-10,"z")
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

infoDict = myStyle.getDictNameFormat(dataset)
# nameFormatted = myStyle.getNameFormatted(dataset,True)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
# if options.errorFull:
#     input_cuts+="_FE"
#     plots_cuts+="_FE"

## Input
inputPath = myStyle.getOutputFileWithPath("Acceptance", dataset, input_cuts, isJLab, False) # "../output/"
inputfile = TFile(inputPath,"READ")

## Output
outputPath = myStyle.getPlotsFolder("Resolution", plots_cuts, infoDict["Target"], isJLab)
# outputROOT = myStyle.getPlotsFile("Resolution", dataset, "root")

### Fit from res<var> histograms (<var> - <mc_var>)
canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
gStyle.SetOptFit()

list_vars = ["Q2", "Nu", "Zh", "Pt2", "PhiPQ"]
list_vars_axistitle = ["Q^{2}", "#nu", "Z_{h}", "P_{t}^{2}", "#phi_{PQ}"]
list_vars_axisunits = ["(GeV^{2})", "(GeV)", "", "(GeV^{2})", "(deg)"]

for i,this_var in enumerate(list_vars):
    this_res_hist = inputfile.Get("res%s"%this_var)

    myMean = this_res_hist.GetMean()
    myRMS  = this_res_hist.GetRMS()
    fit = TF1('fit','gaus',myMean-1.3*myRMS,myMean+1.3*myRMS)
    this_res_hist.Fit(fit,"Q","",myMean-1.3*myRMS,myMean+1.3*myRMS)

    this_res_hist.Draw("hist e")
    fit.Draw("same")

    myStyle.DrawPreliminaryInfo("Resolution")
    myStyle.DrawTargetInfo(infoDict["Target"], "Simulation")

    outputName = myStyle.getPlotsFile("Resolution1D", dataset, "png",this_var)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()

    this_migr_2d = inputfile.Get("histMigrationMatrix%s"%this_var)
    Nbins = this_migr_2d.GetXaxis().GetNbins()

    res_vs_X = TH1D("ResolutionVsX%s"%this_var, "Resolution Vs X;True %s %s;Resolution %s"%(list_vars_axistitle[i],list_vars_axisunits[i],list_vars_axisunits[i]), Nbins, this_migr_2d.GetXaxis().GetXmin(), this_migr_2d.GetXaxis().GetXmax())

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
            # if (debugMode):
            #     tmpHist.Draw("hist")
            #     fit.Draw("same")
            #     canvas.SaveAs(outdir_q+"q_"+info.outHistoName+str(i)+".png")
            #     print ("Bin : " + str(i) + " (x = %.3f"%(info.th1.GetXaxis().GetBinCenter(i)) +") -> Resolution: %.3f +/- %.3f"%(value, error))

        else:
            print("Bin %i doesn't have enough statistics."%b)
            value = 0.0
            error = 0.0

        res_vs_X.SetBinContent(b,value)
        res_vs_X.SetBinError(b,error)

    res_vs_X.GetYaxis().SetRangeUser(0.0, 1.2*res_vs_X.GetMaximum())
    res_vs_X.Draw("hist e")
    myStyle.DrawPreliminaryInfo("Resolution vs x")
    myStyle.DrawTargetInfo(infoDict["Target"], "Simulation")

    outputName = myStyle.getPlotsFile("ResolutionVsX", dataset, "png",this_var)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()

inputfile.Close()
