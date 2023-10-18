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
tsize=ms.get_size()


def get_required_ffit(cuts):
    r_ffit = "0"
    if "Left" in cuts:
        r_ffit = "1"

    return r_ffit

def get_input_info(l_keys):
# Retrieve fit information from list of keys, returning a tuple with:
# list of names, list fit parameters, list correction methods
    l_kname = []
    s_npar = set()
    s_meth = set()

    for key in l_keys:
        obj_type = key.ReadObj().Class_Name()
        kname = key.GetName()
        if "TH1D" not in obj_type:
            continue

        l_kname.append(kname)
        s_npar.add(nf.get_hist_hnpar(kname))
        s_meth.add(nf.get_hist_hmeth(kname))

    return (l_kname, list(s_npar), list(s_meth))

def draw_axes(canvas, href, targ):
# ["par", "norm", "ratio"]
    npar = nf.get_hist_hnpar(canvas.GetName())

    # Define y limits
    y_limit = sf.get_parameters_limits(d_tp_bool, npar, my_xvar_init)
    ymin, ymax = y_limit

    # Create histogram with correct axes
    b1 = href.GetBinCenter(1)
    bN = href.GetBinCenter(href.GetXaxis().GetNbins())
    xtitle = href.GetXaxis().GetTitle()
    ytitle = sf.yaxis_label(npar, my_tp_nameS, targ)
    htitle = ";%s;%s"%(xtitle, ytitle)
    haxis = TH1D("haxis", htitle, 1, b1-0.05, bN+0.05)

    haxis.SetMinimum(ymin)
    haxis.SetMaximum(ymax)
    haxis.SetLabelSize(tsize-20,"xy")
    haxis.SetTitleSize(tsize-16,"xy")
    haxis.SetTitleOffset(1.0,"x")
    haxis.SetTitleOffset(1.8,"y")

    canvas.cd(0)
    # Get the list of primitives drawn in the canvas
    primitives = canvas.GetListOfPrimitives()

    # Loop over the list to retrieve the pads
    pads = []
    for primitive in primitives:
        if isinstance(primitive, ROOT.TPad):
            pads.append(primitive)

    # Define figures to add in every pad
    for pad in pads:
        pad.cd(0)
        # Draw axes
        haxis.Draw("AXIS")
        gPad.RedrawAxis("g")

        # Draw explicit x and y bin range
        px, py = sf.get_pad_coord(pad.GetName())
        axis_txt = draw_bin_aside(px, py)

        # Draw reference line at 1 for ratio
        if d_tp_bool["ratio"]:
            line = draw_line(haxis)
    
    return haxis

def create_d_th1(hvalues, href, l_bincodes, padx_var, pady_var, xaxis_var):
# Create dictionary with pad indices associated to histogram
# as in: {(x,y) : hist}
    d_pad = {}
    kname, targ = hvalues.GetName().split("-")
    for bincode in l_bincodes:
        # Get pad indices
        idx_x = ms.get_bincode_varidx(bincode, padx_var)
        idx_y = ms.get_bincode_varidx(bincode, pady_var)
        pcoord = (idx_x, idx_y)
        if pcoord not in d_pad:
            # Uses same name as pad
            new_name = sf.pad_name(kname, idx_x, idx_y)
            new_name+= "-%s"%(targ)
            htemp = href.Clone(new_name)
            d_pad[pcoord] = htemp
        # Retrieve values from input
        hvalues_bin = hvalues.GetXaxis().FindBin(bincode)
        value = hvalues.GetBinContent(hvalues_bin)
        error = hvalues.GetBinError(hvalues_bin)
        # Fill pad histogram
        hbin = ms.get_bincode_varbin(bincode, xaxis_var)
        this_hist = d_pad[pcoord]
        this_hist.SetBinContent(hbin, value)
        this_hist.SetBinError(hbin, error)

    return d_pad

def fill_canvas(canvas, dict_th1):
# Draw each histogram in its respective pad with proper color
    l_hist = []
    canvas.cd(0)
    for px,py in dict_th1:
        hist = dict_th1[(px,py)]
        pname, targ = hist.GetName().split("-")
        pad = gROOT.FindObject(pname)
        pad.cd(0)
        pad.SetGrid(0,1) # Is it needed?

        # Choose style
        # hist.SetLabelSize(tsize-20,"xy")
        # hist.SetTitleSize(tsize-16,"xy")
        # hist.SetTitleOffset(1.0,"x")
        # hist.SetTitleOffset(1.8,"y")
        hist.SetLineWidth(2)
        hist.SetLineColor(ms.color_target[targ])
        hist.SetMarkerStyle(4)
        hist.SetMarkerColor(ms.color_target[targ])

        # gPad.RedrawAxis("g")
        hist.Draw("hist L X0 SAME")
        # Draw error bars too
        hist.Draw("e X0 SAME")

        l_hist.append(hist)
    
    return l_hist

def create_legend(kname, def_position = True):
    plx, ply = 2, 0
    pad_name = sf.pad_name(kname, plx, ply)
    pad = gROOT.FindObject(pad_name)
    pad.cd(0)
    x1, x2 = sf.x_pad(0.1), sf.x_pad(0.9)
    y1, y2 = sf.y_pad(0.8), sf.y_pad(1.0)
    if not def_position:
        x1, x2 = sf.x_pad(0.1), sf.x_pad(0.9)
        y1, y2 = sf.y_pad(0.7), sf.y_pad(0.9)

    legend = TLegend(x1, y1, x2, y2)
    legend.SetBorderSize(0)
    legend.SetTextFont(ms.get_font())
    legend.SetTextSize(tsize-14)
    legend.SetFillStyle(0)
    legend.SetTextAlign(22)
    legend.SetNColumns(3)

    # Get the list of primitives in the pad
    primitives = pad.GetListOfPrimitives()
    # Filter and extract the histograms from the list
    histograms = {}
    for obj in primitives:
        if isinstance(obj, ROOT.TH1) and ("haxis" not in obj.GetName()):
            _, targ = obj.GetName().split("-")
            if targ in histograms:
                continue
            histograms[targ] = obj
    # Print the list of histograms
    for targ in l_tar_input:
        hist = histograms[targ]
        legend.AddEntry(hist, targ)
    
    legend.Draw()

    return legend

# Define extra stylistic functions
def draw_bin_aside(x, y):
# Check if x,y correspond to one of the boundary pads and write the bin info
    x,y = int(x), int(y)
    pady_drawx = 0
    padx_drawy = npx - 1

    if (x != padx_drawy) and (y != pady_drawx):
        return 0

    text = ROOT.TLatex()
    text.SetTextSize(tsize-14)
    text.SetTextAlign(23)

    # Draw bin info in x-axis
    if (y == pady_drawx):
        title = ms.get_bintxt("%s%s"%(vpx,x), d_bin["nBin"])
        text.DrawLatexNDC(sf.x_pad(0.50),sf.y_pad(-0.20), title)

    # Draw bin info in y-axis
    if (x == padx_drawy):
        text.SetTextAngle(90)
        title = ms.get_bintxt("%s%s"%(vpy,y), d_bin["nBin"])
        text.DrawLatexNDC(sf.x_pad(1.05),sf.y_pad(0.5), title)

    return text

def draw_line(hist):
# Draw line at 1.0
    line1 = ROOT.TLine(0.0,1.0, 1.0,1.0)
    line1.SetLineColorAlpha(ROOT.kRed, 0.5)
    line1.SetLineWidth(1)
    line1.SetLineStyle(9)

    xmin = hist.GetXaxis().GetXmin()
    xmax = hist.GetXaxis().GetXmax()
    line1.DrawLine(xmin,1.0, xmax,1.0)

    return line1


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
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
parser.add_option('-t', dest='type', default = "parameters",
                  help="Choose parameter type: Pars, Norm, Ratio")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")

options, args = parser.parse_args()

dataset = options.Dataset
isJLab = options.isJLab
par_type = options.type
ovr = options.Overwrite

input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

d_bin = ms.get_name_dict(dataset)
m_fit = ms.get_fit_method(input_cuts)

# Revisit this. Maybe plots_cuts might work better / be more general
initials = ms.get_plot_initials(d_bin["nBin"], input_cuts)
d_init_nbins = ms.get_bincode_nbins_dict(d_bin["nBin"], initials)

# Define type of plot
d_tp_bool, my_tp_nameS, my_tp_nameL = sf.get_parameters_type(par_type)

# Define Input
l_inputfile = []
l_tar_input = ms.summary_targ_type(plots_cuts)
# Skip ratio plot of liquid target
if (d_tp_bool["ratio"] and ("D" in l_tar_input[0])):
    ms.error_msg("Ratio", "Skip deuterium for ratio.")
first = True
for tar in l_tar_input:
    temp_dset = "%s_%s"%(tar, dataset)
    in_obj = nf.naming_format(my_tp_nameL, temp_dset, cuts=input_cuts,
                            is_JLab=isJLab)
    inputfile = TFile(in_obj.get_path(),"READ")

    if first:
        l_keys = inputfile.GetListOfKeys()
        l_kname, l_npar, l_meth = get_input_info(l_keys)
        first = False

    l_inputfile.append(inputfile)

# Create canvases
out_obj = nf.naming_format(my_tp_nameL, dataset, cuts=plots_cuts,
                           is_JLab=isJLab)
# outputfile = TFile(out_obj.get_path_summary(True, ovr),"RECREATE")
# TODO: Check how to generalize this for new binning with integrated Q, N, etc.

# Define number of pads and their coordinates
vpx = "Q"
vpy = "N" if "N" in d_init_nbins else "X"
npx = d_init_nbins[vpx]
npy = d_init_nbins[vpy]
l_canvas = sf.create_l_canvas(l_kname, npx, npy)

# Create generic/standard histogram to use in each pad
my_xvar = ms.get_xaxis(input_cuts)
my_xvar_init = ms.d_var_initial[my_xvar]
my_xaxis = ms.axis_label(my_xvar_init,"LatexUnit")
x_limits = ms.get_l_limits(d_bin["nBin"], my_xvar_init)
x_title = ";%s;"%(my_xaxis)
h_tmp = TH1D("h_tmp", x_title, len(x_limits)-1, array('d',x_limits))

# Fill canvases
l_bincodes = ms.get_bincode_list(d_bin["nBin"], input_cuts)
for cv in l_canvas:
    cv.cd(0)
    # Get input histograms
    kname = cv.GetName()
    first = True
    l_l_hist = []
    for i,file in enumerate(l_inputfile):
        hist = file.Get(kname)
        itarg = l_tar_input[i]
        # Avoid overwriting warning
        hist.SetName("%s-%s"%(kname,itarg))

        # Draw same axes in every pad
        if first:
            h_axis = draw_axes(cv, h_tmp, itarg)
            first = False

        # Get histograms
        d_padth1 = create_d_th1(hist, h_tmp, l_bincodes, vpx, vpy, my_xvar)

        # Draw histograms
        l_hist = fill_canvas(cv, d_padth1)
        l_l_hist.append(l_hist)

    cv.cd(0)
    # Draw legend
    legend = create_legend(kname, True)

    cv.cd(0)
    # Define canvas style
    ms.draw_summary("%s"%(my_tp_nameL))
    top_label_text = ms.summary_targ_type_legend(plots_cuts)
    ms.draw_targetinfo(top_label_text, "Data")

    out_obj.updt_name(nf.get_hist_hfullname(kname))
    out_obj.updt_acc_method(nf.get_hist_hmeth(kname))
    out_obj.updt_bin_code("")
    out_obj.updt_extension("png")

    cv.SaveAs(out_obj.get_path_summary(create=True, overwrite=True))
    # out_obj.get_file_name_summary()

    # Avoid memory leak warning
    h_axis.Delete()
    legend.Delete()

# Close input files
for file in l_inputfile:
    file.Close()
