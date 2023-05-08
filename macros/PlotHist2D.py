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
gStyle.SetPadRightMargin(2*ms.get_margin())
gStyle.SetLabelSize(ms.get_size()-10,"z")
gROOT.ForceStyle()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-l', dest='drawLines', action='store_true', default = False, help="Draw lines to see bins")
parser.add_option('-d', dest='isData', action='store_true', default = False, help="HSim: False (default); Data: True")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
rootpath = options.rootpath
isJLab = options.JLabCluster

drawLines = options.drawLines
isData = options.isData

infoDict = ms.get_name_dict(dataset)
nameFormatted = ms.get_name_format(dataset, True)
this_binning = infoDict["BinningType"]
this_bin_dict = ms.all_dicts[this_binning]

useNu = True if ("N" in this_bin_dict) else False

plot_method = 'KinematicVars' if useNu else 'VarsVsXb' # Update this to get Q2, Zh... plots with Xb too

## Input
inputPath = ms.get_output_folder("Hist2D", "", isJLab, False) # "../output/"

inputPath += plot_method+"_"+infoDict["Target"]+"_"
if isData:  inputPath += "data.root"
else:       inputPath += "hsim.root"
inputfile = TFile(inputPath,"READ")

## Output
outputPath = ms.get_plots_folder("Map_Bin2D", "", infoDict["Target"]+"_"+plot_method, isJLab)

correct_prefix = {"reco": "Reconstructed", "mtch": "Reconstructed", "gene": "Generated"}
short_prefix = {"reco": "Rec", "mtch": "Rec", "gene": "Gen"}

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
            if (not useNu) and ("Nu" in h.GetName()): continue

            if not isData and "reco" in h.GetName(): continue


            # Name format is: "hist2D_Q2_PQ_gene" or "hist2D_Xb_Q2_goodPi_reco"
            tmp_txt = h.GetName().split("2D_")[1] # "Q2_PQ_gene" or "Xb_Q2_goodPi_reco"
            tmp_txt = tmp_txt.split("_") # [Q2, PQ, gene] or [Xb, Q2, goodPi, reco]

            var1 = ms.varname2key[tmp_txt[0]] # "Q2" -> 'Q' or "Xb" -> 'X'
            var2 = ms.varname2key[tmp_txt[1]] # "PQ" -> 'I' or "Q2" -> 'Q'
            type_hist = correct_prefix[tmp_txt[-1]]

            out_pref = short_prefix[tmp_txt[-1]]

            if 'goodPi' in tmp_txt:
                out_pref+="Pi"

            x_axis = this_bin_dict[var1]
            y_axis = this_bin_dict[var2]

            hist = h.ReadObj()
            hist.GetZaxis().SetMaxDigits(3)

            hist.GetXaxis().SetRangeUser(x_axis[0],x_axis[-1])
            hist.GetYaxis().SetRangeUser(y_axis[0],y_axis[-1])
            hist.Draw("colz")

            if drawLines:
                # Draw vertical lines
                for ix in range(1,len(x_axis)-1):
                    line.DrawLine(x_axis[ix],y_axis[0], x_axis[ix],y_axis[-1])

                # Draw horizontal lines
                for iy in range(1,len(y_axis)-1):
                    line.DrawLine(x_axis[0],y_axis[iy], x_axis[-1],y_axis[iy])

            ms.draw_preliminary(type_hist)
            dataOrSim = "Data" if isData else "Simulation"
            out_DatOrSim = "Data" if isData else "HSim"

            text_UpRight = ROOT.TLatex()
            text_UpRight.SetTextSize(ms.get_size()-5)
            text_UpRight.SetTextAlign(31)
            to_write = "%s vs %s, %s"%(ms.axis_label(var1, "Name"), ms.axis_label(var2, "Name"), dataOrSim)
            text_UpRight.DrawLatexNDC(1-2*ms.get_margin()-0.005,1-ms.get_margin()+0.01, to_write)

            canvas.SaveAs(outputPath+nameFormatted+"_"+out_DatOrSim+"-"+out_pref+"_"+var1+var2+".png")
            canvas.Clear()

