from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as mS

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
mS.force_style()

# gStyle.SetStatX(1 - mS.get_margin() - 0.005)
# gStyle.SetStatY(2*mS.get_margin() + 0.205)

def PropErrorDivision(v1, e1, v2, e2, cov=0):
    this_error = TMath.Abs(v1/v2)*TMath.Sqrt((e1/v1)*(e1/v1) + (e2/v2)*(e2/v2) - 2*cov/(v1*v2))
    return this_error

def GetMatrixElem(matrix, row, col):
    this_matrix = matrix.GetMatrixArray()
    index = col + 3*row
    return this_matrix[index]

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")

# parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default does not)")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

infoDict = mS.get_name_dict(dataset)
nameFormatted = mS.get_name_format(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"

input_cuts+="_LR"
# plots_cuts+="_LR"

## Input
inputPath = mS.get_plots_folder("Fit", input_cuts, dataset, isJLab, False)
inputROOT = mS.get_plots_file("Fit", dataset, "root", "LR")
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = mS.get_plots_folder("CompareLRFits", plots_cuts, dataset, isJLab)

list_func_names = ["crossSectionR"]
list_func_names.append("crossSectionL")

list_of_hists = inputfile.GetListOfKeys().Clone()
for elem in list_of_hists:
    if (elem.ReadObj().Class_Name() != "TH1D"):
        list_of_hists.Remove(elem)

th1_LoverR_list = []
th1_LoverR_A = TH1D("LoverR_A",";A_{L}/A_{R};Entries", 80,-2.0,2.0)
th1_LoverR_list.append(th1_LoverR_A)

th1_LoverR_B = TH1D("LoverR_B",";B_{L}/B_{R};Entries", 80,-2.0,2.0)
th1_LoverR_list.append(th1_LoverR_B)

th1_LoverR_C = TH1D("LoverR_C",";C_{L}/C_{R};Entries", 80,-2.0,2.0)
th1_LoverR_list.append(th1_LoverR_C)


print("")
print("Target %s"%infoDict["Target"])

# index_h = 0
for i_h,h in enumerate(inputfile.GetListOfKeys()): #list_of_hists):
    if ((h.ReadObj().Class_Name() == "TH1D") and ("Corr_Reconstru" in h.GetName())):
        hist_targ = h.ReadObj()
        hist_name = h.GetName() # Corr_Reconstru_Q0N0Z0_type (type: Fd or LR)

        tmp_name = "_".join(h.GetName().split("_")[1:-2]) # Reconstru
        bin_name = hist_name.split("_")[-2] # Q0N0Z0

        fitL = hist_targ.GetFunction("crossSectionL")
        parL0 = fitL.GetParameter(0)
        parL1 = fitL.GetParameter(1)
        parL2 = fitL.GetParameter(2)

        fitR = hist_targ.GetFunction("crossSectionR")
        parR0 = fitR.GetParameter(0)
        parR1 = fitR.GetParameter(1)
        parR2 = fitR.GetParameter(2)

        th1_LoverR_A.Fill(parL0/parR0)
        th1_LoverR_B.Fill(parL1/parR1)
        th1_LoverR_C.Fill(parL2/parR2)


print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

for i,ipar in enumerate(["A", "B", "C"]):
    th1_LoverR_list[i].Draw()
    mS.DrawPreliminaryInfo("Comparison L/R %s"%ipar)
    mS.DrawTargetInfo(nameFormatted, "Data")

    this_title_gif = outputPath + mS.get_plots_file("CompareLR_%s"%ipar, dataset, "gif")
    this_title_pdf = outputPath + mS.get_plots_file("CompareLR_%s"%ipar, dataset, "pdf")

    canvas.SaveAs(this_title_gif)
    canvas.SaveAs(this_title_pdf)
    canvas.Clear()

print("Made it to the end!")

inputfile.Close()
