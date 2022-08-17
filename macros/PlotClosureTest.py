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

# class HistoInfo:
#     def __init__(self, inHistoName, f, outHistoName, doFits=True, yMax=30.0, title="", xlabel="", ylabel="Position resolution [#mum]", sensor=""):
#         self.inHistoName = inHistoName
#         self.f = f
#         self.outHistoName = outHistoName
#         self.doFits = doFits
#         self.yMax = yMax
#         self.title = title
#         self.xlabel = xlabel
#         self.ylabel = ylabel
#         self.th2 = self.getTH2(f, inHistoName, sensor)
#         self.th1 = self.getTH1(self.th2, outHistoName, self.shift(), self.fine_tuning(sensor))

#     def getTH2(self, f, name, sensor):
#         th2 = f.Get(name)
#         return th2

#     def getTH1(self, th2, name, centerShift, fine_value):
#         th1_temp = TH1D(name,"",th2.GetXaxis().GetNbins(),th2.GetXaxis().GetXmin()-centerShift-fine_value,th2.GetXaxis().GetXmax()-centerShift-fine_value)
#         return th1_temp

#     def shift(self):
#         return self.f.Get("stripBoxInfo03").GetMean(1)

#     def fine_tuning(self, sensor):
#         value = 0.0
#         return value

# def GetBinSufix(list):
#     totalsize = np.prod(list)
#     name_list = []
#     symbol_list = ["Q","N","Z"]
#     for i in range(totalsize):
#         total_tmp = totalsize
#         i_tmp = i
#         txt_tmp = ""
#         for j,nbin in enumerate(list):
#             total_tmp /= nbin
#             index = i_tmp/(total_tmp)
#             i_tmp -= index*total_tmp
#             txt_tmp += (symbol_list[j]+str(index))
#         name_list.append(txt_tmp)
#     return name_list

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-d', dest='debugMode', action='store_true', default = False, help="Run debug mode")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

debugMode = options.debugMode
dataset = options.Dataset
inputPath = myStyle.getInputFile("ClosureTest",dataset) # ClosureTest_%s_B%i_%iD.root
inputfile = TFile(inputPath,"READ")

outputPath = myStyle.getOutputDir("ClosureTest")

#outdir = outputPath+myStyle.getNameFormatted(dataset)

# xlength = float(options.xlength)
# ylength = float(options.ylength)

infoDict = myStyle.getNameFormattedDict(dataset)

histCorr_Reconstructed  = inputfile.Get("Corr_Reconstructed")
histCorr_RecGoodGen_mc  = inputfile.Get("Corr_RecGoodGen_mc")
histCorr_RecGoodGen_rec = inputfile.Get("Corr_RecGoodGen_rec")
histTrue                = inputfile.Get("True")
histTrue_PionRec        = inputfile.Get("True_PionReco")

inputTHnSparse_list = [histCorr_Reconstructed, histCorr_RecGoodGen_mc, histCorr_RecGoodGen_rec, histTrue, histTrue_PionRec]


bins_list = [] # [3, 3, 5]

for i in range(0,infoDict["NDims"]):
    nbins = histCorr_Reconstructed.GetAxis(i).GetNbins()
    bins_list.append(nbins)

totalsize = np.prod(bins_list)
names_list = []
Proj1DTHnSparse_list = [[],[],[],[],[]]
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
outputfile = TFile(outputPath+myStyle.getNameFormatted(dataset)+".root","RECREATE")
for i,info in enumerate(names_list):
    for p,proj in enumerate(Proj1DTHnSparse_list):
        this_proj = proj[i]
        htemp = TH1F("htemp","",1,-181.,181.)
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


        # legend = TLegend(myStyle.GetPadCenter()-0.27,1-myStyle.GetMargin()-0.3,myStyle.GetPadCenter()+0.27,1-myStyle.GetMargin()-0.1)
        # # legend.SetBorderSize(0)
        # # legend.SetFillColor(kWhite)
        # # legend.SetTextFont(myStyle.GetFont())
        # # legend.SetTextSize(myStyle.GetSize())
        # #legend.SetFillStyle(0)

        # if ('oneStrip' in info.outHistoName):
        #     legend.AddEntry(list_Corr_Reconstructed[i], "One strip reconstruction")
        # elif ('twoStrips' in info.outHistoName):
        #     legend.AddEntry(list_Corr_Reconstructed[i], "Two strips reconstruction")
        # else:
        #     legend.AddEntry(list_Corr_Reconstructed[i], "Full reconstruction")
            

        # legend.Draw();
        myStyle.DrawPreliminaryInfo()
        myStyle.DrawTargetInfo(infoDict["Target"], "Simulation")

        canvas.SaveAs(outputPath+this_proj.GetName()+".gif")
        # canvas.SaveAs(outputPath+"CT_"+info+".pdf")
        this_proj.Write()
        htemp.Delete()

outputfile.Close()

