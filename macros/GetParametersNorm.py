from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
myStyle.ForceStyle()

# gStyle.SetStatX(1 - myStyle.GetMargin() - 0.005)
# gStyle.SetStatY(2*myStyle.GetMargin() + 0.205)

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
parser.add_option('-v', dest='verbose', action='store_true', default = False, help="Print values")

parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default does not)")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False, help="Overwrite if file already exists")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster
verbose = options.verbose

use_Fold = options.fold
if (use_Fold):
    options.inputCuts+="_Fd"

### Define type of fit used
fit_type = myStyle.GetFitMethod(options.inputCuts +"_"+ options.outputCuts)

infoDict = myStyle.getDictNameFormat(dataset)
nameFormatted = myStyle.getNameFormatted(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"

# Add fit type to the list of cuts!
input_cuts+="_"+fit_type # Add Fold or LR extension
plots_cuts+="_"+fit_type

## Input
inputPath = myStyle.getPlotsFolder("Fit", input_cuts, myStyle.getBinNameFormatted(dataset) + "/" + infoDict["Target"], isJLab, False) # "../output/"
inputROOT = myStyle.getPlotsFile("Fit", dataset, "root", fit_type)
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = myStyle.getPlotsFolder("ParametersNorm", plots_cuts, myStyle.getBinNameFormatted(dataset) + "/" + infoDict["Target"], isJLab)
outputROOT = myStyle.getPlotsFile("Parameters", dataset, "root", fit_type)
if (not options.Overwrite and os.path.exists(outputPath+outputROOT)):
    print("  [ParNorm] Parameters normalized file already exists! Not overwriting it.")
    exit()

### Define list with fit names
list_func_names = ["crossSectionR"]
if (fit_type == "LR"):
    list_func_names.append("crossSectionL")

n_htypeReco = [0, 0, 0]

list_of_hists = inputfile.GetListOfKeys().Clone()
for elem in list_of_hists:
    if (elem.ReadObj().Class_Name() != "TH1D"):
        list_of_hists.Remove(elem)

    else:
        if ("Corr_Reconstru" in elem.GetName()):
            n_htypeReco[0]+=1
        elif ("Corr_ReMtch_mc" in elem.GetName()):
            n_htypeReco[1]+=1
        elif ("Corr_ReMtch_re" in elem.GetName()):
            n_htypeReco[2]+=1

print("Corr_Reconstru: %i"%n_htypeReco[0])
print("Corr_ReMtch_mc: %i"%n_htypeReco[1])
print("Corr_ReMtch_re: %i"%n_htypeReco[2])

type_reco = ["Reconstru",] # Corr_
type_reco_short = ["Reco",]

if n_htypeReco[1]!=0:
    type_reco.append("ReMtch_mc")
    type_reco_short.append("RMmc")

if n_htypeReco[2]!=0:
    type_reco.append("ReMtch_re")
    type_reco_short.append("RMre")


th1_b_norm_list = [[],[],[]]
th1_c_norm_list = [[],[],[]]

# print(list_of_hists.GetSize())
for e,elem in enumerate(list_func_names):
    for t,typeR in enumerate(type_reco_short):
        this_n = n_htypeReco[t]
        if (this_n>0):
            th1_b_norm = TH1D("f_Norm_B%i_%s"%(e,typeR),";Bin;b/a", this_n,0.0,this_n)
            th1_b_norm_list[t].append(th1_b_norm)

            th1_c_norm = TH1D("f_Norm_C%i_%s"%(e,typeR),";Bin;c/a", this_n,0.0,this_n)
            th1_c_norm_list[t].append(th1_c_norm)

print("")
print("Parameters Norm of target %s"%infoDict["Target"])

binIndex_htype = list(n_htypeReco) # [X, Y, Z] This will give the bins remaining in the different Reco Methods (after the loop will be full of 0s)

for i_h,h in enumerate(inputfile.GetListOfKeys()): #list_of_hists):
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_targ = h.ReadObj()
        hist_name = h.GetName() # Corr_Reconstru_Q0N0Z0_type (type: Fd or LR)
        # print(hist_name)

        tmp_name = "_".join(h.GetName().split("_")[1:-2]) # Reconstru
        bin_name = hist_name.split("_")[-2] # Q0N0Z0

        type_index = type_reco.index(tmp_name) # Index in ["Reconstru", "ReMtch_mc", "ReMtch_re"]

        this_binIndex = n_htypeReco[type_index] - binIndex_htype[type_index] # X-X = 0, next X-(X-1) = 1, ..., X-(X-X) = X

        for i_f,f in enumerate(list_func_names):
            # Get covariance matrix
            # name_cov = "covM" # "covM"
            # if "L" in f:
            #     name_cov+="L" # "covML"

            name_cov = "covM1" if "L" in f else "covM0"

            name_cov+="_%s_%s"%(bin_name, type_reco_short[type_index]) # "covM0_Q0N0Z0_Reco" or "covM1_Q0N0Z0_Reco" (L)
            cov_matrix = inputfile.Get(name_cov)

            fit_targ = hist_targ.GetFunction(f)
            par0 = fit_targ.GetParameter(0)
            par1 = fit_targ.GetParameter(1)
            par2 = fit_targ.GetParameter(2)

            err0 = fit_targ.GetParError(0)
            err1 = fit_targ.GetParError(1)
            err2 = fit_targ.GetParError(2)

            if verbose:
                print("%s Fit: %s"%(hist_name, f))
                print("Solid     : (%6.2f, %5.2f, %5.2f)"%(par0, par1, par2))
                print("Normalized: (%6.2f, %5.2f, %5.2f)"%(par0/par0, par1/par0, par2/par0))
                print("")

            # Fill norm hists with the name (string as label per bin)

            th1_b_norm_list[type_index][i_f].Fill(bin_name, 0.0)
            th1_c_norm_list[type_index][i_f].Fill(bin_name, 0.0)

            # Get error propagated and fill B/A
            cov10 = GetMatrixElem(cov_matrix, 0, 1) # Get Cov AB
            err10 = PropErrorDivision(par1, err1, par0, err0, cov10)

            th1_b_norm_list[type_index][i_f].SetBinContent(this_binIndex+1, (par1/par0))
            th1_b_norm_list[type_index][i_f].SetBinError(this_binIndex+1, err10)

            # Get error propagated and fill C/A
            cov20 = GetMatrixElem(cov_matrix, 0, 2) # Get Cov AC
            err20 = PropErrorDivision(par2, err2, par0, err0, cov20)

            th1_c_norm_list[type_index][i_f].SetBinContent(this_binIndex+1, (par2/par0))
            th1_c_norm_list[type_index][i_f].SetBinError(this_binIndex+1, err20)

        binIndex_htype[type_index]-=1


print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

### Ratio b/a and c/a per target
outputFile = TFile(outputPath+outputROOT,"RECREATE")

ymin = -1.2
ymax =  1.2
# canvas.SetLogy(0)
for e,elem in enumerate(list_func_names):
    for t,typeR in enumerate(type_reco_short):

        name_ext = myStyle.GetFitExtension(fit_type, elem)

        ## Ratio b/a
        # legend_b = TLegend(1-myStyle.GetMargin()-0.35,1-myStyle.GetMargin()-0.12, 1-myStyle.GetMargin()-0.05,1-myStyle.GetMargin()-0.02)
        # legend_b.SetBorderSize(0)
        # # legend_b.SetFillColor(ROOT.kWhite)
        # legend_b.SetTextFont(myStyle.GetFont())
        # legend_b.SetTextSize(myStyle.GetSize()-8)
        # legend_b.SetFillStyle(0)
        ## Positive ratios
        hist_b = th1_b_norm_list[t][e]
        hist_b.SetMinimum(ymin)
        hist_b.SetMaximum(ymax)

        hist_b.SetLineWidth(2)
        hist_b.SetLineColor(ROOT.kBlue)
        # legend_b.AddEntry(hist_b,"Positive ratio")

        hist_b.Write()
        hist_b.Draw("hist e")

        # legend_b.Draw()
        myStyle.DrawPreliminaryInfo("Parameters normalized %s"%(fit_type))
        myStyle.DrawTargetInfo(nameFormatted, "Data")

        outputName = myStyle.getPlotsFile("ParNorm_B_%s"%(typeR), dataset, "png", name_ext)
        canvas.SaveAs(outputPath+outputName)
        canvas.Clear()

        ## Ratio c/a
        # legend_c = TLegend(1-myStyle.GetMargin()-0.35,1-myStyle.GetMargin()-0.12, 1-myStyle.GetMargin()-0.05,1-myStyle.GetMargin()-0.02)
        # legend_c.SetBorderSize(0)
        # # legend_c.SetFillColor(ROOT.kWhite)
        # legend_c.SetTextFont(myStyle.GetFont())
        # legend_c.SetTextSize(myStyle.GetSize()-8)
        # legend_c.SetFillStyle(0)
        ## Positive ratios
        hist_c = th1_c_norm_list[t][e]
        hist_c.SetMinimum(ymin)
        hist_c.SetMaximum(ymax)

        hist_c.SetLineWidth(2)
        hist_c.SetLineColor(ROOT.kBlue)
        # legend_c.AddEntry(hist_c,"Positive ratio")

        hist_c.Write()
        hist_c.Draw("hist e")

        # legend_c.Draw()
        myStyle.DrawPreliminaryInfo("Parameters normalized %s"%(fit_type))
        myStyle.DrawTargetInfo(nameFormatted, "Data")

        outputName = myStyle.getPlotsFile("ParNorm_C_%s"%(typeR), dataset, "png", name_ext)
        canvas.SaveAs(outputPath+outputName)
        canvas.Clear()

outputFile.Write()
outputFile.Close()

print("  [ParNorm] Made it to the end!")

inputfile.Close()
