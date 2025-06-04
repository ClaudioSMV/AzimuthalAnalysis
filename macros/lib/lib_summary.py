from lib_cuts import create_dictionary_binvars
from lib_constants import SIZE_TEXT, OFFSET_TITLE, FONT, summary_y_limits
from lib_cuts import create_bincode, extract_indices_dict
from lib_style import axes_title, draw_bininfo, target_color
from lib_error import info_msg, error_msg
from lib_parameters import propagate_error_division
from ROOT import gROOT, TPad, gPad, TH1D, TLine, kRed, TLegend
import ctypes # Needed to get pointer values
from array import array


def summary_yaxis_label(parameter_idx, targets_set, is_ratio = False):
# Create label for the observable under test
    fit_parameter_symbol = {"0": "1", "1": "cos#phi", "2": "cos2#phi", "3": "sin#phi"}
    targets_set = "A" if (targets_set == "S") else "D"
    axis_label = "#LT%s#GT_{e%s}"%(fit_parameter_symbol[parameter_idx], targets_set)
    if is_ratio:
        axis_label += "/#LT%s#GT_{eD}"%(fit_parameter_symbol[parameter_idx])

    return axis_label

def extract_binvars_axes(formatted_binvars):
# Create dictionary with variable of the pad x-axis and canvas x/y axes
    idx_xvar = formatted_binvars.index("x") + 1
    info = {"pad_x_axis": formatted_binvars[idx_xvar]}
    if ("v" in formatted_binvars): # Pads in two dimensions
        idx_reference = formatted_binvars.index("v")
        info["canvas_x_axis"] = formatted_binvars[idx_reference - 1]
        info["canvas_y_axis"] = formatted_binvars[idx_reference + 1]
    else: # Pads in one dimension only
        info["canvas_x_axis"] = formatted_binvars[idx_xvar - 2]

    return info

def get_number_of_pads(summary_object, single_bin = False):
    if single_bin:
        return 1, 1
    binvars_axes = extract_binvars_axes(summary_object.binvars_format)
    binvars_info = create_dictionary_binvars(summary_object.n_bin, summary_object.binvars)
    canvas_xbins = binvars_info[binvars_axes["canvas_x_axis"]]["Nbins"]
    canvas_ybins = 1
    if "canvas_y_axis" in binvars_axes:
        canvas_ybins = binvars_info[binvars_axes["canvas_y_axis"]]["Nbins"]

    return canvas_xbins, canvas_ybins

def create_summary_histogram(summary_object, single_bin = False):
    # axes = axes_title(x_variable, y_title, x_is_variable=True)
    x_variable = extract_binvars_axes(summary_object.binvars_format)["pad_x_axis"]
    var_info = create_dictionary_binvars(summary_object.n_bin, x_variable)[x_variable]
    line_width = 2 if not single_bin else 4
    marker_size = 1 if not single_bin else 2
    histogram = TH1D("template", "", var_info["Nbins"], array('d', var_info["Limits"]))
    histogram.SetLineWidth(line_width)
    histogram.SetMarkerStyle(4)
    histogram.SetMarkerSize(marker_size)

    return histogram

def create_histograms_in_this_canvas(template_histogram, canvas, list_of_targets):
    pads = [pad for pad in canvas.GetListOfPrimitives() if isinstance(pad, TPad)]
    histograms_in_this_canvas = {}
    for pad in pads:
        (x, y) = get_pad_indices(pad.GetName())
        histograms_in_this_canvas[(x, y)] = []
        for target in list_of_targets:
            hist_name = "%s_%i_%i_%s"%(canvas.GetName(), x, y, target)
            histogram = template_histogram.Clone(hist_name)
            color = target_color[target]
            histogram.SetLineColor(color)
            histogram.SetMarkerColor(color)
            histograms_in_this_canvas[(x, y)].append(histogram)

    return histograms_in_this_canvas


                                 #######################
###################################      Summary      ####################################
###################################  Fill histograms  ####################################
                                 #######################

def fill_histograms(histograms_in_this_canvas, summary_object, hname, inputfiles,
                    targets_list, liquid_inputfiles = [], single_bin = False):
    binvars_axes = extract_binvars_axes(summary_object.binvars_format)
    variable_x = binvars_axes["canvas_x_axis"]
    variable_y = binvars_axes["canvas_y_axis"] if "canvas_y_axis" in binvars_axes else ""
    for (pair, histograms_per_target) in histograms_in_this_canvas.items():
        cx, cy = pair
        if single_bin: # In this case, pad location is not the bin of interest
            bin_indices = extract_indices_dict(single_bin)
            cx = bin_indices[variable_x]
            cy = bin_indices[variable_y] if variable_y else 1
        indices = {variable_x: cx, variable_y: cy}
        for (i, target) in enumerate(targets_list):
            histogram_to_fill = histograms_per_target[i]
            input_histogram = inputfiles[i].Get(hname)
            input_liquid = liquid_inputfiles[i].Get(hname) if liquid_inputfiles else ""
            for bin in range(1, histogram_to_fill.GetXaxis().GetNbins() + 1):
                indices[binvars_axes["pad_x_axis"]] = bin - 1
                bincode = create_bincode(indices)
                value, error = extract_value(input_histogram, bincode, input_liquid)

                histogram_to_fill.SetBinContent(bin, value)
                histogram_to_fill.SetBinError(bin, error)

    return histograms_in_this_canvas

def extract_value(input_histogram, bincode, liquid_input_histogram):
    input_bin = input_histogram.GetXaxis().FindBin(bincode)
    value = input_histogram.GetBinContent(input_bin)
    error = input_histogram.GetBinError(input_bin)
    if liquid_input_histogram:
        liquid_bin = liquid_input_histogram.GetXaxis().FindBin(bincode)
        liq_value = liquid_input_histogram.GetBinContent(liquid_bin)
        liq_error = liquid_input_histogram.GetBinError(liquid_bin)
        error = propagate_error_division(value, error, liq_value, liq_error)
        value = value / liq_value

    return value, error

def create_axes_histogram(summary_object, parameter_idx, single_bin = False):
    binvars_axes = extract_binvars_axes(summary_object.binvars_format)
    pad_x_var = binvars_axes["pad_x_axis"]
    variable_info = create_dictionary_binvars(summary_object.n_bin, pad_x_var)[pad_x_var]
    limits = variable_info["Limits"]
    xmin = (limits[0] + limits[1]) / 2. - 0.05
    xmax = (limits[-2] + limits[-1]) / 2. + 0.05
    is_ratio = ("Ratio" in summary_object.stage_name)
    y_title = summary_yaxis_label(parameter_idx, summary_object.targets_set, is_ratio)
    title = axes_title(pad_x_var, y_title, x_is_variable=True)
    axes_histogram = TH1D("axes_histogram", title, 1, xmin, xmax)

    ymin, ymax = summary_y_limits[summary_object.stage_name][int(parameter_idx)]
    axes_histogram.SetMinimum(ymin)
    axes_histogram.SetMaximum(ymax)
    if not single_bin:
        axes_histogram.SetLabelSize(SIZE_TEXT - 20, "xy")
        axes_histogram.SetTitleSize(SIZE_TEXT - 16, "xy")
        axes_histogram.SetTitleOffset(1.0, "x")
        axes_histogram.SetTitleOffset(OFFSET_TITLE["Y"] + 0.6, "y")

    return axes_histogram

def draw_histograms(canvas, axes_histogram, summary_object, histograms_to_draw,
                    single_bin = False):
    nbin = summary_object.n_bin
    pads = [pad for pad in canvas.GetListOfPrimitives() if isinstance(pad, TPad)]
    for (i, pad) in enumerate(pads):
        pad.cd(0)
        pad.SetGrid(0,1)
        (x, y) = get_pad_indices(pad.GetName())
        axes_histogram.Draw("AXIS")
        gPad.RedrawAxis("g")
        is_ratio = ("Ratio" in summary_object.stage_name)
        if is_ratio: # Draw reference line for ratio only
            draw_ratio_reference_line(axes_histogram)

        histograms_per_target = histograms_to_draw[(x, y)]
        for histogram in histograms_per_target:
            histogram.Draw("hist L X0 SAME")
            histogram.Draw("e X0 SAME") # Add correct error bars

        if single_bin:
            draw_bininfo(single_bin, nbin, y_position=0.95)
            continue

        canvas_variables = extract_binvars_axes(summary_object.binvars_format)
        if (y == 0): # Draw x_var ranges below first row only
            x_var = canvas_variables["canvas_x_axis"]
            draw_canvas_x_bincode_range(x_var + str(x), nbin)
        if "canvas_y_axis" not in canvas_variables:
            continue
        if (x == find_last_column_idx(canvas)):
            y_var = canvas_variables["canvas_y_axis"]
            draw_canvas_y_bincode_range(y_var + str(y), nbin)

def draw_legend(canvas, targets_list, single_bin = False):
    px, py = find_last_column_idx(canvas), 0
    pad_legend = gROOT.FindObject("Pad_%i_%i"%(px, py))
    pad_legend.cd(0)
    primitives = pad_legend.GetListOfPrimitives()
    histograms = [obj for obj in primitives if obj.InheritsFrom("TH1")]
    x1, y1 = get_coordinates_in_pad(0.1, 0.8)
    x2, y2 = get_coordinates_in_pad(0.9, 1.0)
    if single_bin:
        x1, y1 = get_coordinates_in_pad(0.1, 0.01)
        x2, y2 = get_coordinates_in_pad(0.9, 0.21)
    legend = TLegend(x1, y1, x2, y2)
    legend.SetBorderSize(0)
    legend.SetTextFont(FONT)
    legend.SetTextSize(SIZE_TEXT - 16)
    if single_bin:
        legend.SetTextSize(SIZE_TEXT)
    legend.SetFillStyle(0)
    legend.SetTextAlign(22)
    legend.SetNColumns(3)
    for target in targets_list:
        for histogram in histograms:
            if (target != histogram.GetName().split("_")[-1]):
                continue
            legend.AddEntry(histogram, target)
            break
    legend.Draw()

    return legend

                                 #######################
###################################      Summary      ####################################
###################################  Canvas and pads  ####################################
                                 #######################

def pad_name(title, x, y):
# Create name of the pad using its coordinate position x,y
    return "%s_%i_%i"%(title, x, y)

def get_pad_indices(name):
# Obtain pair of coordinates for the pad x,y
    elements = name.split("_")

    return int(elements[-2]), int(elements[-1])

def find_last_column_idx(canvas, initial_guess = 10):
# Look among pads already created and return idx when column exists
    primitives = [obj for obj in canvas.GetListOfPrimitives() if obj.InheritsFrom("TPad")]
    list_of_names = [pad.GetName() for pad in primitives]
    guess = initial_guess # Update if many bins are needed (10 should be enough)
    while (guess > -1):
        guess_name = pad_name("Pad", guess, 0)
        if guess_name in list_of_names:
            return guess
        guess -= 1
    error_msg("find_last_column", "Last column pad not found :(")

def canvas_partition(canvas, nx, ny, margins, extra_name = "Pad"):
# Separate canvas in nx by ny pads
    ## Labelling xy:
    ##  ------------
    ##  - 02 12 22 -
    ##  - 01 11 21 -
    ##  - 00 10 20 -
    ##  ------------
    vSpacing = 0.0
    vStep  = (1.- margins["B"] - margins["T"] - (ny-1) * vSpacing) / ny
    hSpacing = 0.0
    hStep  = (1.- margins["L"] - margins["R"] - (nx-1) * hSpacing) / nx

    for i in range(nx):
        if (i == 0):
            hposl = 0.0
            hposr = margins["L"] + hStep
            hfactor = hposr - hposl
            hmarl = margins["L"] / hfactor
            hmarr = 0.0
        elif (i == nx-1):
            hposl = hposr + hSpacing
            hposr = hposl + hStep + margins["R"]
            hfactor = hposr - hposl
            hmarl = 0.0
            hmarr = margins["R"] / (hposr-hposl)
        else:
            hposl = hposr + hSpacing
            hposr = hposl + hStep
            hfactor = hposr - hposl
            hmarl = 0.0
            hmarr = 0.0

        for j in range(ny):
            if (j==0):
                vposd = 0.0
                vposu = margins["B"] + vStep
                vfactor = vposu-vposd
                vmard = margins["B"] / vfactor
                vmaru = 0.0
            elif (j == ny-1):
                vposd = vposu + vSpacing
                vposu = vposd + vStep + margins["T"]
                vfactor = vposu - vposd
                vmard = 0.0
                vmaru = margins["T"] / (vposu-vposd)
            else:
                vposd = vposu + vSpacing
                vposu = vposd + vStep
                vfactor = vposu - vposd
                vmard = 0.0
                vmaru = 0.0
            canvas.cd(0)
            name = pad_name(extra_name, i, j)
            pad = gROOT.FindObject(name)
            if pad:
                pad.Delete()
            pad = TPad(name, "", hposl, vposd, hposr, vposu)
            pad.SetLeftMargin(hmarl)
            pad.SetRightMargin(hmarr)
            pad.SetBottomMargin(vmard)
            pad.SetTopMargin(vmaru)
            pad.SetFrameBorderMode(0)
            pad.SetBorderMode(0)
            pad.SetBorderSize(0)

            pad.Draw()

def get_coordinates_in_pad(x, y):
# Transform a coordinate pair from pad-NDC to the global/canvas-NDC
    xl, xr = ctypes.c_double(0.0), ctypes.c_double(0.0)
    yd, yu = ctypes.c_double(0.0), ctypes.c_double(0.0)
    gPad.GetPadPar(xl, yd, xr, yu)
    margin_L, margin_R = gPad.GetLeftMargin(), gPad.GetRightMargin()
    margin_B, margin_T = gPad.GetBottomMargin(), gPad.GetTopMargin()
    x = pad_coordinate_to_full_canvas(x, xr.value - xl.value, margin_L, margin_R)
    y = pad_coordinate_to_full_canvas(y, yu.value - yd.value, margin_B, margin_T)

    return (x, y)

def pad_coordinate_to_full_canvas(position, pad_width, margin1, margin2):
# Transform a position in NDC coordinate of a pad to the global-canvas NDC
    pad_width_wrt_canvas = pad_width - pad_width * margin1 - pad_width * margin2

    return (position * pad_width_wrt_canvas + margin1 * pad_width) / pad_width

                              #############################
################################          Style          #################################
################################  Lines and annotations  #################################
                              #############################

def draw_ratio_reference_line(histogram_xaxis):
    line = TLine(0.0, 1.0, 1.0, 1.0)
    line.SetLineColorAlpha(kRed, 0.5)
    line.SetLineWidth(1)
    line.SetLineStyle(9)
    xmin = histogram_xaxis.GetXaxis().GetXmin()
    xmax = histogram_xaxis.GetXaxis().GetXmax()
    line.DrawLine(xmin, 1.0, xmax, 1.0)

def draw_canvas_x_bincode_range(xvar, nbin):
    x, y = get_coordinates_in_pad(0.50, -0.20)
    draw_bininfo(xvar, nbin, x_position=x, y_position=y, reduce_text_size=12, center=True)

def draw_canvas_y_bincode_range(yvar, nbin):
    x, y = get_coordinates_in_pad(1.05, 0.50)
    draw_bininfo(yvar, nbin, x_position=x, y_position=y, angle=90, reduce_text_size=12,
                 center=True)
