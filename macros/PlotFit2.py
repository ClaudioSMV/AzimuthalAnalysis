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
gStyle.SetOptFit(1)

gStyle.SetStatX(1 - ms.get_margin() - 0.005)
gStyle.SetStatY(2*ms.get_margin() + 0.205)


## Define functions

def get_corrected_hist(h_input, h_name, this_fittype):
# Return a copy of the corrected histogram
    # Define initial and final bins depending on fit method
    Nbins_in = h_input.GetXaxis().GetNbins()
    bin_frst = 0
    bin_last = Nbins_in
    l_xbin_out = []
    # if (this_fittype == "LR"):
    if (this_fittype == "Fd"):
        bin0 = h_input.FindBin(0.0)
        bin_frst = bin0

        l_xbin_out.append(0.0)
    # elif (this_fittype == "Sh"):
    # elif (this_fittype == "Ff"):

    # Fill list with x-axis bin's limits
    for bt in range(bin_frst, bin_last+1):
        l_xbin_out.append(h_input.GetBinLowEdge(bt+1))

    # Create output histogram
    phi_axis_title = ms.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"
    h_out_title = ";%s;Counts"%(phi_axis_title)
    Nbins_out = len(l_xbin_out)-1

    h_output = TH1D(h_name, h_out_title, Nbins_out, array('d',l_xbin_out))

    # Fill output histogram
    for b in range(1, Nbins_in+1):
        # Retrieve values from original hist
        value = h_input.GetBinContent(b)
        error = h_input.GetBinError(b)
        this_bin = b

        # if (this_fittype == "LR"):
        if (this_fittype == "Fd"):

            x_center_in = h_input.GetBinCenter(b)

            bin_out = h_output.FindBin(abs(x_center_in))
            value_out = h_output.GetBinContent(bin_out)
            error_out = h_output.GetBinError(bin_out)

            # If bin is not empty, then you're running over the second tail
            # and must add the new content
            if (value_out > 1.0):
            # if (value_out != 0.0):
                value+=value_out
                error = TMath.Sqrt(error_out*error_out + error*error)

            this_bin = bin_out
        # elif (this_fittype == "Sh"):
        # elif (this_fittype == "Ff"):

        # Debug
        # print(this_bin)

        h_output.SetBinContent(this_bin, value)
        h_output.SetBinError(this_bin, error)

    return h_output

def get_fit_functions(h_out, l_fname, fit_meth, opts):
# Return list of TF1 with the proper range
    ### Options:
    ###     Skip0: Skip central peak
    ###     Sin: Use sin(x) term in fit

    # if (fit_meth == "LR"):
    # elif (fit_meth == "Fd"):
    # elif (fit_meth == "Sh"):
    # elif (fit_meth == "Ff"):

    # Define options: ["Fs", "NP",]
    opt_sk0 = ("NP" in ms.get_l_cuts(opts))
    opt_sin = ("Fs" in ms.get_l_cuts(opts))

    # Set limits
    Nbins = h_out.GetXaxis().GetNbins()

    ## Option: Skip peak's bin (Problematic)
    peak_Lend, peak_Rend = 0.0, 0.0
    if (opt_sk0):
        # Define peak bin as the one containing zero when using odd nbins
        # and as both pre-and-post bins to zero with even nbins
        bin_peak = h_out.FindBin(0.0)
        d_peak_end_odd = {
            "LR": [bin_peak, bin_peak+1], "Fd": [0, 2],
            "Sh": [Nbins+1, 2], "Ff": [0, 0],
        }
        d_peak_end_even = {
            "LR": [bin_peak-1, bin_peak+1], "Fd": [0, 2],
            "Sh": [Nbins, 2], "Ff": [0, 0],
        }

        bin_odd = ((Nbins%2) == 1)

        # Define limits of the peak for the fit function
        if bin_odd:
            peak_Lend = h_out.GetBinLowEdge(d_peak_end_odd[fit_meth][0])
            peak_Rend = h_out.GetBinLowEdge(d_peak_end_odd[fit_meth][1])
        else:
            peak_Lend = h_out.GetBinLowEdge(d_peak_end_even[fit_meth][0])
            peak_Rend = h_out.GetBinLowEdge(d_peak_end_even[fit_meth][1])

    xmin_out = h_out.GetBinLowEdge(1)
    xmax_out = h_out.GetBinLowEdge(Nbins+1)
    list_limits = []
    # Define limits of the fit functions
    ## for [Right, Left*]
    for i,func in enumerate(l_fname):
        this_xmin, this_xmax = xmin_out, xmax_out

        if (fit_meth == "LR"):
            this_xmin = peak_Rend if (i==0) else  xmin_out
            this_xmax =  xmax_out if (i==0) else peak_Lend
        elif (fit_meth == "Fd"):
            this_xmin = peak_Rend
            this_xmax =  xmax_out
        elif (fit_meth == "Sh"):
            this_xmin = peak_Rend if (peak_Rend != 0.0) else xmin_out
            this_xmax = peak_Lend if (peak_Lend != 0.0) else xmax_out
        # elif (fit_meth == "Ff"):

        these_limits = [this_xmin, this_xmax]
        list_limits.append(these_limits)

    # Define function
    the_func = "[0] + [1]*cos(TMath::Pi()*x/180.0) +"\
               " [2]*cos(2*TMath::Pi()*x/180.0)"
    if opt_sin:
        the_func+= "+ [3]*sin(TMath::Pi()*x/180.0)"

    tf1_fit = []
    # Create TF1 and return
    ## for [Right, Left*]
    for i,fname in enumerate(l_fname):
        this_xmin = list_limits[i][0]
        this_xmax = list_limits[i][1]

        this_func = TF1(fname,the_func, this_xmin,this_xmax)
        tf1_fit.append(this_func)

    return tf1_fit


def get_chi2ndf(f_fit, x,y, meth_ffit):
    chisq = f_fit.GetChisquare()
    ndf = f_fit.GetNDF()

    fit_str = "#chi^{2} / ndf = %.2f / %i"%(chisq, ndf)
    if (ndf != 0):
        fit_str+= " = %.2f"%(chisq/ndf)
    fit_str = TLatex(x,y, fit_str)

    # 23: use center as reference (default method)
    text_orientation = 23
    if ("LR" in meth_ffit):
        # 13: use left corner as reference (for R method);
        # 33: use right corner as reference (for L method)
        text_orientation = 13 if ("0" in meth_ffit) else 33
    # elif (this_fittype == "Fd"):
    # elif (this_fittype == "Sh"):
    # elif (this_fittype == "Ff"):

    fit_str.SetTextAlign(text_orientation)
    fit_str.SetTextSize(ms.get_size()-6)

    return fit_str

def check_fit_feasibility(hist, fit_method):
# Check if histogram can receive a proper fit treatment
    hname = hist.GetName()
    hentries = hist.GetEntries()
    Nbins = hist.GetXaxis().GetNbins()
    problem = False
    if (hentries == 0):
        info_txt = "Histogram %s is empty! Fit is not possible."%hname
        problem = True
    elif (hentries < 4): # ndf cut
        info_txt = "Histogram %s has not enough bins!"\
                   " Fit is not feasible."%hname
        problem = True
    elif ((fit_method is "LR") and (hentries < Nbins/2.)):
        info_txt = "Histogram %s has half or more empty bins!"\
                   " Fit LR is not feasible."%hname
        problem = True

    is_good = True
    if problem:
        ms.info_msg("Fit",info_txt)
        is_good = False

    return is_good


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
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

input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

d_bin = ms.get_name_dict(dataset)
m_fit = ms.get_fit_method(plots_cuts)


in_obj = nf.naming_format("Correction", dataset, cuts=input_cuts,
                          is_JLab=isJLab)
inputfile = TFile(in_obj.get_path(),"READ")

out_obj = nf.naming_format("Fit", dataset, cuts=plots_cuts,
                          is_JLab=isJLab)
# outputfile = TFile(out_obj.get_path(True),"RECREATE")

l_hists = inputfile.GetListOfKeys()
l_ffit_names = out_obj.get_l_fitnames()

# Create and save output
canvas = ms.create_canvas()
outputfile = TFile(out_obj.get_path(True, ovr),"RECREATE")
phi_axis_title = ms.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"

gStyle.SetTitleYOffset(1.2)

for h in l_hists:
    obj_type = h.ReadObj().Class_Name()

    if "TH1D" not in obj_type:
        continue
    hname = h.GetName()
    if "raw" in hname.lower():
        continue

    # Name format: h(name)_(acc_meth)_(bincode)
    _, cor_meth, bincode = hname.split("_")

    out_obj.updt_acc_method(cor_meth)
    out_obj.updt_bin_code(bincode)

    # Get Histogram
    hist = h.ReadObj()

    # Check feasibility of applying fit
    fit_work = check_fit_feasibility(hist, m_fit)
    if not fit_work:
        continue

    # Get corrected histogram
    hist_corr = get_corrected_hist(hist, out_obj.get_hist_name(), m_fit)

    hist_corr.SetMinimum(0.0001)
    hist_corr.SetMaximum(hist_corr.GetMaximum()*1.4)
    hist_corr.Draw("hist axis")

    # Return list of TF1 with the proper range
    # Use plots_cuts to find special cuts/options
    l_tf1 = get_fit_functions(hist_corr, out_obj.get_l_fitnames(),
                              m_fit, plots_cuts)

    # Make fit and save covariance and correlation matrices
    l_chi2 = []
    for i,fitfunc in enumerate(l_tf1):
        this_fopts = "MSRQ"
        if (i==1):
            this_fopts+= "+"

        fit_matrix = hist_corr.Fit(l_ffit_names[i], this_fopts, "")
        name_cov = out_obj.get_matrix_name("cov", i)
        fit_matrix.GetCovarianceMatrix().Write(name_cov)

        name_corr = out_obj.get_matrix_name("corr", i)
        fit_matrix.GetCorrelationMatrix().Write(name_corr)

        ## Draw chi2 info
        d_pos_tex = {
            "LR": [15.0, -15.0], "Fd": [90.0], "Sh": [180.0], "Ff": [0.0],
        }

        xpos_tex = d_pos_tex[m_fit][i] if m_fit in d_pos_tex else 0.0
        ypos_tex = 1.1*hist.GetMaximum()

        info_chi2 = get_chi2ndf(fitfunc, xpos_tex,ypos_tex, "%s%i"%(m_fit,i))
        l_chi2.append(info_chi2)

    for c in l_chi2:
        c.Draw()

    # Draw and save
    hist_corr.GetYaxis().SetMaxDigits(3)
    hist_corr.Draw("FUNC same")
    hist_corr.Write()

    ms.draw_preliminary("Correction fit")
    ms.draw_targetinfo(ms.get_name_format(dataset), "Data")
    ms.draw_bininfo(bincode, d_bin["nBin"])

    out_obj.updt_extension("png")
    canvas.SaveAs(out_obj.get_path())

    # out_obj.updt_extension("pdf")
    # canvas.SaveAs(out_obj.get_path())

    canvas.Clear()

ms.info_msg("Fit", "Fit parameters saved!\n")
outputfile.Close()
