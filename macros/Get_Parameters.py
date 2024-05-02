from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,\
    TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,\
    kWhite,TH1
import ROOT
import os
import optparse
from copy import copy
import myStyle as ms
import myNameFormat as nf
import mySumFunctions as sf

## Defining Style
ms.force_style()

## Define functions

def create_label_histogram(hname, list_bincodes):
# Create histogram with bincode labels in x-axis
    n_bincodes = len(list_bincodes)
    histogram_with_labels = TH1D(hname, "", n_bincodes, 0, n_bincodes)
    # Set label with bincode to each bin
    for b in range(1, n_bincodes + 1):
        histogram_with_labels.GetXaxis().SetBinLabel(b, list_bincodes[b-1])

    return histogram_with_labels

def propagate_error_division(v1, e1, v2, e2, cov = 0):
# Propagate error using proper formula with covariance included
    r1 = e1/v1
    r2 = e2/v2
    error_value = TMath.Abs(v1/v2)*TMath.Sqrt(r1*r1 + r2*r2 - 2*cov/(v1*v2))

    return error_value

def get_matrix_element(matrix, row, col):
# Return element in position row,col of matrix
    matrix_array = matrix.GetMatrixArray()
    index = col + matrix.GetNcols() * row

    return matrix_array[index]

def fill_parameters_histogram(name_obj, fit, dictionary_hist, covariance_matrix,
                   is_prenormalized = False):
    name = name_obj.name
    n_parameters = fit.GetNpar()
    function_idx = 0 if "R" in fit.GetName() else 1
    for p in range(n_parameters):
        hname_pars = name_obj.get_hist_name_parameters(function_idx, par=p)
        hname_pars = nf.get_hist_hfullname(hname_pars)

        # Create histograms if not in dictionary!
        if hname_pars not in dictionary_hist:
            # Create histogram with bincodes in x-axis to fill with parameters
            hist = create_label_histogram(hname_pars, list_bincodes)
            dictionary_hist[hname_pars] = hist

        # Get parameters and errors from fit
        value = fit.GetParameter(p)
        error = fit.GetParError(p)
        # Modify parameter according to definition of asymmetry <cos\phi> = B/2A
        if ("Asymmetry" in name) and (not is_prenormalized):
            # Remember the factor 1/2 to match the definition!
            weight = 1./2
            # Get info of first parameter
            value0 = fit.GetParameter(0)
            error0 = fit.GetParError(0)
            cov = get_matrix_element(covariance_matrix, 0, p)
            # Get normalization
            asym_value = value/value0
            asym_error = propagate_error_division(value, error, value0, error0, cov)
            # Update final numbers with correct weights
            value = weight * asym_value
            error = weight * asym_error
        elif ("Asymmetry" in name) and is_prenormalized:
            # Prenormalization gives p1 = B/2piA, so to be consistent with the
            # asymmetry definition a pi factor must be added
            # NOTE: The factor is transformed from \pi radians to 180. degrees
            # because the x-axis is given in degrees!
            value = 180. * value
            error = 180. * error

        # Get histogram and fill
        histogram = dictionary_hist[hname_pars]
        hbin = histogram.GetXaxis().FindBin(name_obj.bin_code)
        histogram.SetBinContent(hbin, value)
        histogram.SetBinError(hbin, error)


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
parser.add_option('-b', dest='nonIntegratedVars', default = "",
                  help="Add non-integratedd bins like in QNZ")
parser.add_option('-i', dest='inputCuts', default = "",
                  help="Add input cuts Xf_Yb_Z/P...")
parser.add_option('-o', dest='outputCuts', default = "",
                  help="Add output cuts FE_...")

parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")

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

# Define Input
in_obj = nf.naming_format("Fit", dataset, cuts=input_cuts,
                          is_JLab=isJLab)
inputfile = TFile(in_obj.get_path(),"READ")

out_obj = nf.naming_format("Parameters", dataset, cuts=plots_cuts,
                           is_JLab=isJLab)

# Get dataset info
fit_method = ms.get_fit_method(input_cuts)
dataset_info = ms.get_name_dict(dataset)
nbin_dataset = dataset_info["nBin"]
target = dataset_info["Target"]

is_normalized = ms.cut_is_included("Nm", input_cuts)

# Retrieve all saved in input file
list_of_keys = inputfile.GetListOfKeys()
list_bincodes = ms.get_bincode_list(nbin_dataset, input_cuts)

# Create canvas and output
canvas = ms.create_canvas()
outputfile = TFile(out_obj.get_path(True, ovr),"RECREATE")

# Create dictionary to save histograms 
dictionary_hparameter = {}
for key in list_of_keys:
    key_type = key.ReadObj().Class_Name()
    # Skip if object is not an histogram
    if "TH1" not in key_type:
        continue

    # Extract info from name
    histogram = key.ReadObj()
    hname_input = histogram.GetName()
    acceptance_method = nf.get_hist_hmeth(hname_input)
    bincode = nf.get_hist_hbincode(hname_input)

    # Update objects to name
    out_obj.updt_acc_method(acceptance_method); out_obj.updt_bin_code(bincode)
    # hname_new = out_obj.get_hist_name()
    list_fit_names = out_obj.get_l_fitnames()

    # Extract parameters for each function available
    for i,fname in enumerate(list_fit_names):
        fit = histogram.GetFunction(fname)
        covariance_name = out_obj.get_matrix_name("cov", i)
        covariance = inputfile.Get(covariance_name)
        name_obj = copy(out_obj)
        # Create and fill "bare" parameters histograms
        name_obj.updt_name("Parameters")
        fill_parameters_histogram(name_obj, fit, dictionary_hparameter,
                                  covariance, is_normalized)
        # Create and fill asymmetry parameters histograms
        name_obj.updt_name("Asymmetry")
        fill_parameters_histogram(name_obj, fit, dictionary_hparameter,
                                  covariance, is_normalized)

# Save histograms with info in the output file
for hname, histogram in dictionary_hparameter.items():
    histogram.Write()

ms.info_msg("Get_Parameters", "Made it to the end!\n")
outputfile.Close()
inputfile.Close()
