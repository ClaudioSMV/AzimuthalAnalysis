from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
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
# gStyle.SetPadRightMargin(2*myStyle.GetMargin())
# gStyle.SetLabelSize(myStyle.GetSize()-10,"z")
# gROOT.ForceStyle()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
if options.JLabCluster: rootpath = "JLab_cluster"

infoDict = myStyle.getNameFormattedDict(dataset)
inputPath = myStyle.getInputFile("Acceptance",dataset,rootpath) # Acceptance_%s_B%i.root
inputfile = TFile(inputPath,"READ")

outputPath = myStyle.getOutputDir("Resolution",infoDict["Target"],rootpath)

### Fit from res<var> histograms (<var> - <mc_var>)
canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
gStyle.SetOptFit()

list_vars = myStyle.kin_vars_list[0]
list_vars_axistitle = myStyle.kin_vars_list[1]
list_vars_axisunits = myStyle.kin_vars_list[2]

for i,v in enumerate(list_vars):
    this_res_hist = inputfile.Get("res%s"%v)

    myMean = this_res_hist.GetMean()
    myRMS  = this_res_hist.GetRMS()
    fit = TF1('fit','gaus',myMean-2*myRMS,myMean+2*myRMS)
    this_res_hist.Fit(fit,"","",myMean-2*myRMS,myMean+2*myRMS)

    this_res_hist.Draw("hist e")
    fit.Draw("same")

    myStyle.DrawPreliminaryInfo("Resolution")
    myStyle.DrawTargetInfo(infoDict["Target"], "Simulation")

    canvas.SaveAs("%sRes1D_%s.gif"%(outputPath,v))
    # canvas.SaveAs("%sRes1D_%s.pdf"%(outputPath,v))
    canvas.Clear()

    this_migr_2d = inputfile.Get("histMigrationMatrix%s"%v)
    Nbins = this_migr_2d.GetXaxis().GetNbins()

    res_vs_X = TH1D("Res_Vs_X_%s"%v, "Res Vs X;%s %s;Resolution %s"%(list_vars_axistitle[i],list_vars_axisunits[i],list_vars_axisunits[i]), Nbins, this_migr_2d.GetXaxis().GetXmin(), this_migr_2d.GetXaxis().GetXmax())

    for b in range(0, Nbins+1):
        totalEvents = this_migr_2d.GetEntries()
        tmpHist = this_migr_2d.ProjectionY("py",b,b)
        myMean = tmpHist.GetMean()
        myRMS = tmpHist.GetRMS()
        myRMSError = tmpHist.GetRMSError()
        nEvents = tmpHist.GetEntries()
        fitlow = myMean - 1.5*myRMS
        fithigh = myMean + 1.5*myRMS
        value = myRMS
        error = myRMSError

        minEvtsCut = totalEvents/Nbins

        if (nEvents > 0.1*minEvtsCut):
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
            #     canvas.SaveAs(outdir_q+"q_"+info.outHistoName+str(i)+".gif")
            #     print ("Bin : " + str(i) + " (x = %.3f"%(info.th1.GetXaxis().GetBinCenter(i)) +") -> Resolution: %.3f +/- %.3f"%(value, error))

        else:
            print("Bin %i doesn't have enough statistics."%b)

        res_vs_X.SetBinContent(b,value)
        res_vs_X.SetBinError(b,error)

    res_vs_X.GetYaxis().SetRangeUser(0.0, 1.2*res_vs_X.GetMaximum())
    res_vs_X.Draw("hist e")
    myStyle.DrawPreliminaryInfo("Resolution vs x")
    myStyle.DrawTargetInfo(infoDict["Target"], "Simulation")

    canvas.SaveAs("%sRes2D_%s.gif"%(outputPath,v))
    # canvas.SaveAs("%sRes2D_%s.pdf"%(outputPath,v))
    canvas.Clear()

inputfile.Close()


# correct_prefix = {"reco": "Reconstructed", "mtch": "Reconstructed", "gene": "Generated"}

# list_of_hists = inputfile.GetListOfKeys()

# canvas = TCanvas("cv","cv",1000,800)
# gStyle.SetOptStat(0)

# line = TLine()
# line.SetLineColor(ROOT.kPink+10)
# line.SetLineWidth(3)
# line.SetLineStyle(9)
