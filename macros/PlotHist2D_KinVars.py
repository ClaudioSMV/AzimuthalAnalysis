from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as mS
import math

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
mS.ForceStyle()
gStyle.SetPadRightMargin(2*mS.GetMargin())
gStyle.SetLabelSize(mS.GetSize()-10,"z")
gROOT.ForceStyle()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-l', dest='drawLines', action='store_true', default = False, help="Draw lines to see bins")
parser.add_option('-d', dest='isData', action='store_true', default = False, help="HSim: False (default); Data: True")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

isData = options.isData
drawLines = options.drawLines
rootpath = options.rootpath
dataset = options.Dataset
if options.JLabCluster: rootpath = "JLab_cluster"

infoDict = mS.getNameFormattedDict(dataset)
inputPath = mS.getInputFile("Hist2D",dataset,rootpath) # ClosureTest_%s_B%i_%iD.root
if isData:  inputPath += "data.root"
else:       inputPath += "hsim.root"
inputfile = TFile(inputPath,"READ")

outputPath = mS.getOutputDir("Hist2D",infoDict["Target"],rootpath)

correct_prefix = {"reco": "Reconstructed", "mtch": "Reconstructed", "gene": "Generated"}

list_of_hists = inputfile.GetListOfKeys()

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

line = TLine()
line.SetLineColor(ROOT.kPink+10)
line.SetLineWidth(3)
line.SetLineStyle(9)

for h in list_of_hists:
    if (h.ReadObj().Class_Name() == "TH2D"):
        if "hist2D" in h.GetName():
            if "PQ" in h.GetName(): continue
            if not isData and "reco" in h.GetName(): continue
            # Name format is: hist2D_Q2_Pt_gene
            tmp_txt = h.GetName().split("2D_")[1] # Q2_Pt_gene
            tmp_txt = tmp_txt.split("_") # [Q2, Pt, gene]

            var1 = tmp_txt[0][0] # Q
            var2 = tmp_txt[1][0] # P
            type_hist = correct_prefix[tmp_txt[2]]

            hist = h.ReadObj()
            hist.GetZaxis().SetMaxDigits(3)
            hist.Draw("colz")

            x_axis = mS.all_dicts[0][var1] # ['Bins']
            y_axis = mS.all_dicts[0][var2] # ['Bins']

            if drawLines:
                # Draw vertical lines
                for ix in range(1,len(x_axis)-1):
                    line.DrawLine(x_axis[ix],y_axis[0], x_axis[ix],y_axis[-1])

                # Draw horizontal lines
                for iy in range(1,len(y_axis)-1):
                    line.DrawLine(x_axis[0],y_axis[iy], x_axis[-1],y_axis[iy])

            mS.DrawPreliminaryInfo(type_hist)
            dataOrSim = "Data" if isData else "Simulation"

            text_UpRight = ROOT.TLatex()
            text_UpRight.SetTextSize(mS.GetSize()-5)
            text_UpRight.SetTextAlign(31)
            to_write = "%s vs %s, %s"%(mS.axis_label(var1, "Name"), mS.axis_label(var2, "Name"), dataOrSim)
            text_UpRight.DrawLatexNDC(1-2*mS.GetMargin()-0.005,1-mS.GetMargin()+0.01, to_write)

            canvas.SaveAs(outputPath+"KinVars_"+dataOrSim+"_"+type_hist+"_"+var1+"_"+var2+".gif")
            canvas.Clear()

