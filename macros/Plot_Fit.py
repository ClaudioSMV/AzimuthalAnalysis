import sys; sys.path.append('lib')
from ROOT import TFile,gStyle
import optparse
from lib_style import force_style,create_canvas,draw_preliminary,draw_targetinfo,\
    get_color_palette,draw_bininfo
from lib_cuts import check_cut_is_included
from lib_fit import check_fit_feasibility,get_fit_function,matrix_name,print_fit_info,\
    adapt_histogram_to_fit
from lib_dataset_info import convert_info_tag_str_to_list
from lib_histograms import get_input_histograms
from lib_error import info_msg
from lib_constants import available_fit_methods
import lib_naming as naming

force_style() # Defining Style
gStyle.SetOptFit(1)

fit_colors = [get_color_palette("wine"), get_color_palette("light_blue")]

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <targ>_<binType>_<Ndims>")
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

input_shift = (fit_method == "Sh")
in_obj = naming.analysis_format("Correction", dataset, binvars, cuts=options.cuts,
                                 run_local=run_local, fit_method="Sh"*input_shift)
inputfile = TFile(in_obj.get_file_root_files(), "READ")

out_obj = naming.analysis_format("Fit", dataset, binvars, cuts=options.cuts,
                                 run_local=run_local, fit_method=fit_method)
outputfile_name = out_obj.get_file_root_files(options.Overwrite, True, True)

use_sin, normalize, skip_peak = check_cut_is_included(["Fs", "Nm", "NP"], options.cuts)

# Create canvas
canvas = create_canvas()
outputfile = TFile(outputfile_name, "RECREATE")
target, nbin, _ = convert_info_tag_str_to_list(dataset)
for (hname, histogram) in get_input_histograms(inputfile).items():
    if "raw" in hname.lower(): # Fit corrected histograms only
        continue
    if not check_fit_feasibility(histogram, fit_method, use_sin): # Fit can be done
        continue

    if normalize: # Normalize distribution before performing fit
        histogram.Scale(1.0 / histogram.Integral("width"))

    info = naming.extract_histogram_info(hname)
    reco_method, bincode = info["Reco_method"], info["Bincode"]
    new_name = out_obj.get_name_histogram(reco_method, bincode)
    histogram_to_fit = adapt_histogram_to_fit(histogram, fit_method, new_name)
    histogram_to_fit.Draw("hist axis")
    location_of_fits = available_fit_methods[fit_method]["Sides"]

    for (i, side) in enumerate(location_of_fits):
        fit_name = "fit%i"%(i)
        fit = get_fit_function(histogram_to_fit, fit_name, fit_method, side,
                               use_sin=use_sin, skip_peak=skip_peak)
        color = fit_colors[i]
        fit.SetLineColor(color)
        opts = "MSRQ"
        if (i > 0):
            opts += "+"

        fit_matrix = histogram_to_fit.Fit(fit_name, opts, "")
        histogram_to_fit.SetStats(False)
        print_fit_info(fit, side, color)

        # Save matrices in output
        fit_matrix.GetCovarianceMatrix().Write(matrix_name("Cov", info["NoName"], i))
        fit_matrix.GetCorrelationMatrix().Write(matrix_name("Corr", info["NoName"], i))

    # Draw and save
    histogram_to_fit.Draw("FUNC same")
    histogram_to_fit.Write()

    # Draw annotations
    draw_preliminary("Correction fit")
    # draw_targetinfo("%s_%i"%(target, nbin), "Data")
    draw_targetinfo(target, "Data")
    draw_bininfo(bincode, nbin=nbin)

    canvas.SaveAs(out_obj.get_file_plots(reco_method, bincode))
    canvas.Clear()

info_msg("Fit", "Fit parameters saved!\n")
outputfile.Close()
