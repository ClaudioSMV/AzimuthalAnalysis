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

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-a', dest='saveAll', action='store_true', default = False, help="Save All plots")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset

infoDict = myStyle.getNameFormattedDict(dataset)

inputPath = myStyle.getInputFile("Correction",dataset,rootpath) # Corrected_Fe_B0_2D.root
inputfile = TFile(inputPath,"READ")

outputPath = myStyle.getOutputDir("Correction",infoDict["Target"],rootpath)

histCorr_Reconstructed  = inputfile.Get("Corr_Reconstructed")
histCorr_RecGoodGen_mc  = inputfile.Get("Corr_RecGoodGen_mc")
histCorr_RecGoodGen_rec = inputfile.Get("Corr_RecGoodGen_rec")
histRaw                 = inputfile.Get("Raw_data")

inputTHnSparse_list = [histCorr_Reconstructed, histCorr_RecGoodGen_mc, histCorr_RecGoodGen_rec, histRaw]
prefixType = ["Correction", "Corr GoodGen_mc", "Corr GoodGen_rec", "Raw data"]


bins_list = [] # [3, 3, 5]

for i in range(0,infoDict["NDims"]):
    nbins = histCorr_Reconstructed.GetAxis(i).GetNbins()
    bins_list.append(nbins)

totalsize = np.prod(bins_list)
names_list = []
Proj1DTHnSparse_list = [[],[],[],[]]
symbol_list = ["Q","N","Z"]
for i in range(totalsize):
    total_tmp = totalsize
    i_tmp = i
    txt_tmp = ""
    for j,nbin in enumerate(bins_list):
        total_tmp /= nbin
        index = i_tmp/(total_tmp)
        i_tmp -= index*total_tmp
        txt_tmp += (symbol_list[j]+str(index))

        for t in inputTHnSparse_list:
            t.GetAxis(j).SetRange(index+1, index+1)

        # histCorr_Reconstructed.GetAxis(j).SetRange(index+1, index+1)

    for n,newRangeInput in enumerate(inputTHnSparse_list):
        proj_tmp = newRangeInput.Projection(4)
        proj_tmp.SetName(newRangeInput.GetName()+"_"+txt_tmp)

        Proj1DTHnSparse_list[n].append(proj_tmp)

    # histCorr_Reconstructed_Proj = histCorr_Reconstructed.Projection(4)
    # histCorr_Reconstructed_Proj.SetName(histCorr_Reconstructed.GetName()+"_"+txt_tmp)

    # list_Corr_Reconstructed.append(histCorr_Reconstructed_Proj)
    names_list.append(txt_tmp)


canvas = TCanvas("cv","cv",1000,800)
canvas.SetGrid(0,1)
# gPad.SetTicks(1,1)
TH1.SetDefaultSumw2()
gStyle.SetOptStat(0)


# Plot 2D histograms
nameFormatted = myStyle.getNameFormatted(dataset)
outputfile = TFile(outputPath+nameFormatted+".root","RECREATE")
for i,info in enumerate(names_list):
    for p,proj in enumerate(Proj1DTHnSparse_list):
        if (("Good" in prefixType[p]) and (not saveAll)): continue
        this_proj = proj[i]
        htemp = TH1F("htemp","",1,-180.,180.)
        htemp.SetStats(0)
        htemp.SetMinimum(0.0001)
        # ylim = 30000
        ylim = this_proj.GetMaximum()*1.2
        htemp.SetMaximum(ylim)
        # htemp.SetLineColor(kBlack)
        htemp.GetXaxis().SetTitle("#phi_{PQ} (deg)")
        htemp.GetYaxis().SetTitle("Counts")
        htemp.Draw("AXIS")

        this_proj.SetLineColor(kBlack)
        # list_Corr_Reconstructed[i].SetTitle(info.title)
        # list_Corr_Reconstructed[i].GetXaxis().SetTitle(info.xlabel)
        # list_Corr_Reconstructed[i].GetXaxis().SetRangeUser(-0.32, 0.32)
        # list_Corr_Reconstructed[i].GetYaxis().SetTitle(info.ylabel)

        # gPad.RedrawAxis("g")

        # htemp.Draw("AXIS same")
        # list_Corr_Reconstructed[i].Draw("AXIS same")
        this_proj.Draw("hist e same")

        # legend.Draw();
        myStyle.DrawPreliminaryInfo(prefixType[p])
        myStyle.DrawTargetInfo(nameFormatted, "Data")
        myStyle.DrawBinInfo(info)

        canvas.SaveAs(outputPath+nameFormatted+"-"+this_proj.GetName()+".gif")
        # canvas.SaveAs(outputPath+"CT_"+info+".pdf")
        this_proj.Write()
        htemp.Delete()

outputfile.Close()

