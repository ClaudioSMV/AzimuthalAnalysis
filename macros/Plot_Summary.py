import sys; sys.path.append('lib')
from ROOT import TFile, gROOT
import optparse
from lib_style import force_style, create_canvas, draw_preliminary, draw_targetinfo
from lib_constants import targets_set_info, MARGINS
from lib_histograms import get_input_histograms
from lib_summary import canvas_partition, get_number_of_pads, create_summary_histogram, \
    create_histograms_in_this_canvas, fill_histograms, create_axes_histogram, \
    draw_histograms, draw_legend
from lib_error import info_msg, error_msg
import lib_naming as naming

force_style() # Defining Style
gROOT.SetBatch(True)


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <binType>_<Ndims>")
parser.add_option('-L', dest='run_local', action='store_true', default = False,
                  help="Run local files (Default uses folder from JLab_cluster)")
parser.add_option('-B', dest='bin_vars', default = "",
                  help="Work with these non-integratedd variables. Ex.: QNZ")
parser.add_option('-C', dest='cuts', default = "", help="Add input cuts FE_AQ_Xf_Yb_...")
parser.add_option('-F', dest='fit_method', default = "Ff", help="Add Fit method. Ex. Fd")
parser.add_option('-S', dest='targets_set', default = "", help="Solid (S) or Liquid (L)")

# parser.add_option('-y', dest='y_symmetric', action='store_true', default = False,
#                   help="Use symmetric y-limits (default False)")
parser.add_option('-b', '--Single_bin', dest='single_bin', default = "",
                  help="Draw only one single bin (Format Q0N0)")
options, args = parser.parse_args()

dataset = options.Dataset
run_local = options.run_local
binvars = options.bin_vars
fit_method = options.fit_method
targets_set = options.targets_set
single_bin = options.single_bin

targets_info = targets_set_info[targets_set]
listed_targets = targets_info["List"]
inputfiles = []
for (i, target) in enumerate(listed_targets): # Open input files
    idataset = "%s_%s"%(target, dataset)
    in_obj = naming.analysis_format("Parameters", idataset, binvars, cuts=options.cuts,
                                    run_local=run_local, fit_method=fit_method)
    inputfile = TFile(in_obj.get_file_root_files(), "READ")
    inputfiles.append(inputfile)
list_of_input_names = get_input_histograms(inputfiles[0]).keys()

# Asymmetry section
asymmetry_obj = naming.summary_format("Asymmetry", dataset, binvars, targets_set,
                                      cuts=options.cuts, run_local=run_local,
                                      fit_method=fit_method)
canvas_xbins, canvas_ybins = get_number_of_pads(asymmetry_obj, single_bin)
template = create_summary_histogram(asymmetry_obj, single_bin)
asymmetry_input_names = [name for name in list_of_input_names if "Asymmetry" in name]

for (i, hname) in enumerate(asymmetry_input_names):
    histogram_info = naming.extract_histogram_info(hname, has_fit_info=True)
    parameter_idx = histogram_info["Par_idx"]

    cv = create_canvas("Canvas_%s"%(hname))
    canvas_partition(cv, canvas_xbins, canvas_ybins, MARGINS)
    histograms_in_pad = create_histograms_in_this_canvas(template, cv, listed_targets)
    histograms_in_pad = fill_histograms(histograms_in_pad, asymmetry_obj, hname,
                                        inputfiles, listed_targets, single_bin=single_bin)
    axes_histogram = create_axes_histogram(asymmetry_obj, parameter_idx, single_bin)
    draw_histograms(cv, axes_histogram, asymmetry_obj, histograms_in_pad, single_bin)
    legend = draw_legend(cv, listed_targets, single_bin)
    cv.cd(0)
    draw_preliminary(asymmetry_obj.stage_name)
    draw_targetinfo(targets_info["Legend"], "Data")

    cv.SaveAs(asymmetry_obj.get_summary_plots(histogram_info["Fit_info"],
                                              histogram_info["Reco_method"], single_bin))
    cv.Clear()
    axes_histogram.Delete()

info_msg("Summary", "Asymmetry summary plots drawn!\n")
if (targets_set == "L"): # Omit ratio for liquid targets
    for file in inputfiles: # Close input files
        file.Close()
    exit()

# Ratio section
ratio_obj = naming.summary_format("Ratio", dataset, binvars, targets_set,
                                      cuts=options.cuts, run_local=run_local,
                                      fit_method=fit_method)

liquid_targets_info = targets_set_info["L"]
list_of_liquid_targets = liquid_targets_info["List"]
liquid_inputfiles = []
for (i, target) in enumerate(list_of_liquid_targets): # Open input files
    idataset = "%s_%s"%(target, dataset)
    in_obj = naming.analysis_format("Parameters", idataset, binvars, cuts=options.cuts,
                                    run_local=run_local, fit_method=fit_method)
    inputfile = TFile(in_obj.get_file_root_files(), "READ")
    liquid_inputfiles.append(inputfile)

for (i, hname) in enumerate(asymmetry_input_names):
    histogram_info = naming.extract_histogram_info(hname, has_fit_info=True)
    parameter_idx = histogram_info["Par_idx"]

    cv = create_canvas("CanvasRatio_%s"%(hname))
    canvas_partition(cv, canvas_xbins, canvas_ybins, MARGINS)
    histograms_in_pad = create_histograms_in_this_canvas(template, cv, listed_targets)
    histograms_in_pad = fill_histograms(histograms_in_pad, ratio_obj, hname,
                                        inputfiles, listed_targets, single_bin=single_bin,
                                        liquid_inputfiles=liquid_inputfiles)
    axes_histogram = create_axes_histogram(ratio_obj, parameter_idx, single_bin)
    draw_histograms(cv, axes_histogram, ratio_obj, histograms_in_pad, single_bin)
    legend = draw_legend(cv, listed_targets, single_bin)
    cv.cd(0)
    draw_preliminary(ratio_obj.stage_name)
    draw_targetinfo(targets_info["Legend"], "Data")

    cv.SaveAs(ratio_obj.get_summary_plots(histogram_info["Fit_info"],
                                          histogram_info["Reco_method"], single_bin))
    cv.Clear()
    axes_histogram.Delete()

for file in inputfiles: # Close input files
    file.Close()
info_msg("Summary", "Ratio summary plots drawn!\n")
