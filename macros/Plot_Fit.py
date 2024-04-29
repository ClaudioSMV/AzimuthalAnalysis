from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,\
    TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,\
    kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
import myNameFormat as nf
from array import array

## Defining Style
ms.force_style()
gStyle.SetTitleYOffset(1.2)
# Show Fit stats in correct position
gStyle.SetOptFit(1)
margin = ms.get_margin()
gStyle.SetStatX(1 - margin - 0.005)
gStyle.SetStatY(2*margin + 0.205)

colors = ms.get_color()

## Define functions

def histogram_has_problems(histogram, fit_method):
# Check if histogram has problems that can affect the fit performance
    hist_name = histogram.GetName()
    # Since Correction fills each bin with SetBinContent, GetEntries gives the
    # number of bins with a non-zero value
    hist_entries = histogram.GetEntries()
    hist_nbins = histogram.GetXaxis().GetNbins()
    has_problems = False
    # Skip empty histograms!
    if (hist_entries == 0):
        info_txt = "Histogram %s is empty! Fit is not possible."%(hname)
        has_problems = True
    # Report histograms without enough bins to perform fit (4 ndf needed)
    elif (hist_entries < 4):
        info_txt = "Histogram %s has not enough bins!"\
                   " Fit is not feasible."%(hname)
        has_problems = True
    elif ((fit_method is "LR") and (hist_entries < hist_nbins/2.)):
        info_txt = "Histogram %s has half or more empty bins!"\
                   " Fit LR is not feasible."%hname
        has_problems = True

    # Report if any problem has appeared
    if has_problems:
        ms.info_msg("Fit", info_txt)

    return has_problems

def get_correct_histogram_to_fit(histogram, hname, fit_method):
# Return copy of histogram with the adequate distribution according to the
# fit method selected
    nbins = histogram.GetXaxis().GetNbins()
    bin_zero = histogram.FindBin(0.0)
    # Get bin limits to create corrected histogram to fit
    idx_i = 1 if (fit_method != "Fd") else bin_zero
    idx_f = nbins + 1
    list_limits = [histogram.GetBinLowEdge(b) for b in range(idx_i, idx_f + 1)]

    htitle_x = histogram.GetXaxis().GetTitle()
    htitle_y = histogram.GetYaxis().GetTitle()
    htitle = ";%s;%s"%(htitle_x, htitle_y)
    nbins_to_fit = len(list_limits) - 1
    histogram_to_fit = TH1D(hname, htitle, nbins_to_fit, array('d',list_limits))

    # Fill histogram suitable to fit
    for b in range(1, nbins + 1):
        value = histogram.GetBinContent(b)
        error = histogram.GetBinError(b)

        # Redefine bin number when folding
        if (fit_method is "Fd"):
            is_first_half = (nbins_to_fit - b + 1 > 0)
            # Get correct bin position of the first half in the new histogram
            if is_first_half:
                b = nbins_to_fit - b + 1
            # Same with second half
            else:
                b = b - bin_zero + 1

            # Obtain value in new histogram (zero if empty)
            value_new = histogram_to_fit.GetBinContent(b)
            # Update value if non-zero (i.e. we are in second half)
            if value_new:
                value = value + value_new
                error_new = histogram_to_fit.GetBinError(b)
                error = TMath.Sqrt(error*error + error_new*error_new)

        histogram_to_fit.SetBinContent(b, value)
        histogram_to_fit.SetBinError(b, error)

    # Define corrected plot style
    histogram_to_fit.SetMinimum(0.0001)
    histogram_to_fit.SetMaximum(1.4 * histogram_to_fit.GetMaximum())
    histogram_to_fit.GetYaxis().SetMaxDigits(3)

    return histogram_to_fit

def get_fit_function(histogram_to_fit, tf1_name, fit_method, cut_str):
# Return TF1 with the correct fit range according to the method and cuts
    skip_central_peak = ms.cut_is_included("NP", cut_str)
    add_sin_term = ms.cut_is_included("Fs", cut_str)

    # Create function string
    fit_str = "[0] + [1]*cos(TMath::Pi()*x/180.0) +"\
                   " [2]*cos(2*TMath::Pi()*x/180.0)"
    if add_sin_term:
        fit_str+= "+ [3]*sin(TMath::Pi()*x/180.0)"

    # Select correct fit range
    nbins = histogram_to_fit.GetXaxis().GetNbins()
    bin_i, bin_f = 1, nbins
    xmin = histogram_to_fit.GetBinLowEdge(bin_i)
    xmax = histogram_to_fit.GetBinLowEdge(bin_f + 1)
    # Change values for LR method
    bin_zero = histogram_to_fit.FindBin(0.0)
    if fit_method is "LR":
        if "L" in tf1_name:
            xmax = histogram_to_fit.GetBinLowEdge(bin_zero + 1)
        else:
            xmin = histogram_to_fit.GetBinLowEdge(bin_zero)

    # Skip bin zero if required
    if skip_central_peak:
        # fit_function.RejectPoint(bin_zero) # Did not work :(
        if (fit_method is "Fd") or (fit_method is "Sh"):
            xmin = histogram_to_fit.GetBinLowEdge(bin_i + 1)
        elif (fit_method is "LR"):
            if "L" in tf1_name:
                xmax = histogram_to_fit.GetBinLowEdge(bin_zero)
            else:
                xmin = histogram_to_fit.GetBinLowEdge(bin_zero + 1)

    # Create fit object TF1
    fit_function = TF1(tf1_name, fit_str, xmin, xmax)

    return fit_function

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
parser.add_option('-b', dest='nonIntegratedVars', default = "",
                  help="Add non-integratedd bins like in QNZ")
parser.add_option('-i', dest='inputCuts', default = "",
                  help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "",
                  help="Add output cuts FE_...")

parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")

# input: <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
isJLab = options.isJLab
ovr = options.Overwrite

bin_set = options.nonIntegratedVars
input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts
if bin_set:
    input_cuts+= "_b%s"%bin_set
    plots_cuts+= "_b%s"%bin_set

fit_method = ms.get_fit_method(plots_cuts)
# d_bin = ms.get_name_dict(dataset)

in_obj = nf.naming_format("Correction", dataset, cuts=input_cuts,
                          is_JLab=isJLab)
inputfile = TFile(in_obj.get_path(),"READ")

out_obj = nf.naming_format("Fit", dataset, cuts=plots_cuts,
                          is_JLab=isJLab)

# Get dataset info
dataset_info = ms.get_name_dict(dataset)
nbin_dataset = dataset_info["nBin"]
target = dataset_info["Target"]

# Retrieve all saved in input file
list_of_keys = inputfile.GetListOfKeys()

# Create canvas and output
canvas = ms.create_canvas()
outputfile = TFile(out_obj.get_path(True, ovr),"RECREATE")

for key in list_of_keys:
    key_type = key.ReadObj().Class_Name()
    # Skip if object is not an histogram
    if "TH1" not in key_type:
        continue

    # Use corrected histograms only
    hname = key.GetName()
    if "raw" in hname.lower():
        continue

    # Check if fit can be done
    histogram = key.ReadObj()
    has_problems = histogram_has_problems(histogram, fit_method)
    if has_problems:
        continue

    # Update output object (Name format: h(name)_(acc_meth)_(bincode))
    _, cor_meth, bincode = hname.split("_")
    out_obj.updt_acc_method(cor_meth)
    out_obj.updt_bin_code(bincode)
    hname_new = out_obj.get_hist_name()
    list_fit_names = out_obj.get_l_fitnames()

    # Normalize distribution before perform fit
    if ms.cut_is_included("Nm", plots_cuts):
        histogram.Scale(1.0 / histogram.Integral("width"))

    # Get histogram to fit according to method selected
    histogram_to_fit = get_correct_histogram_to_fit(histogram, hname_new, fit_method)
    histogram_to_fit.Draw("hist axis")

    # Make fit for each fit name available
    for i,fname in enumerate(list_fit_names):
        fit = get_fit_function(histogram_to_fit, fname, fit_method, plots_cuts)
        fit_color = colors[5] if i is 0 else colors[1]
        fit.SetLineColor(fit_color)
        fit_opts = "MSRQ" if "L" not in fname else "MSRQ+"
        fit_matrix = histogram_to_fit.Fit(fname, fit_opts, "")

        # Save covariance and correlation matrices
        covariance_name = out_obj.get_matrix_name("cov", i)
        fit_matrix.GetCovarianceMatrix().Write(covariance_name)
        correlation_name = out_obj.get_matrix_name("corr", i)
        fit_matrix.GetCorrelationMatrix().Write(correlation_name)

        # Draw fit info
        chi_square = fit.GetChisquare()
        ndf = fit.GetNDF()
        fit_info_str = "#chi^{2} / ndf = %.2f / %i"%(chi_square, ndf)
        if ndf:
            fit_info_str+= " = %.2f"%(chi_square/ndf)

        fit_info_Latex = TLatex()
        x_fit = ms.get_pad_center()
        y_fit = 1 - 2*margin - 0.02 - i*margin
        fit_info_Latex.SetTextAlign(23)
        fit_info_Latex.SetTextColor(fit_color)
        fit_info_Latex.SetTextSize(ms.get_size() - 6)
        fit_info_Latex.DrawLatexNDC(x_fit, y_fit, fit_info_str)

    # Draw and save
    histogram_to_fit.Draw("FUNC same")
    histogram_to_fit.Write()

    ms.draw_preliminary("Correction fit")
    ms.draw_targetinfo(ms.get_name_format(dataset), "Data")
    ms.draw_bininfo(bincode, nbin_dataset)

    out_obj.updt_extension("png")
    canvas.SaveAs(out_obj.get_path())

    # out_obj.updt_extension("pdf")
    # canvas.SaveAs(out_obj.get_path())

    canvas.Clear()

ms.info_msg("Fit", "Fit parameters saved!\n")
outputfile.Close()
