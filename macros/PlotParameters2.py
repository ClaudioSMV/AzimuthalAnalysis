from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,\
    TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,\
    kWhite,TH1
import ROOT
import os
import optparse
import copy
import myStyle as ms
import myNameFormat as nf
import mySumFunctions as sf

## Defining Style
ms.force_style()

gStyle.SetStatX(1 - ms.get_margin() - 0.005)
gStyle.SetStatY(2*ms.get_margin() + 0.205)


## Define functions
def calculate_errdivision(v1, e1, v2, e2, cov=0):
# Propagate error using proper formula with covariance included
    r1 = e1/v1
    r2 = e2/v2
    my_error = TMath.Abs(v1/v2)*TMath.Sqrt(r1*r1 + r2*r2 - 2*cov/(v1*v2))

    return my_error

def get_matrixelement(matrix, row, col):
# Return element in position row,col of matrix
    this_matrix = matrix.GetMatrixArray()
    index = col + 3*row

    return this_matrix[index]

def get_fit_pars(hist):
# Return list with dictionaries saving fit function name and two lists:
# made of parameters and their associated errors, per fit function
    fits_results = []
    # Run over all fit functions associated with the histogram
    list_functions = hist.GetListOfFunctions()
    for i in range(list_functions.GetSize()):
        ffit = list_functions.At(i)
        fname = ffit.GetName()
        fpars = []
        ferrs = []

        # Check if the element is a TF1 fit function
        if not isinstance(ffit, ROOT.TF1):
            continue

        this_par = ffit.GetParameters()
        this_err = ffit.GetParErrors()
        n_parameters = ffit.GetNpar()

        # Save all parameters and errors for this function
        for p in range(n_parameters):
            fpars.append(this_par[p])
            ferrs.append(this_err[p])

        this_dict = {"fname": fname, "parv": fpars, "pare": ferrs}
        fits_results.append(this_dict)

    return fits_results

def get_input_info(l_keys):
# Retrieve fit information from list of keys, returning a tuple with:
# n fit functions, n fit parameters, set of correction methods,
# dictionary with fit parameters, and dictionary with covariance matrices
    s_meth = set()
    nfit, npar = 0, 0
    first_entry = True
    # Get list with fit parameters and covariance matrices
    d_pfit = {} # {hname: [{fname, [fpars (parv)], [ferrs (pare)]}]}
    d_covm = {} # {bincode_meth: [matrices]}
    for key in l_keys:
        obj_type = key.ReadObj().Class_Name()
        kname = key.GetName()
        # Extract parameters from fit functions
        if "TH1D" in obj_type:
            if "raw" in kname.lower():
                continue

            hist = key.ReadObj()
            dict_pars = get_fit_pars(hist)
            d_pfit[kname] = dict_pars

            # Save number of fits and parameters once only
            if first_entry:
                nfit = len(dict_pars)
                npar = len(dict_pars[0]["parv"])
                first_entry = False
        
        # Save covariance matrices
        else:
            if "cov" not in kname:
                continue

            # Name format: M(name)(number)_(acc_meth)_(bincode)
            mname = nf.get_hist_hname(kname)
            mmeth = nf.get_hist_hmeth(kname)
            mbincode = nf.get_hist_hbincode(kname)
            # Get set with all correction methods used
            s_meth.add(mmeth)

            fnumb = int(mname[-1])
            code_name = "%s_%s"%(mbincode, mmeth)

            matrix = key.ReadObj()
            # Use (bincode)_(acc_meth) as key to the matrices' list
            if code_name not in d_covm:
                d_covm[code_name] = [matrix]
            else:
                # Add first Right fit (0 index) and second Left one (1 index)
                d_covm[code_name].insert(fnumb,matrix)

    return (nfit, npar, s_meth, d_pfit, d_covm)

def get_values(l_l_val, l_l_err, l_covm):
# Obtain list of values and errors for the type of interest to plot
# (Pars, Norm, Ratio, etc.)
    l_newval, l_newerr = [], []
    l_val, l_err, covm = l_l_val[0], l_l_err[0], l_covm[0]

    for i in range(len(l_val)):
        val = l_val[i]
        err = l_err[i]

        if d_tp_bool["norm"]:
            val, err = value_norm(l_val, l_err, covm, i)

        elif d_tp_bool["ratio"]:
            l_valD, l_errD, covmD = l_l_val[1], l_l_err[1], l_covm[1]
            val, err = value_ratio(l_val, l_err, covm, l_valD, l_errD, covmD, i)

        l_newval.append(val)
        l_newerr.append(err)

    return l_newval, l_newerr

def value_norm(l_val, l_err, covm, iidx, nidx = 0):
# Calculate normalized parameters (using nidx term as reference)
    ival, ierr = l_val[iidx], l_err[iidx]
    nval, nerr = l_val[nidx], l_err[nidx]
    # Remember the factor 1/2 to match the definition
    weight = 1./2
    new_val = weight * (ival / nval)
    cov_val = get_matrixelement(covm, nidx, iidx)
    new_err = calculate_errdivision(ival, ierr, nval, nerr, cov_val)
    # The next line is right! Leave it commented out to check previous results
    # with the old definition (previous line)
    # new_err = weight * calculate_errdivision(ival, ierr, nval, nerr, cov_val)

    return (new_val, new_err)

def value_ratio(l_val, l_err, covm, l_valD, l_errD, covmD, iidx, nidx = 0):
# Calculate ratio of solid over Deuterium parameters
# (using nidx term as reference to normalize)
    val, err = value_norm(l_val, l_err, covm, iidx, nidx)
    valD, errD = value_norm(l_valD, l_errD, covmD, iidx, nidx)

    new_val = val / valD
    new_err = calculate_errdivision(val, err, valD, errD)

    return (new_val, new_err)


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "",
                  help="Add input cuts Xf_Yb_Z/P...")
parser.add_option('-o', dest='outputCuts', default = "",
                  help="Add output cuts FE_...")

parser.add_option('-t', dest='type', default = "parameters",
                  help="Choose parameter type: Pars, Norm, Ratio")
parser.add_option('-v', dest='verbose', action='store_true', default = False,
                  help="Print values")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")

options, args = parser.parse_args()

dataset = options.Dataset
isJLab = options.isJLab
par_type = options.type
verb = options.verbose
ovr = options.Overwrite

input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

d_bin = ms.get_name_dict(dataset)
m_fit = ms.get_fit_method(plots_cuts)

# Define type of plot
d_tp_bool, my_tp_nameS, my_tp_nameL = sf.get_parameters_type(par_type)

# Define Input
in_obj = nf.naming_format("Fit", dataset, cuts=input_cuts,
                          is_JLab=isJLab)
inputfile = TFile(in_obj.get_path(),"READ")

# Retrieve info from input
l_keys = inputfile.GetListOfKeys()
n_fits, n_pars, s_meth, d_pfit, d_covm = get_input_info(l_keys)

if d_tp_bool["ratio"]:
    if "D" in d_bin["Target"]:
        info_txt = "Ratio is not possible with D target. Skipping"
        ms.info_msg(my_tp_nameL, info_txt)
        exit()

    D_obj = nf.naming_format("Fit", "D%s"%(dataset), cuts=input_cuts,
                             is_JLab=isJLab)
    Dfile = TFile(D_obj.get_path(),"READ")

    # Retrieve info from D input
    l_keysD = Dfile.GetListOfKeys()
    _, _, _, d_pfitD, d_covmD = get_input_info(l_keysD)

    Dfile.Close()

l_bincodes = ms.get_bincode_list(d_bin["nBin"],input_cuts)
totalsize = len(l_bincodes)

out_obj = nf.naming_format(my_tp_nameL, dataset, cuts=plots_cuts,
                           is_JLab=isJLab)
# outputfile = TFile(out_obj.get_path(True, ovr),"RECREATE")

# Get x-axis variable information
my_xvar = ms.get_xaxis(input_cuts)
my_xvar_init = ms.d_var_initial[my_xvar]

# Create final plots with dictionary to store final hists per method
d_hfinal = {}
for sm in s_meth:
    out_obj.updt_acc_method(sm)
    for i in range(n_fits):
        kname = "%s%i"%(sm,i)
        d_hfinal[kname] = []
        for par in range(n_pars):
            hname = out_obj.get_hist_name_summary(i, par)
            htitle = ";Bin;%s"%my_tp_nameS
            this_hist = TH1D(hname, htitle, totalsize,0.0,totalsize)
            # Change x-axis to get bincode as label per bin
            for bc in l_bincodes:
                this_hist.Fill(bc, 0.0)

            d_hfinal[kname].append(this_hist)

# Create output
out_obj.updt_acc_method("")
canvas = ms.create_canvas()
outputfile = TFile(out_obj.get_path(True, ovr),"RECREATE")

gStyle.SetTitleYOffset(1.2)

# Fill final histograms
for fullname in d_pfit:
    # d_pfit = {} # {hname: [{fname, [fpars (parv)], [ferrs (pare)]}]}
    hname = nf.get_hist_hname(fullname)
    hmeth = nf.get_hist_hmeth(fullname)
    hbincode = nf.get_hist_hbincode(fullname)

    # Save name of the covariance matrix
    kmatrix = "%s_%s"%(hbincode,hmeth)

    # Loop over fit functions (useful for LR method only 77)
    for dict in d_pfit[fullname]:
        ifit = 0 if "R" in dict["fname"] else 1
        hfinal_name = "%s%i"%(hmeth,ifit)

        l_parv = dict["parv"]
        l_pare = dict["pare"]
        cov_matrix = d_covm[kmatrix][ifit]

        l_l_parv, l_l_pare, l_cov = [l_parv], [l_pare], [cov_matrix]
        if d_tp_bool["ratio"]:
            l_l_parv.append(d_pfitD[fullname][ifit]["parv"])
            l_l_pare.append(d_pfitD[fullname][ifit]["pare"])
            l_cov.append(d_covmD[kmatrix][ifit])

        f_par, f_err = get_values(l_l_parv, l_l_pare, l_cov)

        # Fill final histogram
        for i,parv in enumerate(f_par):
            value, error = f_par[i], f_err[i]
            hfin = d_hfinal[hfinal_name][i]
            # hfin.Fill(hbincode, 0.0)
            fbin = hfin.GetXaxis().FindBin(hbincode)

            hfin.SetBinContent(fbin, value)
            hfin.SetBinError(fbin, error)

# Save and write histograms
for kname in d_hfinal:
    tmeth, tfidx = kname[:-1], kname[-1:]
    for i,hf in enumerate(d_hfinal[kname]):
        plot_obj = copy.copy(out_obj)
        plot_obj.updt_name("%sp%i"%(tfidx,i), True)
        plot_obj.updt_acc_method(tmeth)
        plot_obj.updt_bin_code("")
        plot_obj.updt_extension("png")

        # Define y limits
        y_limit = sf.get_parameters_limits(d_tp_bool, i, my_xvar_init)
        ymin, ymax = y_limit

        hf.SetLineWidth(2)
        hf.SetLineColor(ROOT.kBlue)
        hf.SetMinimum(ymin)
        hf.SetMaximum(ymax)
        hf.Write()
        hf.Draw("hist e")

        ms.draw_preliminary("%s %s"%(my_tp_nameL, tmeth))
        ms.draw_targetinfo(ms.get_name_format(dataset), "Data")

        canvas.SaveAs(out_obj.get_folder_name() + plot_obj.get_file_name())
        canvas.Clear()

ms.info_msg(my_tp_nameL, "Made it to the end!\n")
outputfile.Write()
outputfile.Close()
inputfile.Close()
