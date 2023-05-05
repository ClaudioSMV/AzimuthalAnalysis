from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
ms.force_style()


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_Z_P_...")

parser.add_option('-A', dest='saveAll', action='store_true', default = False, help="Save All plots")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False, help="Overwrite if file already exists")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
rootpath = options.rootpath
isJLab = options.JLabCluster
saveAll = options.saveAll

input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

infoDict = ms.get_name_dict(dataset)
nameFormatted = ms.get_name_format(dataset)

## Cuts
shift = False
if ("Shift" in ms.get_cut_str2finallist(plots_cuts)):
    shift = True
    print("  [Correction] Plot PhiPQ shifted, ranging in ~(0., 360.)")

useZh = False
usePt2 = False
if ("Z" in ms.get_cut_str2finallist(plots_cuts)):
    useZh = True
if ("P" in ms.get_cut_str2finallist(plots_cuts)):
    usePt2 = True

if (useZh) and (usePt2):
    print("  [Correction] Two binning selected. Please, choose only one of the options!")
    exit()
elif useZh:
    plots_cuts+="_Zx"
elif usePt2:
    plots_cuts+="_Px"
else:
    print("  [Correction] Select Zx or Px as x binning!")
    exit()

## Input
inputPath = ms.get_output_fullpath("Correction", dataset, input_cuts, isJLab, False) # "../output/"
inputfile = TFile(inputPath,"READ")

## Output
outputPath = ms.get_plots_folder("Correction", plots_cuts, dataset, isJLab)
outputROOT = ms.get_plots_file("Corrected", dataset, "root")
if (not options.Overwrite and os.path.exists(outputPath+outputROOT)):
    print("  [Correction] Correction already exists! Not overwriting it.")
    exit()

histCorr_Reconstru = inputfile.Get("Corr_Reconstru")
histCorr_ReMtch_mc = inputfile.Get("Corr_ReMtch_mc")
histCorr_ReMtch_re = inputfile.Get("Corr_ReMtch_re")
histRaw            = inputfile.Get("Raw_data")

inputTHnSparse_list = [histCorr_Reconstru, histCorr_ReMtch_mc, histCorr_ReMtch_re, histRaw]
prefixType = ["Correction", "Corr GoodGen_mc", "Corr GoodGen_rec", "Raw data"]


# bins_list = [] # [3, 3, 10, 1]
# default_conf = [1,1,0,0] # 2D bins -> Q2 and Nu, integrate Zh and Pt2
# this_conf = [1,1,0,0]

# ### REVISIT THIS!
# # Set default shown binning by BinningType
# if (infoDict["BinningType"] == 0): # 0: Small binning
#     default_conf[2] = 0
#     default_conf[3] = 0
# elif (infoDict["BinningType"] >= 1): # 1: SplitZh
#     default_conf[2] = 1
#     default_conf[3] = 0
# # elif (infoDict["BinningType"] == 2): # 2: ThinZh bin, so it is intended to shown results as function of Zh
# #     default_conf[2] = 1
# #     default_conf[3] = 0

# # Change binning using input (or use default)
# if (useZh):
#     this_conf[2] = 1
#     this_conf[3] = 0
# elif (usePt2):
#     this_conf[2] = 0
#     this_conf[3] = 1
# else:
#     this_conf = default_conf # Plot Z

this_binDict = ms.all_dicts[infoDict["BinningType"]]

binstr = "QN" if "X" not in this_binDict else "QX"

# Change binning using input (or use default)
if (useZh):
    binstr+="Z"
elif (usePt2):
    binstr+="P"
else:
    print("  [Correction] Use Zx or Px.")
    exit()

## Get projections
names_list = ms.get_bincode_list(binstr, this_binDict)
Proj1DTHnSparse_list = []

for th in inputTHnSparse_list:
    list_proj = ms.get_sparseproj1d_list(th, names_list, shift)
    Proj1DTHnSparse_list.append(list_proj)

canvas = TCanvas("cv","cv",1000,800)
canvas.SetGrid(0,1)
# gPad.SetTicks(1,1)
TH1.SetDefaultSumw2()
gStyle.SetOptStat(0)


# Plot 2D histograms
outputfile = TFile(outputPath+outputROOT,"RECREATE")
phi_axis_title = ms.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"

for i,info in enumerate(names_list):
    for p,proj in enumerate(Proj1DTHnSparse_list):
        if (("Good" in prefixType[p]) and (not saveAll)): continue
        this_proj = proj[i]

        x_min = this_proj.GetXaxis().GetXmin()
        x_max = this_proj.GetXaxis().GetXmax()

        htemp = TH1F("htemp","",1, x_min,x_max)
        htemp.SetStats(0)
        htemp.SetMinimum(0.0001)
        # ylim = 30000
        ylim = this_proj.GetMaximum()*1.2
        htemp.SetMaximum(ylim)
        # htemp.SetLineColor(kBlack)
        htemp.GetYaxis().SetMaxDigits(3)
        htemp.GetXaxis().SetTitle(phi_axis_title)
        htemp.GetYaxis().SetTitle("Counts")
        htemp.Draw("AXIS")

        this_proj.SetLineColor(kBlack)

        # gPad.RedrawAxis("g")

        # htemp.Draw("AXIS same")
        # list_Corr_Reconstru[i].Draw("AXIS same")
        this_proj.Draw("hist e same")

        # legend.Draw();
        ms.DrawPreliminaryInfo(prefixType[p])
        ms.DrawTargetInfo(nameFormatted, "Data")
        ms.DrawBinInfo(info, infoDict["BinningType"])

        histName = "_".join(this_proj.GetName().split("_")[0:-1]) # Corr_A_B_Q1N2 -> Corr_A_B
        outputName = ms.get_plots_file(histName, dataset, "png", info)
        canvas.SaveAs(outputPath+outputName)
        this_proj.Write()
        htemp.Delete()
        canvas.Clear()

print("  [Correction] Correction plots saved!\n")
outputfile.Close()

