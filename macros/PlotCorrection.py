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
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")

parser.add_option('-Z', dest='useZh',  action='store_true', default = False, help="Use bin in Zh, integrate Pt2")
parser.add_option('-P', dest='usePt2', action='store_true', default = False, help="Use bin in Pt2, integrate Zh")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
rootpath = options.rootpath
saveAll = options.saveAll
if options.JLabCluster: rootpath = "JLab_cluster"
ext_error = "_FullErr" if options.errorFull else ""

useZh = options.useZh
usePt2 = options.usePt2
if (not useZh) and (not usePt2): print("Using default binning!")
if (useZh) and (usePt2):
    print("Two binning selected. Please, choose only one of the options!")
    exit()

infoDict = myStyle.getNameFormattedDict(dataset)

inputPath = myStyle.getInputFile("Correction",dataset,rootpath) # Corrected_Fe_B0_2D.root
inputPath = myStyle.addBeforeRootExt(inputPath,ext_error)
inputfile = TFile(inputPath,"READ")

outputPath = myStyle.getOutputDir("Correction",infoDict["Target"],rootpath)

histCorr_Reconstru = inputfile.Get("Corr_Reconstru")
histCorr_ReMtch_mc = inputfile.Get("Corr_ReMtch_mc")
histCorr_ReMtch_re = inputfile.Get("Corr_ReMtch_re")
histRaw                 = inputfile.Get("Raw_data")

inputTHnSparse_list = [histCorr_Reconstru, histCorr_ReMtch_mc, histCorr_ReMtch_re, histRaw]
prefixType = ["Correction", "Corr GoodGen_mc", "Corr GoodGen_rec", "Raw data"]


bins_list = [] # [3, 3, 10, 1]
default_conf = [1,1,0,0] # 2D bins -> Q2 and Nu, integrate Zh and Pt2
this_conf = [1,1,0,0]
hadronic_bin_name = ""

# Set default shown binning by BinningType
if (infoDict["BinningType"] == 0): # 0: Small binning
    default_conf[2] = 0
    default_conf[3] = 0
elif (infoDict["BinningType"] == 1): # 1: SplitZh
    default_conf[2] = 1
    default_conf[3] = 0
elif (infoDict["BinningType"] == 2): # 2: ThinZh bin, so it is intended to shown results as function of Zh
    default_conf[2] = 1
    default_conf[3] = 0

# Change binning using input (or use default)
if (useZh):
    this_conf[2] = 1
    this_conf[3] = 0
    hadronic_bin_name = "_Z"
elif (usePt2):
    this_conf[2] = 0
    this_conf[3] = 1
    hadronic_bin_name = "_P"
else:
    this_conf = default_conf

# for i in range(0,outDim):
for i,i_bool in enumerate(this_conf):
    if i_bool:
        nbins = histCorr_Reconstru.GetAxis(i).GetNbins()
        bins_list.append(nbins)
    else:
        bins_list.append(1)

totalsize = np.prod(bins_list)
names_list = []
Proj1DTHnSparse_list = [[],[],[],[]]
symbol_list = ["Q","N","Z","P"]
for i in range(totalsize):
    total_tmp = totalsize
    i_tmp = i
    txt_tmp = ""
    # for j,nbin in enumerate(bins_list):
    for j,j_bool in enumerate(this_conf):
        if j_bool:
            total_tmp /= bins_list[j]
            index = i_tmp/(total_tmp)
            i_tmp -= index*total_tmp
            txt_tmp += (symbol_list[j]+str(index))

            for t in inputTHnSparse_list:
                t.GetAxis(j).SetRange(index+1, index+1)

            # histCorr_Reconstru.GetAxis(j).SetRange(index+1, index+1)

    for n,newRangeInput in enumerate(inputTHnSparse_list):
        proj_tmp = newRangeInput.Projection(4)
        proj_tmp.SetName(newRangeInput.GetName()+"_"+txt_tmp)

        Proj1DTHnSparse_list[n].append(proj_tmp)

    # histCorr_Reconstru_Proj = histCorr_Reconstru.Projection(4)
    # histCorr_Reconstru_Proj.SetName(histCorr_Reconstru.GetName()+"_"+txt_tmp)

    # list_Corr_Reconstru.append(histCorr_Reconstru_Proj)
    names_list.append(txt_tmp)


canvas = TCanvas("cv","cv",1000,800)
canvas.SetGrid(0,1)
# gPad.SetTicks(1,1)
TH1.SetDefaultSumw2()
gStyle.SetOptStat(0)


# Plot 2D histograms
nameFormatted = myStyle.getNameFormatted(dataset)
outputfile = TFile(outputPath+nameFormatted+hadronic_bin_name+ext_error+".root","RECREATE")
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
        htemp.GetYaxis().SetMaxDigits(3)
        htemp.GetXaxis().SetTitle("#phi_{PQ} (deg)")
        htemp.GetYaxis().SetTitle("Counts")
        htemp.Draw("AXIS")

        this_proj.SetLineColor(kBlack)
        # list_Corr_Reconstru[i].SetTitle(info.title)
        # list_Corr_Reconstru[i].GetXaxis().SetTitle(info.xlabel)
        # list_Corr_Reconstru[i].GetXaxis().SetRangeUser(-0.32, 0.32)
        # list_Corr_Reconstru[i].GetYaxis().SetTitle(info.ylabel)

        # gPad.RedrawAxis("g")

        # htemp.Draw("AXIS same")
        # list_Corr_Reconstru[i].Draw("AXIS same")
        this_proj.Draw("hist e same")

        # legend.Draw();
        myStyle.DrawPreliminaryInfo(prefixType[p])
        myStyle.DrawTargetInfo(nameFormatted, "Data")
        myStyle.DrawBinInfo(info, infoDict["BinningType"])

        canvas.SaveAs(outputPath+nameFormatted+hadronic_bin_name+"-"+this_proj.GetName()+ext_error+".gif")
        this_proj.Write()
        htemp.Delete()

outputfile.Close()

