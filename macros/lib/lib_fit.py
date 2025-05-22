from lib_error import error_msg,info_msg
from lib_constants import ordered_stages,available_fit_methods,MARGINS,SIZE_TEXT
from lib_style import axes_title
from ROOT import TH1D,TMath,TF1,TLatex
from array import array

                                     ################
#######################################    Fits    #######################################
#######################################   Naming   #######################################
                                     ################

def matrix_name(matrix_name, histogram_info, idx):
# Return name for matrix objects so that they are unique
    matrix_name = "M%s"%(matrix_name)

    return "_".join([matrix_name, histogram_info, str(idx)])

def get_fit_name(method_tag):
    return available_fit_methods[method_tag]["Name"]

                                   ###################
#####################################      Fits     ######################################
#####################################  Check input  ######################################
                                   ###################

def check_fit_method_exists(method_name, stage):
    shift_exception = ((method_name == "Sh") and (stage == "Correction"))
    if (ordered_stages.index(stage) <= ordered_stages.index("Correction")):
        return "" if not shift_exception else "Sh" # Use shift in corrected distribution
    if method_name not in available_fit_methods:
        error_msg("check_fit_method_exists", "Non-existent fit method!")

    return method_name

                                    #################
######################################     Fits    #######################################
######################################  Functions  #######################################
                                    #################

def get_fit_mathematical_expression(fit_method, use_sin):
    string = "[0]"
    string += " + [1]*cos(TMath::Pi()*x/180.0)"
    string += " + [2]*cos(2*TMath::Pi()*x/180.0)"
    if use_sin:
        string += " + [3]*sin(TMath::Pi()*x/180.0)"

    return string

def minimum_bins_required(fit_method, use_sin):
    function = get_fit_mathematical_expression(fit_method, use_sin)

    return function.count("[") + 1 # At least more than the ndf

def check_fit_feasibility(histogram, fit_method, use_sin):
# Check if histogram has problems that can affect the fit performance
# NOTE: GetEntries gives the number of no-null bins because of the use of SetBinContent
    hname = histogram.GetName()
    no_null_bins = histogram.GetEntries()
    nbins = histogram.GetXaxis().GetNbins()
    feasible = True
    if (no_null_bins == 0):
        feasible = False; msg = "Histogram is empty!"
    elif (no_null_bins < minimum_bins_required(fit_method, use_sin)):
        feasible = False; msg = "Histogram has not enough bins!"
    elif (fit_method == "Wg") and (no_null_bins < nbins/2.):
        feasible = False; msg = "Histogram has not enough bins for wing fit!"
    if not feasible: # Report if any problem has appeared
        info_msg("check_fit_feasibility", "%s: Fit not feasible. %s"%(hname, msg))

    return feasible

def new_axis_limits(histogram, fit_method):
    initial = 1 if (fit_method != "Fd") else histogram.FindBin(0.0)
    final = histogram.GetXaxis().GetNbins() + 1

    return [histogram.GetBinLowEdge(i) for i in range(initial, final + 1)]

def get_folded_bin(old_bin, old_zero, new_histogram):
# Return the correct bin to fill in the new histogram when folding distribution
    new_Nbins = new_histogram.GetXaxis().GetNbins()
    first_half = (new_Nbins - old_bin + 1 > 0)
    if first_half: # Here the new histogram is filled backwards!
        new_bin = new_Nbins - old_bin + 1
    else: # Here goes back to the normal filling direction
        new_bin = old_bin - old_zero + 1

    return new_bin

def adapt_histogram_to_fit(histogram, fit_method, new_name):
# Return histogram to fit, according to the fit method selected
    new_limits = new_axis_limits(histogram, fit_method)
    title = axes_title(histogram.GetXaxis().GetTitle(), histogram.GetYaxis().GetTitle())
    new_Nbins = len(new_limits) - 1
    new_histogram = TH1D(new_name, title, new_Nbins, array('d', new_limits))

    for i in range(1, histogram.GetXaxis().GetNbins() + 1):
        value = histogram.GetBinContent(i)
        error = histogram.GetBinError(i)

        if (fit_method == "Fd"): # Redefine bin number when folding
            new_bin = get_folded_bin(i, histogram.FindBin(0.0), new_histogram)

            if new_histogram.GetBinContent(new_bin): # Update bin value folded
                value += new_histogram.GetBinContent(new_bin)
                error = TMath.Sqrt(error**2 + new_histogram.GetBinError(new_bin)**2)

        new_bin = i if (fit_method != "Fd") else new_bin
        new_histogram.SetBinContent(new_bin, value)
        new_histogram.SetBinError(new_bin, error)
    new_histogram.SetMinimum(0.0001)
    new_histogram.SetMaximum(1.4 * new_histogram.GetMaximum())
    new_histogram.GetYaxis().SetMaxDigits(3)

    return new_histogram

def get_fit_limits(histogram, fit_method, side, skip_peak):
    bin_zero = histogram.FindBin(0.0)
    bin0, bin1 = 1, histogram.GetXaxis().GetNbins() + 1
    if side: # Used by "Wing" method only, for the moment
        if (side == "Right"):
            bin0 = bin_zero
        elif (side == "Left"):
            bin1 = bin_zero + 1
    if skip_peak: # Remove bin including the central peak!
        if (fit_method in ["Fd", "Sh"]) or (side == "Right"):
            bin0 += 1
        elif (side == "Left"):
            bin1 -= 1

    return histogram.GetBinLowEdge(bin0), histogram.GetBinLowEdge(bin1)

def get_fit_function(histogram, fit_name, fit_method, side, use_sin, skip_peak):
# Return TF1 with the correct fit range according to the method and cuts
    fit_expression = get_fit_mathematical_expression(fit_method, use_sin)
    fmin, fmax = get_fit_limits(histogram, fit_method, side, skip_peak)
    fit_function = TF1(fit_name, fit_expression, fmin, fmax)

    return fit_function

def print_fit_info(fit, side, color):
# Draw quality info from the fit
    align = 31
    xpos = 1 - MARGINS["R"] - 0.03
    if (side == "Left"):
        align = 11
        xpos = MARGINS["L"] + 0.03
    ypos = MARGINS["B"] + 0.03 + fit.GetNpar() * 0.05

    for i in range(fit.GetNpar() + 1):
        info = TLatex()
        info.SetNDC()
        info.SetTextAlign(align)
        info.SetTextColor(color)
        info.SetTextSize(SIZE_TEXT - 12)
        if (i == 0):
            string = "#chi^{2} / ndf = %.2f / %i"%(fit.GetChisquare(), fit.GetNDF())
            if fit.GetNDF():
                string += " = %.2f"%(fit.GetChisquare() / fit.GetNDF())
        else:
            parameter = i - 1
            value = fit.GetParameter(parameter)
            error = fit.GetParError(parameter)
            string = "%s = %.3e #pm %.3e"%("abcde"[parameter], value, error)
        info.DrawLatexNDC(xpos, ypos, string)
        ypos -= 0.05
