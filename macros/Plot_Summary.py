from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,\
    TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,\
    kBlack,kWhite,TH1
import ROOT
import os
import optparse
import copy
import myStyle as ms
import myNameFormat as nf
import mySumFunctions as sf
from array import array

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
ms.force_style()
# font=ms.get_font()
tsize = ms.get_size()
mg = ms.get_margin()

def propagate_error_division(v1, e1, v2, e2, cov = 0):
# Propagate error using proper formula with covariance included
    r1 = e1/v1
    r2 = e2/v2
    error_value = TMath.Abs(v1/v2)*TMath.Sqrt(r1*r1 + r2*r2 - 2*cov/(v1*v2))

    return error_value


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
parser.add_option('-b', dest='nonIntegratedVars', default = "",
                  help="Add non-integratedd bins like in QNZ")
parser.add_option('-i', dest='inputCuts', default = "",
                  help="Add input cuts Xf_Yb_Z/P...")
parser.add_option('-o', dest='outputCuts', default = "",
                  help="Add output cuts FE_...")

# parser.add_option('-y', dest='y_symmetric', action='store_true', default = False,
#                   help="Use symmetric y-limits (default False)")
# parser.add_option('-s', dest='solidTargets', action='store_true', default = False,
#                   help="Draw only solid targets (default adds D)")
# parser.add_option('-a', dest='allDSplit', action='store_true', default = False,
#                   help="Draw only deuterium for different solid targets")
# parser.add_option('-t', dest='type', default = "parameters",
#                   help="Choose parameter type: Pars, Norm, Ratio")
parser.add_option('-r', dest='ratio', action='store_true', default = False,
            help="Show ratio solid/deuterium. Default: individual asymmetry")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")
parser.add_option('-s', '--single_bin', dest='single_bin', default = "",
                  help="Draw only one single bin (Format Q0N0)")

options, args = parser.parse_args()

dataset = options.Dataset
isJLab = options.isJLab
ovr = options.Overwrite

single_bin = options.single_bin
bin_set = options.nonIntegratedVars
input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts
if bin_set:
    input_cuts+= "_b%s"%bin_set
    plots_cuts+= "_b%s"%bin_set
is_ratio = options.ratio

# Get dataset info
fit_method = ms.get_fit_method(input_cuts)
dataset_info = ms.get_name_dict(dataset)
nbin_dataset = dataset_info["nBin"]
list_targets = ms.get_list_summary_targets(plots_cuts)

# Differentiate solid from liquid set
is_solid_set = ms.cut_is_included("sl", plots_cuts)
legend_title_set = ms.get_list_summary_targets(plots_cuts, get_legend=True)

# Differentiate asymmetry from ratio
output_name = "Asymmetry" if not is_ratio else "Ratio"
top_msg = "Asymmetry parameter" if not is_ratio else "Ratio solid-deuterium"

if is_ratio:
    # Send error if trying to plot ratio with Deuterium
    if (not is_solid_set):
        err_txt = "Ratio doesn't make sense with D. Skipping!"
        ms.error_msg("Summary_ratio", err_txt)
    # Remove solid info for ratio (redundant)
    if ms.cut_is_included("sl", plots_cuts):
        input_cuts = input_cuts.replace("sl", "")
        plots_cuts = plots_cuts.replace("sl", "")

_, dict_nbins, dict_limits = ms.get_bincode_info(nbin_dataset, input_cuts)
vars_VS_x_format = ms.get_non_integrated_vars(input_cuts, versus_x_format=True)

# Define inputs in a list
list_inputfile = []
list_inputfile_D = []
for i,target in enumerate(list_targets):
    dataset_tmp = "%s_%s"%(target, dataset)
    in_obj = nf.naming_format("Parameters", dataset_tmp, cuts=input_cuts,
                          is_JLab=isJLab)
    inputfile = TFile(in_obj.get_path(),"READ")

    # Extract saved histogram names to use later
    if i is 0:
        list_hnames = []
        for key in inputfile.GetListOfKeys():
            if "TH1" not in key.ReadObj().Class_Name():
                continue
            key_name = key.GetName()
            # Skip "bare" parameters
            if "Parameter" in key_name:
                continue
            list_hnames.append(key_name)
    list_inputfile.append(inputfile)

    # Fill input with Deuterium info to get ratios
    if is_ratio:
        dataset_tmp = "D%s_%s"%(target, dataset)
        in_obj = nf.naming_format("Parameters", dataset_tmp, cuts=input_cuts,
                            is_JLab=isJLab)
        inputfile = TFile(in_obj.get_path(),"READ")
        list_inputfile_D.append(inputfile)

out_obj = nf.naming_format(output_name, dataset, cuts=plots_cuts,
                           is_JLab=isJLab)

# Create template histogram with correct x-axis
x_axis_var = ms.get_xaxis(input_cuts)
x_axis_title = ms.axis_label(x_axis_var, "LatexUnit")
x_axis_nbins = dict_nbins[x_axis_var]
x_axis_limits = dict_limits[x_axis_var]
haxis_title = ";%s;"%x_axis_title
htemplate = TH1D("htemplate", haxis_title, x_axis_nbins, array('d',x_axis_limits))
y_axis_limits = [[0.0, 2.0], [-0.599,0.099], [-0.299,0.099], [-0.599,0.599]]
if is_ratio:
    y_axis_limits = [[0.0, 2.0], [0.201,1.799], [0.001,1.999], [0.001,1.999]]

# Define number of pads and their coordinates (format QvNxZ)
vars_VS = vars_VS_x_format[:-2]
var_padx = vars_VS[0]
var_pady = vars_VS[-1] if len(vars_VS) > 1 else ""
npx = dict_nbins[vars_VS[0]]
npy = dict_nbins[vars_VS[-1]] if len(vars_VS) > 1 else 1
if single_bin:
    npx, npy = 1, 1

# Draw and save full canvas for each of the histograms with the parameters info
for name_idx, hname in enumerate(list_hnames):
    # Create canvas of NxN
    cv = ms.create_canvas("Pad%i"%name_idx)
    sf.canvas_partition(cv, npx, npy, extra_name="Pad")

    # Access to pads and create list
    pads = [pad for pad in cv.GetListOfPrimitives() if isinstance(pad, ROOT.TPad)]

    # Save histograms to be drawn in each pad, using key of the pad position
    all_histograms = {}
    for pad in pads:
        pad_name = pad.GetName()
        list_histogram_per_target = []
        for i,target in enumerate(list_targets):
            hist_name = pad_name.replace("Pad", "%st%i"%(hname, i))
            hist_cloned = htemplate.Clone(hist_name)
            # Define style of the cloned histogram!
            color_targ = ms.color_target[target]
            line_width = 2 if not single_bin else 4
            hist_cloned.SetLineWidth(line_width)
            hist_cloned.SetLineColor(color_targ)
            hist_cloned.SetMarkerStyle(4)
            marker_size = 1 if not single_bin else 2
            hist_cloned.SetMarkerSize(marker_size)
            hist_cloned.SetMarkerColor(color_targ)
            list_histogram_per_target.append(hist_cloned)
        (x, y) = sf.get_pad_coord(pad_name)
        all_histograms[(x, y)] = list_histogram_per_target

    # Loop over targets to fill histograms
    for i,target in enumerate(list_targets):
        # Get histogram with parameter/asymmetry info
        hparameters = list_inputfile[i].Get(hname)
        hpars_nbins = hparameters.GetXaxis().GetNbins()
        # Run over parameter values
        for b in range(1, hpars_nbins + 1):
            bincode = hparameters.GetXaxis().GetBinLabel(b)
            # Get indices of the pad to fill given a bincode
            idx_x = ms.get_bincode_varidx(bincode, var_padx)
            idx_y = ms.get_bincode_varidx(bincode, var_pady) if var_pady else 0
            # Check we take only the required bincode if ploting one bin only
            if single_bin:
                # Skip if X-AXIS is not correct
                sidx_x = ms.get_bincode_varidx(single_bin, var_padx)
                if "%s%i"%(var_padx, sidx_x) not in bincode:
                    continue
                if var_pady:
                    # Skip if Y-AXIS is not correct, if existing
                    sidx_y = ms.get_bincode_varidx(single_bin, var_pady)
                    if "%s%i"%(var_pady, sidx_y) not in bincode:
                        continue
                idx_x, idx_y = 0, 0

            # Retrieve histogram and bin to fill
            histogram_to_fill = all_histograms[(idx_x, idx_y)][i]
            bin_to_fill = ms.get_bincode_varidx(bincode, x_axis_var) + 1

            # Retrieve values
            value = hparameters.GetBinContent(b)
            error = hparameters.GetBinError(b)
            if is_ratio:
                hparameters_D = list_inputfile_D[i].Get(hname)
                b_D = hparameters_D.GetXaxis().FindBin(bincode)
                value_D = hparameters_D.GetBinContent(b_D)
                error_D = hparameters_D.GetBinError(b_D)
                # Get ratio values!
                value_ratio = value / value_D
                error_ratio = propagate_error_division(value, error, value_D, error_D)
                # Update variable to save
                value = value_ratio
                error = error_ratio
            # Fill histogram!
            histogram_to_fill.SetBinContent(bin_to_fill, value)
            histogram_to_fill.SetBinError(bin_to_fill, error)

    # Define axis histogram
    idx_parameter = nf.get_hist_hnpar(hname)
    xmin = (x_axis_limits[0] + x_axis_limits[1])/2. - 0.05
    xmax = (x_axis_limits[-2] + x_axis_limits[-1])/2. + 0.05
    haxis = TH1D("haxis", haxis_title, 1, xmin, xmax)
    #     # Limits for Zh
    #     type_norm_Z = {"0": [0.0, 2.0], "1": [-0.599,0.099],
    #                  "2": [-0.299,0.099], "3": [-0.599,0.599]}
    #     type_ratio_Z = {"0": [0.0, 2.0], "1": [0.201,1.799],
    #                  "2": [0.001,1.999], "3": [0.001,1.999]}
    #     # Limits for Pt
    #     type_norm_P = {"0": [0.0, 2.0], "1": [-0.299,0.049],
    #                  "2": [-0.049,0.099], "3": [-0.599,0.599]}
    #     type_ratio_P = {"0": [0.0, 2.0], "1": [0.301, 1.299],
    #                  "2": [0.001,1.999], "3": [0.001,1.999]}
    ymin, ymax = y_axis_limits[int(idx_parameter)]
    haxis.SetMinimum(ymin)
    haxis.SetMaximum(ymax)
    label_size = (tsize - 20) if not single_bin else (tsize - 9)
    title_size = (tsize - 16) if not single_bin else (tsize - 3)
    y_offset = 1.8 if not single_bin else 1.2
    haxis.SetLabelSize(label_size, "xy")
    haxis.SetTitleSize(title_size, "xy")
    haxis.SetTitleOffset(1.0, "x")
    haxis.SetTitleOffset(y_offset, "y")
    ytitle = sf.get_yaxis_label(idx_parameter, output_name, is_solid_set)
    haxis.GetYaxis().SetTitle(ytitle)

    # Now that we get all histograms filled for all targets, let's draw them
    for i, pad in enumerate(pads):
        pad.cd(0)
        pad.SetGrid(0,1)
        pad_name = pad.GetName()
        x, y = sf.get_pad_coord(pad_name)
        # Draw axes!
        haxis.Draw("AXIS")
        gPad.RedrawAxis("g")
        # Draw reference line for ratio
        if is_ratio:
            ref_line = ROOT.TLine(0.0, 1.0, 1.0, 1.0)
            ref_line.SetLineColorAlpha(ROOT.kRed, 0.5)
            ref_line.SetLineWidth(1)
            ref_line.SetLineStyle(9)
            xmin = haxis.GetXaxis().GetXmin()
            xmax = haxis.GetXaxis().GetXmax()
            ref_line.DrawLine(xmin, 1.0, xmax, 1.0)

        # Draw parameters/asymmetry histograms
        list_histogram_per_target = all_histograms[(x, y)]
        for j, target in enumerate(list_targets):
            histogram = list_histogram_per_target[j]
            histogram.Draw("hist L X0 SAME")
            # Add correct error bars
            histogram.Draw("e X0 SAME")

        # Draw VS bin info
        if single_bin:
            ms.draw_bininfo(single_bin, nbin_dataset, yT=0.95)
        else:
            bin_info = ROOT.TLatex()
            info_size = (tsize - 14)
            bin_info.SetTextSize(info_size)
            bin_info.SetTextAlign(23)
            # X direction
            is_bot_row = (y is 0)
            if is_bot_row:
                bincode_X = "%s%i"%(var_padx, x)
                bin_infoX = ms.get_bincode_explicit_range(bincode_X, nbin_dataset)
                y_pc =-0.20
                bin_info.DrawLatexNDC(sf.x_pad(0.50), sf.y_pad(y_pc), bin_infoX)
            # Y direction
            is_right_col = (x is (npx - 1))
            if is_right_col and var_pady:
                bin_info.SetTextAngle(90)
                bincode_Y = "%s%i"%(var_pady, y)
                bin_infoY = ms.get_bincode_explicit_range(bincode_Y, nbin_dataset)
                x_pc = 1.05
                bin_info.DrawLatexNDC(sf.x_pad(x_pc),sf.y_pad(0.50), bin_infoY)

        # Run at the end only
        if i is (len(pads) - 1):
            coord = "%i_%i"%(x, y)

            # Create and draw legend
            px_legend = (npx - 1) if not single_bin else 0
            py_legend = 0
            coord_legend = "%i_%i"%(px_legend, py_legend)
            pad_legend_name = pad_name.replace(coord, coord_legend)
            pad_legend = gROOT.FindObject(pad_legend_name)
            pad_legend.cd(0)
            # TODO: Add specific position for certain plots
            # x1, x2 = sf.x_pad(0.1), sf.x_pad(0.9)
            # y1, y2 = sf.y_pad(0.8), sf.y_pad(1.0)
            # if not def_position:
            #     x1, x2 = sf.x_pad(0.1), sf.x_pad(0.9)
            #     y1, y2 = sf.y_pad(0.7), sf.y_pad(0.9)
            # if one_bin:
            #     x1, x2 = sf.x_pad(0.1), sf.x_pad(0.9)
            #     y1, y2 = sf.y_pad(0.01), sf.y_pad(0.21)
            x1, x2 = sf.x_pad(0.1), sf.x_pad(0.9)
            y1, y2 = sf.y_pad(0.8), sf.y_pad(1.0)
            if single_bin:
                x1, x2 = sf.x_pad(0.1), sf.x_pad(0.9)
                y1, y2 = sf.y_pad(0.01), sf.y_pad(0.21)
            legend = TLegend(x1, y1, x2, y2)
            legend.SetBorderSize(0)
            legend.SetTextFont(ms.get_font())
            legend.SetTextSize(title_size)
            legend.SetFillStyle(0)
            legend.SetTextAlign(22)
            legend.SetNColumns(3)
            for j, target in enumerate(list_targets):
                histogram = list_histogram_per_target[j]
                legend.AddEntry(histogram, target)
            legend.Draw()

    # Draw final messages in canvas
    cv.cd(0)
    # Define canvas style
    ms.draw_summary(top_msg)
    ms.draw_preliminary()
    ms.draw_targetinfo(legend_title_set, "Data")

    new_name = nf.get_hist_hfullname(hname).replace("Asymmetry", output_name)
    out_obj.updt_name(new_name)
    out_obj.updt_acc_method(nf.get_hist_hmeth(hname))
    out_obj.updt_bin_code("")
    if single_bin:
        out_obj.updt_bin_code(single_bin)
    out_obj.updt_extension("png")

    cv.SaveAs(out_obj.get_path_summary(create=True, overwrite=True))
    # out_obj.get_file_name_summary()

    # Avoid memory leak warning
    haxis.Delete()
    legend.Delete()

# Close input files
for file in list_inputfile:
    file.Close()
ms.info_msg("Summary", "Summary plots drawn!\n")
