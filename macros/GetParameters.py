from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
myStyle.ForceStyle()

gStyle.SetStatX(1 - myStyle.GetMargin() - 0.005)
gStyle.SetStatY(2*myStyle.GetMargin() + 0.205)

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")
parser.add_option('-v', dest='verbose', action='store_true', default = False, help="Print values")

parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default does not)")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")
parser.add_option('--zoom', dest='useZoom', action='store_true', default = False, help="Zoom y-axis range (useful for solid target)")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False, help="Overwrite if file already exists")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster
verbose = options.verbose

useFold = options.fold
if "Fold" in myStyle.getCutStrFromStr(options.outputCuts):
    useFold = True
fit_type = "Fd" if useFold else "LR"

useZoom = options.useZoom

infoDict = myStyle.getDictNameFormat(dataset)
nameFormatted = myStyle.getNameFormatted(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"

input_cuts+="_"+fit_type # Add Fold or LR extension
plots_cuts+="_"+fit_type

## Input
inputPath = myStyle.getOutputFileWithPath("Fit", dataset, input_cuts, isJLab, False) # "../output/"
inputROOT = myStyle.getPlotsFile("Fit", dataset, "root", fit_type)
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = myStyle.getPlotsFolder("FitParameters", plots_cuts, infoDict["Target"], isJLab)
outputROOT = myStyle.getPlotsFile("Parameters", dataset, "root", fit_type)
if (not options.Overwrite and os.path.exists(outputPath+outputROOT)):
    print("Parameters file already exists! Not overwriting it.")
    exit()

list_func_names = ["crossSectionR"]
if not useFold:
    list_func_names.append("crossSectionL")

list_of_hists = inputfile.GetListOfKeys().Clone()
for elem in list_of_hists:
    if (elem.ReadObj().Class_Name() != "TH1D"):
        list_of_hists.Remove(elem)

parameter_A_list = []
parameter_B_list = []
parameter_C_list = []

for e,elem in enumerate(list_func_names):
    parameter_A_hist = TH1D("par_A%i"%e,";Bin;Parameter A [?]", list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    parameter_A_list.append(parameter_A_hist)

    parameter_B_hist = TH1D("par_B%i"%e,";Bin;Parameter B [?]", list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    parameter_B_list.append(parameter_B_hist)

    parameter_C_hist = TH1D("par_C%i"%e,";Bin;Parameter C [?]", list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    parameter_C_list.append(parameter_C_hist)

print("")
print("Target %s"%infoDict["Target"])

index_h = 0
for i_h,h in enumerate(inputfile.GetListOfKeys()):
    if ((h.ReadObj().Class_Name() == "TH1D") and ("Corr_Reconstru" in h.GetName())): ## ADD SUPPORT FOR ALL CORRECTIONS!
        hist_target = h.ReadObj()
        hist_name = h.GetName() # Corr_Reconstru_Q0N0_type (type: Fd or LR)

        tmp_name = "_".join(h.GetName().split("_")[1:-2]) # Reconstru
        bin_name = hist_name.split("_")[-2] # Q0N0

        for i_f,f in enumerate(list_func_names):
            this_fit = hist_target.GetFunction(f)
            par0 = this_fit.GetParameter(0)
            par1 = this_fit.GetParameter(1)
            par2 = this_fit.GetParameter(2)

            err0 = this_fit.GetParError(0)
            err1 = this_fit.GetParError(1)
            err2 = this_fit.GetParError(2)

            if verbose:
                print("%s Fit: %s"%(hist_name, f))
                print("Parameters: (%6.2f, %5.2f, %5.2f)"%(par0, par1, par2))
                print("Errors    : (%6.2f, %5.2f, %5.2f)"%(err0, err1, err2))
                print("")

            parameter_A_list[i_f].Fill(bin_name, 0.0)
            parameter_B_list[i_f].Fill(bin_name, 0.0)
            parameter_C_list[i_f].Fill(bin_name, 0.0)

            parameter_A_list[i_f].SetBinContent(index_h+1, par0)
            parameter_B_list[i_f].SetBinContent(index_h+1, par1)
            parameter_C_list[i_f].SetBinContent(index_h+1, par2)

            parameter_A_list[i_f].SetBinError(index_h+1, err0)
            parameter_B_list[i_f].SetBinError(index_h+1, err1)
            parameter_C_list[i_f].SetBinError(index_h+1, err2)
        index_h+=1

print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

### Save parameters
outputFile = TFile(outputPath+outputROOT,"RECREATE")

zoom_ext = "" if not useZoom else "_zoom"
# canvas.SetLogy(1)
for e,elem in enumerate(list_func_names):
    if ("L" in elem): name_ext = "L"
    elif ("R" in elem): name_ext = "R"
    if ("F" in fit_type): name_ext = "F"

    min_A = 0.0
    max_A = 14.0e5 if "F" in name_ext else  7.0e5
    min_B =-12.0e4 if "F" in name_ext else -6.0e4
    max_B =  0.2   if "F" in name_ext else  0.1
    min_C = -4.0e4 if "F" in name_ext else -2.0e4
    max_C = 10.0e3 if "F" in name_ext else  5.0e3

    if useZoom and (infoDict["Target"]!="D"):
        # min_A = 0.0
        max_A = 4.0e5 if "F" in name_ext else  2.0e5
        min_B =-3.0e4 if "F" in name_ext else -1.5e4
        max_B = 0.2   if "F" in name_ext else  0.1
        min_C =-5.0e3 if "F" in name_ext else -2.5e3
        max_C = 4.0e3 if "F" in name_ext else  2.0e3

    ## Save A
    hist_A = parameter_A_list[e]
    hist_A.SetMinimum(min_A)
    hist_A.SetMaximum(max_A)

    hist_A.SetLineWidth(2)
    # hist_A.SetLineColor(ROOT.kBlue)
    hist_A.Write()
    hist_A.Draw("hist e")

    myStyle.DrawPreliminaryInfo("Parameter A %s"%fit_type)
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    outputName = myStyle.getPlotsFile("ParameterA%s"%zoom_ext, dataset, "gif", name_ext)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()
    # legend.Clear()

    ## Save B
    hist_B = parameter_B_list[e]
    hist_B.SetMinimum(min_B)
    hist_B.SetMaximum(max_B)

    hist_B.SetLineWidth(2)
    # hist_B.SetLineColor(ROOT.kBlue)
    hist_B.Write()
    hist_B.Draw("hist e")

    myStyle.DrawPreliminaryInfo("Parameter B %s"%fit_type)
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    outputName = myStyle.getPlotsFile("ParameterB%s"%zoom_ext, dataset, "gif", name_ext)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()

    ## Save C
    hist_C = parameter_C_list[e]
    hist_C.SetMinimum(min_C)
    hist_C.SetMaximum(max_C)

    hist_C.SetLineWidth(2)
    # hist_C.SetLineColor(ROOT.kBlue)
    hist_C.Write()
    hist_C.Draw("hist e")

    myStyle.DrawPreliminaryInfo("Parameter C %s"%fit_type)
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    outputName = myStyle.getPlotsFile("ParameterC%s"%zoom_ext, dataset, "gif", name_ext)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()

print("Made it to the end!")

outputFile.Write()
outputFile.Close()
inputfile.Close()
