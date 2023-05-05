from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
from array import array

gROOT.SetBatch( True )
gStyle.SetOptFit(1)

## Defining Style
ms.ForceStyle()

gStyle.SetStatX(1 - ms.GetMargin() - 0.005)
gStyle.SetStatY(2*ms.GetMargin() + 0.205)

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")

# parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")
# parser.add_option('-O', dest='Overwrite', action='store_true', default = False, help="Overwrite if file already exists")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

infoDict = ms.get_name_dict(dataset)
nameFormatted = ms.get_name_format(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts

if ("FErr" in ms.get_cut_str2finallist(input_cuts)):
    input_cuts = input_cuts.replace("FE","")
if ("FErr" in ms.get_cut_str2finallist(plots_cuts)):
    plots_cuts = plots_cuts.replace("FE","")

input_cuts_eE = input_cuts
plots_cuts_eE = plots_cuts

input_cuts_FE = input_cuts + "_FE"
plots_cuts_FE = plots_cuts + "_FE"

## Input
inputPath_eE = ms.get_plots_folder("Correction", input_cuts_eE, dataset, isJLab, False)
inputPath_FE = ms.get_plots_folder("Correction", input_cuts_FE, dataset, isJLab, False)
inputROOT = ms.get_plots_file("Corrected", dataset, "root")

inputfile_eE = TFile(inputPath_eE+inputROOT,"READ")
inputfile_FE = TFile(inputPath_FE+inputROOT,"READ")

## Output
outputPath = ms.get_plots_folder("ErrorsCompared", plots_cuts_eE, dataset, isJLab)
outputROOT = ms.get_plots_file("Errors", dataset, "root")
# if (not options.Overwrite and os.path.exists(outputPath+outputROOT)):
#     print("Fit already exists! Not overwriting it.")
#     exit()

list_hists = inputfile_eE.GetListOfKeys()
this_dict = ms.all_dicts[infoDict["BinningType"]]
phi_binning = this_dict['I']

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

outputfile = TFile(outputPath+outputROOT,"RECREATE")

for h in list_hists:
    if (h.ReadObj().Class_Name() == "TH1D"):
        if "Corr" in h.GetName(): ## ADD SUPPORT FOR ALL CORRECTIONS!
            # if "PQ" in h.GetName(): continue
            # if not isData and "reco" in h.GetName(): continue

            # Name format is: Corr_Reconstru_Q0N0
            tmp_name = "_".join(h.GetName().split("_")[1:-1]) # Reconstru
            tmp_txt = h.GetName().split("_")[-1] # Q0N0Z0

            hist_eE = h.ReadObj()
            Nbins = hist_eE.GetXaxis().GetNbins()
            hist_FE = inputfile_FE.Get(h.GetName())

            ## Fold two tails in one
            hist_tmp = TH1D("%s_EDiff"%(h.GetName()), "Error difference (#phi^{FE}_{PQ} - #phi^{eE}_{PQ})/#phi^{eE}_{PQ};#phi_{PQ} (deg);(E^{FE}_{#phi} - E^{eE}_{#phi})/E^{eE}_{#phi}", Nbins, array('d',phi_binning)) #, 500,-0.2,1.3)
            # hist_tmp.Sumw2()

            for b in range(1, Nbins+1):
                value_eE = hist_eE.GetBinContent(b)
                value_FE = hist_FE.GetBinContent(b)

                if (value_eE!=value_FE):
                    print("eE: %.4f; FE: %.4f;"%(value_eE,value_FE))

                error_eE = hist_eE.GetBinError(b)
                error_FE = hist_FE.GetBinError(b)

                if (error_eE!=0):
                    hist_tmp.Fill(hist_eE.GetBinCenter(b), (error_FE-error_eE)/error_eE)
                else:
                    hist_tmp.Fill(hist_eE.GetBinCenter(b), -0.1)

            hist_tmp.SetMinimum(-0.1)
            # ylim = hist_tmp.GetMaximum()*1.4
            hist_tmp.SetMaximum(1.3) #(ylim)

            # hist_tmp.GetXaxis().SetTitle("#phi_{PQ} (deg)")
            # hist_tmp.GetYaxis().SetTitle("Counts")

            hist_tmp.Draw("hist col")
            hist_tmp.Write()

            ms.DrawPreliminaryInfo("Compare error")
            ms.DrawTargetInfo(nameFormatted, "Data")
            ms.DrawBinInfo(tmp_txt, infoDict["BinningType"])

            outputName = ms.get_plots_file("CompareError_"+tmp_name, dataset, "png",tmp_txt)
            canvas.SaveAs(outputPath+outputName)
            canvas.Clear()

print("Comparison done!\n")
outputfile.Close()
