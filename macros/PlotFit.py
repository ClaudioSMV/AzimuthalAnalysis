from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle
from array import array

gROOT.SetBatch( True )
gStyle.SetOptFit(1)

## Defining Style
myStyle.ForceStyle()

gStyle.SetStatX(1 - myStyle.GetMargin() - 0.005)
gStyle.SetStatY(2*myStyle.GetMargin() + 0.205)


## Define functions

def Get_HistCorrected(h_input, h_name, this_fittype): # , opts):

    ### Get binning
    Nbins_in = h_input.GetXaxis().GetNbins()

    bin_frst = 0
    bin_last = Nbins_in
    list_xbin_out = []

    # if (this_fittype == "LR"):
    if (this_fittype == "Fd"):
        bin0 = h_input.FindBin(0.0)
        bin_frst = bin0

        list_xbin_out.append(0.0)
    # elif (this_fittype == "Sh"):

    ### Fill list with x-axis bin's limits
    for bt in range(bin_frst, bin_last+1):
        list_xbin_out.append(h_input.GetBinLowEdge(bt+1))

    ### Create output histogram
    phi_axis_title = myStyle.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"
    Nbins_out = len(list_xbin_out)-1
    h_output = TH1D("%s_%s"%(h_name, this_fittype), ";%s;Counts"%(phi_axis_title), Nbins_out, array('d',list_xbin_out))

    ### Fill output histogram
    # Run over original hist
    for b in range(1, Nbins_in+1):
        value = h_input.GetBinContent(b)
        error = h_input.GetBinError(b)

        this_bin = b

        # if (this_fittype == "LR"):
        if (this_fittype == "Fd"):

            x_center_in = h_input.GetBinCenter(b)

            bin_out = h_output.FindBin(abs(x_center_in))
            value_out = h_output.GetBinContent(bin_out)
            error_out = h_output.GetBinError(bin_out)

            # If bin is not empty, then you're running over the second tail and must add the new content
            if (value_out > 1.0):
            # if (value_out != 0.0):
                value+=value_out
                error = TMath.Sqrt(error_out*error_out + error*error)

            this_bin = bin_out
        # elif (this_fittype == "Sh"):

        # Debug
        # print(this_bin)

        h_output.SetBinContent(this_bin, value)
        h_output.SetBinError(this_bin, error)

    return h_output

def Get_FitFunctions(h_out, list_fname, this_fittype, opts):
    ### Options:
    ###     Skip0: Skip central peak
    ###     Sin: Use sin(x) term in fit

    # if (this_fittype == "LR"):
    # elif (this_fittype == "Fd"):
    # elif (this_fittype == "Sh"):

    ### Define options
    opt_sk0 = True if ("Sk0" in opts) else False
    opt_sin = True if ("Sin" in opts) else False

    ### Set limits
    Nbins = h_out.GetXaxis().GetNbins()

    ## Option: Skip peak's bin (Problematic)
    peak_Lend, peak_Rend = 0.0, 0.0

    if (opt_sk0):
        if (this_fittype == "LR"):
            bin_peak = h_out.FindBin(0.0)
            # if Nbins odd then; else;
            peak_Lend = h_out.GetBinLowEdge(bin_peak) if ((Nbins%2) == 1) else h_out.GetBinLowEdge(bin_peak-1)
            peak_Rend = h_out.GetBinLowEdge(bin_peak+1) # if ((Nbins%2) == 1) else h_out.GetBinLowEdge(bin_peak+1)
        elif (this_fittype == "Fd"):
            # peak_Lend = 0.0 # useless
            peak_Rend = h_out.GetBinLowEdge(2)
        elif (this_fittype == "Sh"):
            # if Nbins odd then; else;
            peak_Lend = h_out.GetBinLowEdge(Nbins+1) if ((Nbins%2) == 1) else h_out.GetBinLowEdge(Nbins)
            peak_Rend = h_out.GetBinLowEdge(2) # if ((Nbins%2) == 1) else h_out.GetBinLowEdge(2)


    xmin_out = h_out.GetBinLowEdge(1)
    xmax_out = h_out.GetBinLowEdge(Nbins+1)
    list_limits = []

    ## for [Right, Left*]
    for i,func in enumerate(list_fname):

        this_xmin, this_xmax = xmin_out, xmax_out

        if (this_fittype == "LR"):
            this_xmin = peak_Rend if (i==0) else  xmin_out
            this_xmax =  xmax_out if (i==0) else peak_Lend
        elif (this_fittype == "Fd"):
            this_xmin = peak_Rend
            this_xmax =  xmax_out
        elif (this_fittype == "Sh"):
            this_xmin = peak_Rend
            this_xmax = peak_Lend if (peak_Lend != 0.0) else xmax_out

        # print("  [Fit] Function %s limits: [%.2f, %.2f]"%(func, this_xmin, this_xmax))

        these_limits = [this_xmin, this_xmax]
        list_limits.append(these_limits)

    ### Define function
    the_func = "[0] + [1]*cos(TMath::Pi()*x/180.0) + [2]*cos(2*TMath::Pi()*x/180.0)"
    if (opt_sin):
        the_func+= "+ [3]*sin(TMath::Pi()*x/180.0)"

    tf1_fit = []

    ## for [Right, Left*]
    for i,fname in enumerate(list_fname):
        this_xmin = list_limits[i][0]
        this_xmax = list_limits[i][1]

        this_func = TF1(fname,the_func, this_xmin,this_xmax)
        tf1_fit.append(this_func)

    ### Return list with TF1 with the proper range
    return tf1_fit


def Get_Chi2ndf(fit_funct, x,y, position):
    chisq = fit_funct.GetChisquare()
    ndf = fit_funct.GetNDF()
    if (ndf != 0):
        str_Fit = TLatex(x,y, "#chi^{2} / ndf = %.2f / %i = %.2f"%(chisq, ndf, chisq/ndf))
    else:
        str_Fit = TLatex(x,y, "#chi^{2} / ndf = %.2f / %i"%(chisq, ndf))

    # 23: use center as reference (default method)
    text_orientation = 23
    if ("LR" in position):
        # 13: use left corner as reference (for R method); 33: use right corner as reference (for L method)
        text_orientation = 13 if ("0" in position) else 33
    # elif (this_fittype == "Fd"):
    # elif (this_fittype == "Sh"):

    str_Fit.SetTextAlign(text_orientation)
    str_Fit.SetTextSize(myStyle.GetSize()-6)

    return str_Fit


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")

parser.add_option('-F', dest='fold', action='store_true', default = False, help="Use fold tails (default fits both tails separated)")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False, help="Overwrite if file already exists")
parser.add_option('-s', dest='useSin', action='store_true', default = False, help="Add a sin\phi term in the fit (expected to be negligible)")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

# Define use of Fold method
use_Fold = options.fold
if "Fold" in myStyle.getCutStrFromStr(options.outputCuts):
    use_Fold = True

useSin = options.useSin
if (useSin or ("Sin" in myStyle.getCutStrFromStr(options.outputCuts))):
    useSin = True
    options.outputCuts += "_Fs"

use_Shift = False
if (("Shift" in myStyle.getCutsAsList(myStyle.getCutStrFromStr(options.outputCuts))) or ("Shift" in myStyle.getCutsAsList(myStyle.getCutStrFromStr(options.inputCuts)))):
    use_Shift = True
    # print("  [Fit] Fit PhiPQ shifted, ranging in ~(0., 360.)")


### Define type of fit used
# [LR] is default
fit_type = "LR"

if (use_Fold and use_Shift):
    print("  [Fit] More than one fit method selected. Please, choose only one of the options!")
    exit()
# [Fold]
elif (use_Fold):
    fit_type = "Fd"
# [Shift]
elif (use_Shift):
    fit_type = "Sh"
# [LR]
# else: fit_type = "LR" # Default

infoDict = myStyle.getDictNameFormat(dataset)
nameFormatted = myStyle.getNameFormatted(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"
if useSin:
    plots_cuts+="_Fs"

plots_cuts+="_"+fit_type # Add Fold or LR extension


## Input
inputPath = myStyle.getPlotsFolder("Correction", input_cuts, myStyle.getBinNameFormatted(dataset) + "/" + infoDict["Target"], isJLab, False) # "../output/"
inputROOT = myStyle.getPlotsFile("Corrected", dataset, "root")
inputfile = TFile(inputPath+inputROOT,"READ")

## Output
outputPath = myStyle.getPlotsFolder("Fit", plots_cuts, myStyle.getBinNameFormatted(dataset) + "/" + infoDict["Target"], isJLab)
outputROOT = myStyle.getPlotsFile("Fit", dataset, "root", fit_type)
if (not options.Overwrite and os.path.exists(outputPath+outputROOT)):
    print("  [Fit] Fit already exists! Not overwriting it.")
    exit()

list_of_hists = inputfile.GetListOfKeys()

### Define list with reco methods
type_reco = ["Reconstru", "ReMtch_mc", "ReMtch_re"] # Corr_
type_reco_short = ["Reco", "RMmc", "RMre"]

### Define list with fit names
list_fitfname = ["crossSectionR"]
if (fit_type == "LR"):
    list_fitfname.append("crossSectionL")
# elif (fit_type == "Fd"):
# elif (fit_type == "Sh"):

# ### UPDATE THIS!
# fit_opts = "" if not useSin else "Sin"
# fit_opts += "Skip0"

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)

outputfile = TFile(outputPath+outputROOT,"RECREATE")

phi_axis_title = myStyle.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"

for h in list_of_hists:
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_name = h.GetName() # Corr_Reconstru_Q0N0Z0
        if "Corr" in hist_name:

            # Name format is: Corr_Reconstru_Q0N0
            tmp_name = "_".join(hist_name.split("_")[1:-1]) # Reconstru
            this_nbin = hist_name.split("_")[-1] # Q0N0Z0

            type_index = type_reco.index(tmp_name) # Index in ["Reconstru", "ReMtch_mc", "ReMtch_re"]

            # Get Histogram
            hist = h.ReadObj()

            Nbins = hist.GetXaxis().GetNbins()
            bin1 = hist.GetBinContent(1)
            bin2 = hist.GetBinContent(2)

            ### Skip empty histograms
            # print("  GetEntries: %i;  GetNbins: %i ;  Value bin1: %i; bin2: %i"%(hist.GetEntries(),Nbins, bin1, bin2))
            if (hist.GetEntries() == 0): # Maybe require a minimum number of entries?
                print("  [Fit] Histogram %s is empty! Fit is not possible."%hist_name)
                continue

            ### Get corrected histogram
            hist_corr = Get_HistCorrected(hist, hist_name, fit_type)

            hist_corr.SetMinimum(0.0001)
            hist_corr.SetMaximum(hist_corr.GetMaximum()*1.4)
            hist_corr.Draw("hist axis")

            ### Return list of TF1 with the proper range
            # Use plots_cuts to find special cuts/options
            list_tf1 = Get_FitFunctions(hist_corr, list_fitfname, fit_type, myStyle.getCutStrFromStr(plots_cuts)) # fit_opts

            ### Make fit and save covariance and correlation matrices
            list_this_chi2 = []
            for i,fitfunc in enumerate(list_tf1):
                this_fopts = "MSRQ" if (i==0) else "MSRQ+"
                fit_matrix = hist_corr.Fit(list_fitfname[i], this_fopts, "")

                name_cov  = "covM%i_%s_%s"%(i, this_nbin, type_reco_short[type_index]) # "covM0_Q0N0Z0_Reco" or "covM1_Q0N0Z0_Reco" (L)
                fit_matrix.GetCovarianceMatrix().Write(name_cov)

                name_corr = "corrM%i_%s_%s"%(i, this_nbin, type_reco_short[type_index]) # "corrM0_Q0N0Z0_Reco" or "corrM1_Q0N0Z0_Reco" (L)
                fit_matrix.GetCorrelationMatrix().Write(name_corr)

                ## Draw chi2 info
                xpos_tex, ypos_tex = 0.0, 1.1*hist.GetMaximum()
                if (fit_type == "LR"):
                    xpos_tex = 15 if (i==0) else -15
                elif (fit_type == "Fd"):
                    xpos_tex = 90
                elif (fit_type == "Sh"):
                    xpos_tex = 180

                this_chi2 = Get_Chi2ndf(fitfunc, xpos_tex,ypos_tex, "%s%i"%(fit_type,i))
                list_this_chi2.append(this_chi2)

            for c in list_this_chi2:
                c.Draw()

            ### Draw and save
            hist_corr.Draw("FUNC same")
            hist_corr.Write()

            myStyle.DrawPreliminaryInfo("Correction fit")
            myStyle.DrawTargetInfo(nameFormatted, "Data")
            myStyle.DrawBinInfo(this_nbin, infoDict["BinningType"])

            outputName = myStyle.getPlotsFile("Fit_"+tmp_name, dataset, "png",this_nbin)
            canvas.SaveAs(outputPath+outputName)
            canvas.Clear()

print("  [Fit] Fit parameters saved!")
outputfile.Close()
