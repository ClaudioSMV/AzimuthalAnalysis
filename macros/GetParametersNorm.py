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

useFold = options.fold
if "Fold" in myStyle.getCutStrFromStr(options.outputCuts):
    useFold = True
fit_type = "Fd" if useFold else "LR"

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
inputPath = myStyle.getPlotsFolder("Fit", input_cuts, infoDict["Target"], isJLab, False) # "../output/"
inputROOT = myStyle.getPlotsFile("Fit", dataset, "root", fit_type)
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = myStyle.getPlotsFolder("FitParametersNorm", plots_cuts, infoDict["Target"], isJLab)
outputROOT = myStyle.getPlotsFile("Parameters", dataset, "root", fit_type)
if (not options.Overwrite and os.path.exists(outputPath+outputROOT)):
    print("Parameters normalized file already exists! Not overwriting it.")
    exit()


list_func_names = ["crossSectionR"]
if not useFold:
    list_func_names.append("crossSectionL")

list_of_hists = inputfile.GetListOfKeys().Clone()
for elem in list_of_hists:
    if (elem.ReadObj().Class_Name() != "TH1D"):
        list_of_hists.Remove(elem)

th1_b_norm_pos_list = []
th1_b_norm_neg_list = []
th1_c_norm_pos_list = []
th1_c_norm_neg_list = []

for e,elem in enumerate(list_func_names):
    th1_b_norm_pos = TH1D("f_Norm_B%i_Pos"%e,";Bin;b_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    th1_b_norm_pos_list.append(th1_b_norm_pos)

    th1_b_norm_neg = TH1D("f_Norm_B%i_Neg"%e,";Bin;b_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    th1_b_norm_neg_list.append(th1_b_norm_neg)

    th1_c_norm_pos = TH1D("f_Norm_C%i_Pos"%e,";Bin;c_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    th1_c_norm_pos_list.append(th1_c_norm_pos)

    th1_c_norm_neg = TH1D("f_Norm_C%i_Neg"%e,";Bin;c_{%s}/a_{%s}"%(infoDict["Target"],infoDict["Target"]), list_of_hists.GetSize(),0.0,list_of_hists.GetSize())
    th1_c_norm_neg_list.append(th1_c_norm_neg)

print("")
print("Target %s"%infoDict["Target"])

index_h = 0
for i_h,h in enumerate(inputfile.GetListOfKeys()): #list_of_hists):
    # if (h.ReadObj().Class_Name() == "TH1D"):
    if ((h.ReadObj().Class_Name() == "TH1D") and ("Corr_Reconstru" in h.GetName())): ## ADD SUPPORT FOR ALL CORRECTIONS!
        hist_targ = h.ReadObj()
        hist_name = h.GetName() # Corr_Reconstru_Q0N0Z0_type (type: Fd or LR)

        tmp_name = "_".join(h.GetName().split("_")[1:-2]) # Reconstru
        bin_name = hist_name.split("_")[-2] # Q0N0Z0

        for i_f,f in enumerate(list_func_names):
            # Get covariance matrix
            name_cov = "%s_covM"%(bin_name)
            if "L" in f:
                name_cov+="L"
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
            th1_b_norm_pos_list[i_f].Fill(bin_name, 0.0)
            th1_b_norm_neg_list[i_f].Fill(bin_name, 0.0)
            th1_c_norm_pos_list[i_f].Fill(bin_name, 0.0)
            th1_c_norm_neg_list[i_f].Fill(bin_name, 0.0)

            # Get error propagated and fill B/A
            cov10 = GetMatrixElem(cov_matrix, 0, 1) # Get Cov AB
            err10 = PropErrorDivision(par1, err1, par0, err0, cov10)
            if (par1/par0)>0:
                th1_b_norm_pos_list[i_f].SetBinContent(index_h+1, (par1/par0))
                th1_b_norm_pos_list[i_f].SetBinError(index_h+1, err10)
            else:
                th1_b_norm_neg_list[i_f].SetBinContent(index_h+1, abs(par1/par0))
                th1_b_norm_neg_list[i_f].SetBinError(index_h+1, err10)

            # Get error propagated and fill C/A
            cov20 = GetMatrixElem(cov_matrix, 0, 2) # Get Cov AC
            err20 = PropErrorDivision(par2, err2, par0, err0, cov20)
            if (par2/par0)>0:
                th1_c_norm_pos_list[i_f].SetBinContent(index_h+1, (par2/par0))
                th1_c_norm_pos_list[i_f].SetBinError(index_h+1, err20)
            else:
                th1_c_norm_neg_list[i_f].SetBinContent(index_h+1, abs(par2/par0))
                th1_c_norm_neg_list[i_f].SetBinError(index_h+1, err20)
        index_h+=1


print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

### Ratio b/a and c/a per target
outputFile = TFile(outputPath+outputROOT,"RECREATE")

ymin = 0.001
ymax = 1.2
# canvas.SetLogy(0)
for e,elem in enumerate(list_func_names):
    if ("L" in elem): name_ext = "L"
    elif ("R" in elem): name_ext = "R"
    if ("F" in fit_type): name_ext = "F"

    ## Ratio b/a
    legend_b = TLegend(1-myStyle.GetMargin()-0.35,1-myStyle.GetMargin()-0.12, 1-myStyle.GetMargin()-0.05,1-myStyle.GetMargin()-0.02)
    legend_b.SetBorderSize(0)
    # legend_b.SetFillColor(ROOT.kWhite)
    legend_b.SetTextFont(myStyle.GetFont())
    legend_b.SetTextSize(myStyle.GetSize()-8)
    legend_b.SetFillStyle(0)
    ## Positive ratios
    hist_b_pos = th1_b_norm_pos_list[e]
    hist_b_pos.SetMinimum(ymin)
    hist_b_pos.SetMaximum(ymax)

    hist_b_pos.SetLineWidth(2)
    hist_b_pos.SetLineColor(ROOT.kBlue)
    legend_b.AddEntry(hist_b_pos,"Positive ratio")

    hist_b_pos.Write()
    hist_b_pos.Draw("hist e")

    hist_b_neg = th1_b_norm_neg_list[e]

    hist_b_neg.SetLineWidth(2)
    hist_b_neg.SetLineColor(ROOT.kRed)
    legend_b.AddEntry(hist_b_neg,"Negative ratio")

    hist_b_neg.Write()
    hist_b_neg.Draw("hist e same")

    legend_b.Draw()
    myStyle.DrawPreliminaryInfo("Parameters normalized %s"%(fit_type))
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    outputName = myStyle.getPlotsFile("ParameterNorm_B", dataset, "gif", name_ext)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()

    ## Ratio c/a
    # legend_c = TLegend()
    legend_c = TLegend(1-myStyle.GetMargin()-0.35,1-myStyle.GetMargin()-0.12, 1-myStyle.GetMargin()-0.05,1-myStyle.GetMargin()-0.02)
    legend_c.SetBorderSize(0)
    # legend_c.SetFillColor(ROOT.kWhite)
    legend_c.SetTextFont(myStyle.GetFont())
    legend_c.SetTextSize(myStyle.GetSize()-8)
    legend_c.SetFillStyle(0)
    ## Positive ratios
    hist_c_pos = th1_c_norm_pos_list[e]
    hist_c_pos.SetMinimum(ymin)
    hist_c_pos.SetMaximum(ymax)

    hist_c_pos.SetLineWidth(2)
    hist_c_pos.SetLineColor(ROOT.kBlue)
    legend_c.AddEntry(hist_c_pos,"Positive ratio")

    hist_c_pos.Write()
    hist_c_pos.Draw("hist e")

    hist_c_neg = th1_c_norm_neg_list[e]

    hist_c_neg.SetLineWidth(2)
    hist_c_neg.SetLineColor(ROOT.kRed)
    legend_c.AddEntry(hist_c_neg,"Negative ratio")

    hist_c_neg.Write()
    hist_c_neg.Draw("hist e same")

    legend_c.Draw()
    myStyle.DrawPreliminaryInfo("Parameters normalized %s"%(fit_type))
    myStyle.DrawTargetInfo(nameFormatted, "Data")

    outputName = myStyle.getPlotsFile("ParameterNorm_C", dataset, "gif", name_ext)
    canvas.SaveAs(outputPath+outputName)
    canvas.Clear()

outputFile.Write()
outputFile.Close()

print("Made it to the end!")

inputfile.Close()
