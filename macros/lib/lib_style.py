from ROOT import TH1, TH1D, gROOT, gStyle, TGaxis, TCanvas, TLatex, kGray, TColor
from lib_constants import MARGINS, FONT, SIZE_TEXT, OFFSET_TITLE, update_margins, \
    update_offset, variable_info, color_palette
from lib_cuts import extract_indices_dict
# import os
from Bins_testing import List_of_binning

                               ############################
#################################         Style          #################################
#################################  Define general style  #################################
                               ############################

def force_style(use_colz = False):
# Define Style for plots with uniform margins and text format
    gROOT.SetBatch(True)
    gStyle.SetOptFit(1011)
    if use_colz: # Update values to support layout with colored z-scale
        update_margins({"T": 0.055, "R": 0.10})
        # gStyle.SetLabelSize(SIZE_TEXT - 9,"z")
        update_offset({"Y": 1.3})
    # MARGINS
    gStyle.SetPadTopMargin(MARGINS["T"])
    gStyle.SetPadRightMargin(MARGINS["R"])
    gStyle.SetPadBottomMargin(MARGINS["B"])
    gStyle.SetPadLeftMargin(MARGINS["L"])
    # TICKS IN AXES
    gStyle.SetPadTickX(1)
    gStyle.SetPadTickY(1)
    # FONT
    gStyle.SetTextFont(FONT)
    gStyle.SetLabelFont(FONT,"x")
    gStyle.SetTitleFont(FONT,"x")
    gStyle.SetLabelFont(FONT,"y")
    gStyle.SetTitleFont(FONT,"y")
    gStyle.SetLabelFont(FONT,"z")
    gStyle.SetTitleFont(FONT,"z")
    # TEXT SIZE
    gStyle.SetTextSize(SIZE_TEXT)
    gStyle.SetLabelSize(SIZE_TEXT - 9,"x")
    gStyle.SetTitleSize(SIZE_TEXT - 3,"x")
    gStyle.SetLabelSize(SIZE_TEXT - 9,"y")
    gStyle.SetTitleSize(SIZE_TEXT - 3,"y")
    gStyle.SetLabelSize(SIZE_TEXT - 9,"z")
    gStyle.SetTitleSize(SIZE_TEXT - 3,"z")
    # LEGEND
    gStyle.SetLegendFont(FONT)
    gStyle.SetLegendTextSize(SIZE_TEXT)
    gStyle.SetLegendBorderSize(0)
    gStyle.SetLegendFillColor(0)
    # TITLE OFFSET
    gStyle.SetTitleXOffset(OFFSET_TITLE["X"])
    gStyle.SetTitleYOffset(OFFSET_TITLE["Y"])
    gStyle.SetOptTitle(0)
    # gStyle.SetOptStat(0)
    gStyle.SetHistLineWidth(4)
    gStyle.SetGridColor(921)
    gStyle.SetGridStyle()
    TGaxis.SetExponentOffset(-0.07, 0.0, "y") # Move exponent in y-axis to the left
    gROOT.ForceStyle()

                                 #######################
###################################     Functions     ####################################
###################################  Canvas and pads  ####################################
                                 #######################

def get_pad_center(mleft = MARGINS["L"], mright = MARGINS["R"]):
    return 1/2. + mleft/2. - mright/2.

def create_canvas(cname = "cv", xsize = 1000, ysize = 800):
    canvas = TCanvas(cname, "cv", xsize, ysize)
    canvas.SetGrid(0,1)
    # gPad.SetTicks(1,1)
    TH1.SetDefaultSumw2()
    gStyle.SetOptStat(0)

    return canvas

                            #################################
##############################          Functions          ###############################
##############################  Annotations and comments   ###############################
                            #################################

def draw_annotation(txt_bold = "", txt = "", where = "L", xoff = 0.005, yoff = 0.01):
# Draw annotations on top of the plot
    to_draw = TLatex()
    to_draw.SetTextSize(SIZE_TEXT-4)
    if "R" in where:
        to_draw.SetTextAlign(31)
    xpoint = MARGINS["L"] + xoff if "L" in where else 1 - MARGINS["R"] - xoff
    ypoint = 1 - MARGINS["T"] + yoff
    this_text = "#bf{%s}"%(txt_bold)
    if txt:
        this_text += " %s"%(txt)
    to_draw.DrawLatexNDC(xpoint, ypoint, this_text)

def draw_preliminary(text = "", xoff = 0.005, yoff = 0.01):
# Draw watermark to show that these are preliminary results.
    preliminar_msg = TLatex()
    preliminar_msg.SetTextSize(SIZE_TEXT+10)
    preliminar_msg.SetTextAlign(22)
    preliminar_msg.SetTextAngle(45)
    preliminar_msg.SetTextColor(kGray)
    preliminar_msg.SetTextColorAlpha(kGray, 0.4)
    xcenter = get_pad_center(MARGINS["L"], MARGINS["R"])
    ycenter = get_pad_center(MARGINS["B"], MARGINS["T"])
    msg = "#bf{%s}"%("  CLAS preliminary  "*2)
    preliminar_msg.DrawLatexNDC(xcenter, ycenter, msg)
    if text:
        draw_annotation(text, where="L", xoff=xoff, yoff=yoff)

def draw_summary(text = "", xoff = 0.005, yoff = 0.01):
# Draw top left annotation indicating "Summary"
    # draw_annotation(text, "Summary", where="L", xoff=xoff, yoff=yoff)
    draw_annotation(text, where="L", xoff=xoff, yoff=yoff)

def draw_targetinfo(text, is_data, show_set_type = False):
# Draw top right label with target and "simulation" or "data" info
    set_type = "Data" if is_data else "Simulation"
    if text in target_color.keys(): # Insert word "target" to be more clear
        text += " target"
    if show_set_type:
        text += ", %s"%(set_type)
    draw_annotation(text, where="R")

def draw_bininfo(bincode, nbin, x_position = 0, y_position = 0, use_units = False,
                 angle = 0, reduce_text_size = 0, center = 0):
# Draw bin info such as: "0.1 GeV < nu < 1.0 GeV"
    txt = TLatex()
    txt.SetTextSize(SIZE_TEXT - 4 - reduce_text_size)
    bin_range = get_bincode_explicit_range(bincode, nbin, use_units)
    align = 23 if not x_position else 33 # x_position: top-right; center if None
    if center:
        align = 23
    txt.SetTextAlign(align)
    txt.SetTextAngle(angle)
    x_point = get_pad_center() if not x_position else x_position
    y_point = 1 - MARGINS["T"] - 0.02 if not y_position else y_position

    txt.DrawLatexNDC(x_point, y_point, bin_range)

def get_bincode_explicit_range(bincode, nbin, use_units = False):
# Return text with variable and limits. Ex.: "N0" -> "0.1 GeV < nu < 1.0 GeV"
    dictionary_limits = list(List_of_binning)[nbin]
    list_ranges = []
    dictionary_indices = extract_indices_dict(bincode)
    for char in bincode:
        if char.isdigit():
            continue
        latex_var = axis_label(char, "L")
        var = variable_info[char][0]
        idx = dictionary_indices[char]
        min = "%.2f"%(dictionary_limits[var][idx])
        max = "%.2f"%(dictionary_limits[var][idx + 1])
        if use_units:
            unit = axis_label(char, "U")
            min += " %s"%(unit)
            max += " %s"%(unit)
        txt = "%s #leq %s < %s"%(min, latex_var, max)
        list_ranges.append(txt)

    return "; ".join(list_ranges) if len(list_ranges) > 1 else list_ranges[0]

                                ##########################
##################################      Functions       ##################################
##################################  Markers and colors  ##################################
                                ##########################

def rgb_to_root(rgb_tuple):
# Translate color from RGB format to inner ROOT format
    R, G, B = rgb_tuple

    return TColor.GetColor(R, G, B)

def get_marker(filled = False):
# List with markers: [circle, square, triangle, diamond, star-inverse, inverse-triangle]
    marker_hollow = [24, 25, 26, 27, 30, 32]
    marker_filled = [20, 21, 22, 33, 29, 23]

    return marker_hollow if not filled else marker_filled

def get_color_palette(only_this_color = ""):
# Get color palette or a single color with the ROOT required format
    if only_this_color:
        return rgb_to_root(color_palette[only_this_color])

    return {name: rgb_to_root(rgb) for (name, rgb) in color_palette.items()}

target_color = {
    'C': get_color_palette("blue"),
    'Fe': get_color_palette("green"),
    'Pb': get_color_palette("mustard"),
    'D': get_color_palette("light_red"),
    'DC': get_color_palette("light_blue"),
    'DFe': get_color_palette("wine"),
    'DPb': get_color_palette("gray"),
}

                                   ###################
#####################################   Functions   ######################################
#####################################  Axes labels  ######################################
                                   ###################

def axis_label(var, options = "LU"):
# Return label of a variable. Good looking axes need "LU" (Latex + Units)!
    label = []
    if ("L" in options): # Use Latex form
        label.append(variable_info[var][1])
    if ("U" in options): # Show units
        label.append(variable_info[var][2])
    if not label: # Use plain name
        label = [variable_info[var][0]]

    return " ".join(label) if len(label) > 0 else label[0]

def axes_title(xname, yname, zname = "", x_is_variable = False, y_is_variable = False,
               z_is_variable = False, pad_title = ""):
    xtitle = xname if not x_is_variable else axis_label(xname)
    ytitle = yname if not y_is_variable else axis_label(yname)
    ztitle = zname if not z_is_variable else axis_label(zname)
    root_style = "%s;%s;%s"%(pad_title, xtitle, ytitle)
    if ztitle:
        root_style += ";%s"%(ztitle)

    return root_style
