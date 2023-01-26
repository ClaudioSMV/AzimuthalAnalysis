from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as mS

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
mS.ForceStyle()

# gStyle.SetStatX(1 - mS.GetMargin() - 0.005)
# gStyle.SetStatY(2*mS.GetMargin() + 0.205)

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

parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default does not)")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

useFold = options.fold
if ("Fold" in mS.getCutStrFromStr(options.inputCuts) or "Fold" in mS.getCutStrFromStr(options.outputCuts)):
    useFold = True
fit_type = "Fd" if useFold else "LR"

infoDict = mS.getDictNameFormat(dataset)
nameFormatted = mS.getNameFormatted(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"

input_cuts+="_"+fit_type # Add Fold or LR extension
plots_cuts+="_"+fit_type

## Input
inputPath = mS.getPlotsFolder("Fit", input_cuts, infoDict["Target"], isJLab, False) # "../output/"
inputROOT = mS.getPlotsFile("Fit", dataset, "root", fit_type)
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = mS.getPlotsFolder("ParametersCorrelation", plots_cuts, infoDict["Target"], isJLab)

list_func_names = ["crossSectionR"]
if not useFold:
    list_func_names.append("crossSectionL")

list_of_hists = inputfile.GetListOfKeys().Clone()
for elem in list_of_hists:
    if (elem.ReadObj().Class_Name() != "TH1D"):
        list_of_hists.Remove(elem)

th1_CorrAB_list = []
th1_CorrAC_list = []
th1_CorrBC_list = []
for e,elem in enumerate(list_func_names):
    th1_CorrAB = TH1D("correlationAB%i"%e,";Correlation;Entries", 100,-1.0,1.0)
    th1_CorrAB_list.append(th1_CorrAB)

    th1_CorrAC = TH1D("correlationAC%i"%e,";Correlation;Entries", 100,-1.0,1.0)
    th1_CorrAC_list.append(th1_CorrAC)

    th1_CorrBC = TH1D("correlationBC%i"%e,";Correlation;Entries", 100,-1.0,1.0)
    th1_CorrBC_list.append(th1_CorrBC)


print("")
print("Target %s"%infoDict["Target"])

# index_h = 0
for i_h,h in enumerate(inputfile.GetListOfKeys()): #list_of_hists):
    if ((h.ReadObj().Class_Name() == "TH1D") and ("Corr_Reconstru" in h.GetName())):
        hist_targ = h.ReadObj()
        hist_name = h.GetName() # Corr_Reconstru_Q0N0Z0_type (type: Fd or LR)

        tmp_name = "_".join(h.GetName().split("_")[1:-2]) # Reconstru
        bin_name = hist_name.split("_")[-2] # Q0N0Z0

        for i_f,f in enumerate(list_func_names):
            # Get correlation matrix
            name_corr = "%s_corrM"%(bin_name)
            if "L" in f:
                name_corr+="L"
            corr_matrix = inputfile.Get(name_corr)

            corrAB = GetMatrixElem(corr_matrix, 0, 1) # Get Corr AB
            corrAC = GetMatrixElem(corr_matrix, 0, 2) # Get Corr AC
            corrBC = GetMatrixElem(corr_matrix, 1, 2) # Get Corr BC

            th1_CorrAB_list[i_f].Fill(corrAB)
            th1_CorrAC_list[i_f].Fill(corrAC)
            th1_CorrBC_list[i_f].Fill(corrBC)


print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

# canvas.SetLogy(0)
for e,elem in enumerate(list_func_names):
    if ("L" in elem): name_ext = "L"
    elif ("R" in elem): name_ext = "R"
    if ("F" in fit_type): name_ext = "F"

    th1_CorrAB_list[e].Draw()

    mS.DrawPreliminaryInfo("Correlation AB %s"%(fit_type))
    mS.DrawTargetInfo(nameFormatted, "Data")

    this_title_gif = outputPath + mS.getPlotsFile("CorrelationAB", dataset, "gif")
    if ("LR" in this_title_gif):
        this_title_gif = mS.addBeforeRootExt(this_title_gif, "-%s"%(name_ext), "gif")

    this_title_pdf = outputPath + mS.getPlotsFile("CorrelationAB", dataset, "pdf")
    if ("LR" in this_title_pdf):
        this_title_pdf = mS.addBeforeRootExt(this_title_pdf, "-%s"%(name_ext), "pdf")

    canvas.SaveAs(this_title_gif)
    canvas.SaveAs(this_title_pdf)
    canvas.Clear()


    th1_CorrAC_list[e].Draw()

    mS.DrawPreliminaryInfo("Correlation AC %s"%(fit_type))
    mS.DrawTargetInfo(nameFormatted, "Data")

    this_title_gif = outputPath + mS.getPlotsFile("CorrelationAC", dataset, "gif")
    if ("LR" in this_title_gif):
        this_title_gif = mS.addBeforeRootExt(this_title_gif, "-%s"%(name_ext), "gif")

    this_title_pdf = outputPath + mS.getPlotsFile("CorrelationAC", dataset, "pdf")
    if ("LR" in this_title_pdf):
        this_title_pdf = mS.addBeforeRootExt(this_title_pdf, "-%s"%(name_ext), "pdf")

    canvas.SaveAs(this_title_gif)
    canvas.SaveAs(this_title_pdf)
    canvas.Clear()


    th1_CorrBC_list[e].Draw()

    mS.DrawPreliminaryInfo("Correlation BC %s"%(fit_type))
    mS.DrawTargetInfo(nameFormatted, "Data")

    this_title_gif = outputPath + mS.getPlotsFile("CorrelationBC", dataset, "gif")
    if ("LR" in this_title_gif):
        this_title_gif = mS.addBeforeRootExt(this_title_gif, "-%s"%(name_ext), "gif")

    this_title_pdf = outputPath + mS.getPlotsFile("CorrelationBC", dataset, "pdf")
    if ("LR" in this_title_pdf):
        this_title_pdf = mS.addBeforeRootExt(this_title_pdf, "-%s"%(name_ext), "pdf")

    canvas.SaveAs(this_title_gif)
    canvas.SaveAs(this_title_pdf)
    canvas.Clear()

print("Made it to the end!")

inputfile.Close()