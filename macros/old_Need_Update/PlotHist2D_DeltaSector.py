from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,THStack,TLatex,TMath,TColor,TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
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
gStyle.SetLabelSize(ms.get_size()-10,"z")
gStyle.SetTitleYOffset(1.3)
gROOT.ForceStyle()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
# parser.add_option('-l', dest='drawLines', action='store_true', default = False, help="Draw lines to see bins")
parser.add_option('-d', dest='isData', action='store_true', default = False, help="HSim: False (default); Data: True")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
rootpath = options.rootpath
isJLab = options.JLabCluster

# drawLines = options.drawLines
isData = options.isData

infoDict = ms.get_name_dict(dataset)
nameFormatted = ms.get_name_format(dataset, True)
this_binning = infoDict["BinningType"]
this_bin_dict = ms.all_dicts[this_binning]

## Cuts
input_cuts = options.inputCuts

## Input
inputPath = ms.get_output_folder("Hist2D", input_cuts, isJLab, False) # "../output/"
inputPath += "PQVsDeltaSector_"+nameFormatted+"_"
inputPath += "data.root" if isData else "hsim.root"
inputfile = TFile(inputPath,"READ")

## Output
outputPath = ms.get_plots_folder("Hist2D/DeltaSector", input_cuts, dataset, isJLab)

correct_prefix = {"reco": "Reconstructed", "recoAcc": "Acc corrected", "gene": "Generated"}
# short_prefix = {"reco": "Rec", "mtch": "Rec", "gene": "Gen"}

### Set input hists
list_2dHist = []
list_methods = ["reco", "recoAcc"]
if not isData:
    list_methods.append("gene")

for m in list_methods:
    this_2dHist = inputfile.Get("hist2D_DeltaSector_PhiPQ_%s"%m)
    list_2dHist.append(this_2dHist)

### Set output hists
phi_axis_title = ms.axis_label('I',"LatexUnit")

# list_outHists = []
list_thStack = []
for m in list_methods:
    outHistStack = THStack("hStack_%s"%m,"%s;%s;Counts"%(correct_prefix,phi_axis_title))
    list_thStack.append(outHistStack)

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

list_colors = ms.get_color()

ROOT.TGaxis.SetExponentOffset(-0.06, 0.0, "y")

for h,hist in enumerate(list_2dHist):
    xbins = hist.GetXaxis().GetNbins()
    list_outHists = []

    this_legend = TLegend(ms.get_padcenter()-0.2,1-ms.get_margin()-0.27, ms.get_padcenter()+0.2,1-ms.get_margin()-0.02)
    this_legend.SetBorderSize(0)
    # this_legend.SetFillColor(ROOT.kWhite)
    this_legend.SetTextFont(ms.get_font())
    this_legend.SetTextSize(ms.get_size()-8)
    this_legend.SetFillStyle(0)

    this_thStack = list_thStack[h]

    for s in range(1,xbins+1):
        this_proj = hist.ProjectionY("py",s,s)

        if (s<6):
            tmp_proj = this_proj.Clone("DeltaSec%i"%(s))
            tmp_proj.SetTitle("|#DeltaSect|(#pi-e) = %i;%s;Counts"%(s,phi_axis_title))
            list_outHists.append(tmp_proj)
        elif (s==6):
            tmp_proj = this_proj.Clone("DeltaSec0")
            tmp_proj.SetTitle("|#DeltaSect|(#pi-e) = 0;%s;Counts"%(phi_axis_title))
            # list_outHists.append(tmp_proj)

            tmp_proj.SetFillColorAlpha(list_colors[6], 0.5)
            tmp_proj.SetLineColorAlpha(list_colors[6], 1.0)
            this_thStack.Add(tmp_proj)

            this_legend.AddEntry(tmp_proj,"","lf")
        else: # s>6
            tmp_outhist = list_outHists[s-7]
            tmp_outhist.Add(this_proj)

            tmp_outhist.SetFillColorAlpha(list_colors[s-7], 0.5)
            tmp_outhist.SetLineColorAlpha(list_colors[s-7], 1.0)
            this_thStack.Add(tmp_outhist)

            this_legend.AddEntry(tmp_outhist,"","lf")

    # this_legend.AddEntry(this_thStack)

    this_thStack.Draw()
    this_thStack.GetYaxis().SetMaxDigits(3)
    this_thStack.SetMaximum(this_thStack.GetMaximum()*1.3)
    this_thStack.Draw("NOSTACK")
    # gPad.BuildLegend(0.3,0.7,0.7,0.9,"")

    this_legend.Draw()

    this_method = list_methods[h]
    ms.draw_preliminary("#DeltaSector %s"%correct_prefix[this_method])
    dataOrSim = "Data" if isData else "Simulation"
    out_DatOrSim = "Data" if isData else "HSim"

    ms.draw_targetinfo(infoDict["Target"], dataOrSim)

    name_png = ms.get_plots_file("DSect_%s"%(this_method),dataset,"png",out_DatOrSim)
    canvas.SaveAs(outputPath+name_png)

    # name_pdf = ms.get_plots_file("DSect_%s"%(this_method),dataset,"pdf",out_DatOrSim)
    # canvas.SaveAs(outputPath+name_pdf)

    canvas.Clear()
