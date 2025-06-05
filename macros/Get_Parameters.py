import sys; sys.path.append('lib')
from ROOT import TFile
import optparse
from lib_style import force_style,create_canvas
from lib_cuts import check_cut_is_included,get_list_of_bincodes
from lib_fit import matrix_name
from lib_parameters import create_parameters_histograms,extract_fit_values
from lib_dataset_info import convert_info_tag_str_to_list,methods_under_use
from lib_error import info_msg
from lib_constants import available_fit_methods
from lib_histograms import create_bincode_histogram,get_input_histograms
import lib_naming as naming

force_style() # Defining Style

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-L', dest='run_local', action='store_true', default = False,
                  help="Run local files (Default uses folder from JLab_cluster)")
parser.add_option('-B', dest='bin_vars', default = "",
                  help="Work with these non-integratedd variables. Ex.: QNZ")
parser.add_option('-C', dest='cuts', default = "", help="Add input cuts FE_AQ_Xf_Yb_...")
parser.add_option('-F', dest='fit_method', default = "Ff", help="Add Fit method. Ex. Fd")

parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")
options, args = parser.parse_args()

dataset = options.Dataset
run_local = options.run_local
binvars = options.bin_vars
fit_method = options.fit_method

in_obj = naming.analysis_format("Fit", dataset, binvars, cuts=options.cuts,
                                 fit_method=fit_method, run_local=run_local)
inputfile = TFile(in_obj.get_file_root_files(), "READ")

out_obj = naming.analysis_format("Parameters", dataset, binvars, cuts=options.cuts,
                                 fit_method=fit_method, run_local=run_local)
outputfile_name = out_obj.get_file_root_files(options.Overwrite, True, True)

normalize = check_cut_is_included("Nm", options.cuts)

# Prepare histograms to fill
list_of_bincodes = get_list_of_bincodes(dataset, binvars)
histogram_template = create_bincode_histogram("template", list_of_bincodes)
dictionary_input_histograms = get_input_histograms(inputfile)
n_fits = len(available_fit_methods[fit_method]["Sides"])
n_pars = dictionary_input_histograms.values()[0].GetFunction("fit0").GetNpar()
listed_reco_methods = methods_under_use(dictionary_input_histograms)
histograms_to_fill = create_parameters_histograms(histogram_template, out_obj,
                                                  listed_reco_methods, n_fits, n_pars)
# Create canvas
canvas = create_canvas()
outputfile = TFile(outputfile_name, "RECREATE")
target, nbin, _ = convert_info_tag_str_to_list(dataset)

for (hname, input_histogram) in dictionary_input_histograms.items():
    input_info = naming.extract_histogram_info(hname)
    reco_method, bincode = input_info["Reco_method"], input_info["Bincode"]

    for (name, histogram) in histograms_to_fill.items():
        info = naming.extract_histogram_info(name, has_fit_info=True)
        if (info["Reco_method"] != reco_method):
            continue
        fit_idx, parameter = int(info["Fit_idx"]), int(info["Par_idx"])
        fit = input_histogram.GetFunction("fit%i"%(fit_idx))

        covariance = inputfile.Get(matrix_name("Cov", input_info["NoName"], fit_idx))
        asymmetry = ("Asymmetry" in info["Name"])
        value, error = extract_fit_values(fit, parameter, covariance_matrix=covariance,
                                          is_asymmetry=asymmetry, prenormalized=normalize)
        bin = histogram.GetXaxis().FindBin(bincode)
        histogram.SetBinContent(bin, value)
        histogram.SetBinError(bin, error)

for name in sorted(histograms_to_fill.keys()): # Remember to save histograms!
    histograms_to_fill[name].Write()

info_msg("Get_Parameters", "Made it to the end!\n")
outputfile.Close()
inputfile.Close()
