import ROOT
import os
import Bins as bn


################################################################################
##                              Global variables                              ##
################################################################################

marg=0.05
font=43 # Helvetica
tsize=38

def get_margin():
# Return margin value
    return marg

def get_font():
# Return font value
    return font

def get_size():
# Return size of text value
    return tsize

def get_pad_center(mleft=2*marg, mright=marg):
    center = 1/2. + mleft/2. - mright/2.
    return center

################################################################################
##                         Name and input code format                         ##
################################################################################

def get_targ_input(targ_str):
# Transform <targ>_<nBin>_<nDim> input into list
    l_targ = targ_str.split("_")
    # Remove empty elements
    while("" in l_targ):
        l_targ.remove("")
    # Add target default name
    if l_targ[0] not in color_target:
        l_targ.insert(0, "None")
    # Transform nBin element into int
    l_targ[1] = int(l_targ[1])
    # Add and transform nDim element (using 1 as default number)
    if len(l_targ) == 2:
        l_targ.append(1)
    l_targ[2] = int(l_targ[2])

    # Kill if formating didn't work
    if len(l_targ) > 3:
        error_msg("Input", "Format <targ>_<nBin>_<nDim> was not followed!")

    return l_targ

def get_name_dict(format):
# Create dictionary from <targ>_<nBin>_<nDim> input
    l_input = get_targ_input(format)
    d_targ = {
        "Target": l_input[0], "targ": l_input[0],
        "BinningType": l_input[1], "nBin": l_input[1], "n_bin": l_input[1],
        "NDims": l_input[2], "nDim": l_input[2], "n_dim": l_input[2],
    }

    return d_targ

def get_name_format(format, isAcc = False):
# Use <targ>_<nBin>_<nDim> and receive "<targ>_<nBin>B<nDim>" as output
    d_format = get_name_dict(format)
    fileName = "%s_%iB"%(d_format["Target"],d_format["nBin"])
    if (not isAcc) and d_format["nDim"]:
        fileName+="%i"%(d_format["nDim"])

    return fileName

def get_name_format_inverse(nameFormat, isAcc = False):
# Give string with name formatted inversed using input: <targ>_<nBin>_<nDim>
# with output: "<nBin>B<nDim>_<targ>"
    formDict = get_name_dict(nameFormat)
    fileName = "%iB"%(formDict["BinningType"])
    if (not isAcc) and formDict["NDims"]:
        fileName+="%i"%(formDict["NDims"])
    fileName+= "_%s"%(formDict["Target"])

    return fileName

def get_name_format_bin(nameFormat):
# Give string with name formatted using input: <targ>_<nBin>_<nDim>
# with output: "<nBin>B<nDim>"
    nameFull = get_name_format(nameFormat)
    name_bin = nameFull.split('_')[1]

    return name_bin

def add_str_before_ext(path, before_dot, other_extension = "root"):
# Returns same string <path> with new text <before_dot> before extension
    new_path = path.split(".%s"%other_extension)[0]

    return new_path + before_dot + "." + other_extension


################################################################################
##                              Inline messages                               ##
################################################################################

def error_msg(function, text):
    msg_str = "  [!|%s] "%(function)
    msg_str+= text

    print(msg_str)
    exit()

def info_msg(function, text):
    msg_str = "  [%s] "%(function)
    msg_str+= text

    print(msg_str)


################################################################################
##                           Cuts and dictionaries                            ##
################################################################################

################  Transform a long cut's name into a short tag  ################
d_cut_acc = {
    "XF": "Xf", "Xf": "Xf", "CFR": "Xf",
    "XT_TFR": "XT", "XTFR": "XT", "Xt": "XT", "XT": "XT", "TFR": "XT",
    "DeltaSector": "DS", "DSect": "DS", "DSctr": "DS", "DS": "DS",\
    "DSect0": "DS",
    "BadSector": "BS", "rmBadSector": "BS", "BS": "BS", "rS": "BS",\
    "NoBadSec": "BS",
    "PionFiducial": "PF", "PiFiducial": "PF", "Pf": "PF", "PF": "PF",\
    "PFid": "PF", "PiFid": "PF",
    "MirrorMatch": "MM", "MMtch": "MM", "MM": "MM",
    "MirrorMatch2": "M2", "MMtch2": "M2", "M2": "M2", "MM2": "M2",
}
d_cut_cor = {
    "FErr": "FE", "FullError": "FE", "Fe": "FE", "FE": "FE", "Err": "FE",
    "AccQlt": "AQ", "AccQuality": "AQ", "AQ": "AQ",
    "rmNpheElH": "Pe", "PheElH": "Pe", "PE": "Pe", "Pe": "Pe",\
    "rmTheLine": "Pe", "dfNphe": "Pe",
}
d_cut_xax = {
    "Z": "Zx", "Zx": "Zx",
    "P": "Px", "Px": "Px",
}
d_cut_fit = {
    "useSin": "Fs", "FitSin": "Fs", "Fs": "Fs", "fSin": "Fs",
    "NPeak": "NP", "NP": "NP",
    "Norm": "Nm", "Normalize": "Nm", "Nm": "Nm", "PreNorm": "Nm"
}
d_cut_sum = {
    "MixD": "MD", "MD": "MD", "mergeD": "MD",
}
d_cut_tar = {
    "solid": "sl", "sl": "sl", "Sl": "sl", "Sol": "sl",
    "liquid": "lq", "Lq": "lq", "liq": "lq", "lq": "lq", "Liq": "lq",
}
d_fit_met = {
    "Shift": "Sh", "Sh": "Sh",
    "Fold": "Fd", "Fd": "Fd",
    "LR": "LR",
    "Fullfit": "Ff", "FFit": "Ff", "Ff": "Ff", "FullRng": "Ff",
}

d_cuts = {} # Merge all dictionaries into one
d_cuts.update(d_cut_acc)
d_cuts.update(d_cut_cor)
d_cuts.update(d_cut_xax)
d_cuts.update(d_cut_fit)
d_cuts.update(d_cut_sum)
d_cuts.update(d_cut_tar)
d_cuts.update(d_fit_met)


##################  From short tag to /Output/ folder's tags  ##################
d_cut_out_acc = {
    "Xf": "Xf", "XT": "XTFR", "DS": "DSect0", "BS": "NoBadSec",
    "PF": "PiFid", "MM": "MMtch", "M2": "MMtch2",
}
d_cut_out_cor = {
    "FE": "FErr", "AQ": "AccQlt", "Pe": "dfNphe",
}

d_cuts_output = {} # Merge all dictionaries into one
d_cuts_output.update(d_cut_out_acc)
d_cuts_output.update(d_cut_out_cor)


################  From short tag to /Plot-Final/ folder's tags  ################
d_cut_fin_acc = {
    "Xf": "CFR", "XT": "TFR", "DS": "DS", "BS": "rS", "PF": "PFid",
    "MM": "MM", "M2": "MM2",
}
d_cut_fin_cor = {
    "FE": "Err", "AQ": "AQ", "Pe": "rmTheLine",
}
d_cut_fin_xax = {
    "Zx": "Zx", "Px": "Px",
}
d_cut_fin_fit = {
    "Fs": "fSin", "NP": "NP", "Nm": "PreNorm",
}
d_cut_fin_sum = {
    "MD": "mergeD",
}
d_cut_fin_tar = {
    "sl": "Sol", "lq": "Liq",
}
d_fit_fin_met = {
    "Sh": "Shift", "Fd": "Fold", "LR": "LR", "Ff": "FullRng",
}

d_cuts_final = {} # Merge all dictionaries into one
d_cuts_final.update(d_cut_fin_acc)
d_cuts_final.update(d_cut_fin_cor)
d_cuts_final.update(d_cut_fin_xax)
d_cuts_final.update(d_cut_fin_fit)
d_cuts_final.update(d_cut_fin_sum)
d_cuts_final.update(d_cut_fin_tar)
d_cuts_final.update(d_fit_fin_met)


######################  From short tag to legend's title  ######################
d_cut_leg_acc = {
    "Xf": "#X_f CFR", "XT": "#X_f TFR", "DS": "#Delta Sect #neq 0",
    "BS": "No bad Sect", "PF": "Fidual cut #pi",
    "MM": "Mirror Matching", "M2": "Mirror Matching 2",
}
d_cut_leg_cor = {
    "FE": "", "AQ": "", "Pe": "N_{phe}^{el} #neq N_{phe}^{h}",
}
d_cut_leg_xax = {
    "Zx": "", "Px": "",
}
d_cut_leg_fit = {
    "Fs": "Fit with Sin(x)", "NP": "Skip central peak",
    "Nm": "Previously normalized",
}
d_cut_leg_sum = {
    "MD": "Merge all D",
}
d_cut_leg_tar = {
    "sl": "Solid targets", "lq": "Liquid targets",
}
d_fit_leg_met = {
    "Sh": "Shift", "Fd": "Fold", "LR": "LR", "Ff": "Full range",
}

d_cuts_legend = {} # Merge all dictionaries into one
d_cuts_legend.update(d_cut_leg_acc)
d_cuts_legend.update(d_cut_leg_cor)
d_cuts_legend.update(d_cut_leg_xax)
d_cuts_legend.update(d_cut_leg_fit)
d_cuts_legend.update(d_cut_leg_sum)
d_cuts_legend.update(d_cut_leg_tar)
d_cuts_legend.update(d_fit_leg_met)


######################  List with cuts in correct order  #######################
l_cut_tar = ["sl", "lq",]
l_cut_xaxis = ["Zx", "Px",]
l_fit_met = ["Sh", "Fd", "LR", "Ff",]
l_cut_acc = ["Xf", "XT", "DS", "BS", "PF", "MM", "M2",]
l_cut_cor = ["FE", "AQ", "Pe",]
l_cut_fit = ["Fs", "NP", "Nm",]
l_cut_sum = ["MD",]

l_cuts = []
l_cuts.extend(l_cut_tar)
l_cuts.extend(l_cut_xaxis)
l_cuts.extend(l_fit_met)
l_cuts.extend(l_cut_acc)
l_cuts.extend(l_cut_cor)
l_cuts.extend(l_cut_fit)
l_cuts.extend(l_cut_sum)


def summary_targ_type(cut_str):
# Return list with list of targets to run over, based on l_cut_tar
    l_targtype = []
    l_solid = ["C", "Fe", "Pb"]
    l_liquid = ["DC", "DFe", "DPb"]
    d_lists = {"sl": l_solid, "lq": l_liquid}

    # Get list with internal names
    l_cuts = get_l_cuts(cut_str)

    unique = True
    for x in l_cut_tar:
        if (x in l_cuts) and unique:
            l_targtype = list(d_lists[x])
            unique = False
        elif (x in l_cuts) and not unique:
            this_msg = "Only solid (sl) or liquid (lq) sets are supported!"
            error_msg("targ_type", this_msg)

    if not l_targtype:
        this_msg = "Choose one set of targets: solid (sl) or liquid (lq)."
        error_msg("targ_type", this_msg)

    return l_targtype

def summary_targ_type_legend(cut_str):
# Return text to use in legend or top label
    # Get list with internal names
    l_cuts = get_l_cuts(cut_str)

    unique = True
    for cut in d_cut_leg_tar:
        if (cut in l_cuts) and unique:
            targ_legend = d_cut_leg_tar[cut]
            unique = False
        elif (cut in l_cuts) and not unique:
            error_msg("targ_type", "Only solid or liquid sets are supported!")

    return targ_legend


################################################################################
##                                Format cuts                                 ##
################################################################################

def get_l_cuts(cut_str):
# Return list with short cut tags
    l_mycuts = cut_str.split("_")
    # Remove empty entries from input
    while("" in l_mycuts):
        l_mycuts.remove("")

    # Save input entries with their short name
    for c,cut in enumerate(l_mycuts):
        if cut in d_cuts:
            l_mycuts[c] = d_cuts[cut]
        # Send error if input doesn't exist
        else:
            err_txt = "\"%s\" cut not found in any list."%(cut)
            error_msg("Cut", err_txt)
    # Remove repeated elements
    l_mycuts = list(set(l_mycuts))

    return l_mycuts

def get_cut_final(cut_str = "", among_these = "all", is_output = False):
# Transform str with cuts as in "Aa_Bb_Cccc" into a str with final names
    ref_list = list(l_cuts)
    # Create list with possible cuts only (say, our universe of options)
    unwanted_cuts = []
    if is_output:
        unwanted_cuts.extend(l_cut_sum)
        unwanted_cuts.extend(l_cut_fit)
        unwanted_cuts.extend(l_fit_met)
        unwanted_cuts.extend(l_cut_xaxis)
        if "acc" in among_these.lower():
            unwanted_cuts.extend(l_cut_cor)
    elif "closure" in among_these.lower():
        unwanted_cuts.extend(l_cut_fit)
        unwanted_cuts.extend(l_fit_met)
        unwanted_cuts.extend(l_cut_sum)
        unwanted_cuts.remove("Sh")
    elif among_these is not "all":
        is_higher_cut = False
        if ("acc" in among_these.lower()) or is_higher_cut:
            unwanted_cuts.extend(l_cut_cor)
            unwanted_cuts.extend(l_cut_xaxis)
            is_higher_cut = True
        if ("corr" in among_these.lower()) or is_higher_cut:
            unwanted_cuts.extend(l_cut_fit)
            unwanted_cuts.extend(l_fit_met)
            if not is_higher_cut:
                unwanted_cuts.remove("Sh")
            is_higher_cut = True
        if ("sum" not in among_these.lower()) or is_higher_cut:
            unwanted_cuts.extend(l_cut_sum)
            is_higher_cut = True
    unwanted_cuts = list(set(unwanted_cuts))

    # Remove selected elements from reference
    for uc in unwanted_cuts:
        ref_list.remove(uc)

    # Get list with internal/short names no repeated
    l_mycuts = get_l_cuts(cut_str)

    # Check that only one xaxis is used (just in case)
    _xaxis = get_xaxis(cut_str)

    l_cutfin = []
    # Save proper name in final list
    for possible_cut in ref_list:
        if possible_cut in l_mycuts:
            ftag = d_cuts_final[possible_cut]
            if is_output:
                ftag = d_cuts_output[possible_cut]
            l_cutfin.append(ftag)
            l_mycuts.remove(possible_cut)

    # Send warning if an existing cut is not in the sublist
    if len(l_mycuts) > 0:
        inf_txt = "Elements not used as cuts: %s."%(l_mycuts)
        info_msg("Cut", inf_txt)

    final_str = "_".join(l_cutfin)
    return final_str


################################################################################
##                      Bincode and variables' functions                      ##
################################################################################

def get_l_limits(nbin, init):
# Return list with limits for the specific variable
    my_dict = all_dicts[nbin]
    if init not in my_dict:
        error_msg("Limits", "Variable not found :(")

    return my_dict[init]

def get_plot_initials(nbin, cuts):
# Get string with initials of the bincode
    binstr = "Q"
    binstr+= "N" if "X" not in all_dicts[nbin] else "X"
    binstr+= get_var_init(cuts, True) # Z or P

    return binstr

def get_bincode_nbins(nbin, initials):
# Return list with number of bins for this configuration
    nbins = []
    # Get total number of bins per variable (remove integrated ones)
    for v,var in enumerate(initials):
        this_bin = len(all_dicts[nbin][var]) - 1
        nbins.append(this_bin)

    return nbins

def get_bincode_nbins_dict(nbin, initials):
# Return dictionary with number of bins for this configuration
    nbins = {}
    # Get total number of bins per variable (remove integrated ones)
    for v,var in enumerate(initials):
        this_bin = len(all_dicts[nbin][var]) - 1
        nbins[var] = this_bin

    return nbins

def get_bincode_list(nbin, cuts):
# Create bincode list with the nbin configuration and using variables defined
# in cuts (say, Zh or Pt2 bins)
    vars_init = get_plot_initials(nbin, cuts)
    l_nbins = get_bincode_nbins(nbin, vars_init)

    output_list = []
    totalsize = 1
    for nb in l_nbins:
        totalsize*=nb
    # Create str with bincode and save it in list
    for i in range(totalsize):
        total_tmp = totalsize
        i_tmp = i
        txt_tmp = ""
        for v,var in enumerate(vars_init):
            total_tmp /= l_nbins[v]
            index = i_tmp/(total_tmp)
            i_tmp-= index*total_tmp
            txt_tmp+= "%s%i"%(var, index)
        output_list.append(txt_tmp)

    # Output would be ["Q0N0Z0", "Q0N0Z1", ..., "Q3N3Z9"]
    return output_list

def get_bincode_varidx(bincode, init):
# Return index number associated to init var in bincode
# i.e. in "Q0N2Z4", init="Z" will return 4, and init="Q" will return 0
    init = d_var_initial[init]
    if init not in bincode:
        error_msg("Bincode", "Variable not found in bincode :(")
    idx_char = bincode.index(init)
    varidx = int(bincode[idx_char+1])

    return varidx

def get_bincode_varbin(bincode, init):
# Return bin number associated to init var in bincode
# i.e. in "Q0N2Z4", init="Z" will return 5, and init="Q" will return 1
    varbin = get_bincode_varidx(bincode, init) + 1

    return varbin


################################################################################
##                         Histograms and projections                         ##
################################################################################

def create_phi_hist(th1_input, name, do_shift):
# Create a copy of a 1d histogram for phi_PQ
# By default, it uses x-axis within [-180, 180]
# Option do_shift plots within [0, 360]
    this_xmin = th1_input.GetXaxis().GetXmin() # -180.
    this_xmax = th1_input.GetXaxis().GetXmax() #  180.
    this_nbin = th1_input.GetNbinsX()

    if (do_shift):
        # if (this_nbin%2 == 0): # Even (0. is in a bin edge) (default)
        this_xmin =   0.
        this_xmax = 360.
        central_bin = int(this_nbin/2)+1
        # Note that if nbin is Even, central_bin is the bin at the right of the
        # central one; if it is Odd, central_bin is the real central one;

        if (this_nbin%2 == 1): # Odd (0. is in the middle of a bin)
            bin_width = th1_input.GetBinWidth(central_bin)

            # Slightly shift edges so that bins are correct
            this_xmin -= bin_width/2.
            this_xmax -= bin_width/2.

    ax_name = ";%s;Counts"%(axis_label('I',"LatexUnit"))
    h_tmp = ROOT.TH1D(name,ax_name, this_nbin, this_xmin, this_xmax)

    # Fill histogram bin by bin
    for i in range(1,this_nbin+1):
        this_value = th1_input.GetBinContent(i)
        this_error = th1_input.GetBinError(i)
        # if (this_value == 0):
        #     print("    %s : Value: %i"%(name,this_value))
        #     this_value = 0.0
        #     this_error = 0.0
        bin_L_edge = th1_input.GetBinLowEdge(i)
        bin_center = th1_input.GetBinCenter(i)

        the_bin = i
        if (do_shift):
            # Move the left half to the right of the right half
            # Even  e.g. with 6 bins, first right bin is 4
            if (this_nbin%2 == 0):
                if (bin_L_edge < 0.0):
                    the_bin = i + central_bin -1
                    # e.g. 1,2,3 bins will be 4,5,6
                else:
                    the_bin = i - central_bin + 1
                    # e.g. 4,5,6 bins will be 1,2,3
            # Odd e.g. with 5 bins, center is 3
            elif (this_nbin%2 == 1):
                if (bin_center < 0.0):
                    the_bin = i + central_bin
                    # e.g. 1,2 bins will be 4,5
                else:
                    the_bin = i - central_bin + 1
                    # e.g. 3,4,5 bins will be 1,2,3
                # Note in this case the distribution does not start at zero,
                # but at a negative number
        # Skip bins that are empty to avoid counting them as an entry
        # with zero value
        if (this_value != 0):
            h_tmp.SetBinContent(the_bin, this_value)
            h_tmp.SetBinError(the_bin, this_error)

    return h_tmp

def get_sparseproj1d_list(thnSparse, list_binstr, shift):
# Create list of phi 1d hist from thnSparse for each bin defined in
# list_binstr (list of bincodes)
    this_outlist = []
    template = ["Q","","Z","P"]
    template[1] = "N" if ("X" not in list_binstr[0]) else "X"

    # Remove integrated variables (not in bincode)
    for l,letter in enumerate(template):
        if letter not in list_binstr[0]:
            template[l] = ""

    # Run over all n-dimensional bins
    for bincode in list_binstr:
        for l,letter in enumerate(template):
            if not letter:
                continue

            # Get letter location and add 1 to get the number location
            # idx_letter = bincode.index(letter)
            # pos = int(bincode[idx_letter+1])
            # thnSparse.GetAxis(l).SetRange(pos+1, pos+1)
            vbin = get_bincode_varbin(bincode, letter)
            thnSparse.GetAxis(l).SetRange(vbin, vbin)
            # Note that if range is not changed, projection
            # will integrate over that axis!

        proj_tmp = thnSparse.Projection(4)
        proj_tmp.SetName("proj_tmp")
        final_name = thnSparse.GetName()+"_"+bincode
        this_hist = create_phi_hist(proj_tmp, final_name, shift)
        this_outlist.append(this_hist)
        proj_tmp.Delete()

    return this_outlist


################################################################################
##                            Fit method functions                            ##
################################################################################

def get_fit_method(cut_str, use_default = True):
# Return string with fit method string name
    str_fit = ""
    # Get list with internal names
    l_cuts = get_l_cuts(cut_str)

    error1_str = "More than one fit method selected.\n"\
                "  Please, choose only one (Ff -Full- is default)."
    unique = True
    for fmeth in l_fit_met:
        if (fmeth in l_cuts) and unique:
            str_fit = fmeth
            unique = False
        elif (fmeth in l_cuts) and not unique:
            error_msg("fit_method", error1_str)

    # In case no fit name was given and default is selected
    if unique and use_default:
        str_fit = "Ff"
        info_str = "No fit method introduced. Using Full as default."
        info_msg("fit_method", info_str)

    return str_fit

def get_fit_shortmethod(this_method, fname):
# Return new short-name for method to be used in the name of a file
    # In principle, the initial letter should be enough
    this_ext = this_method[0]

    # We want to differenciate between Left and Right
    if (this_method=="LR") and ("R" in fname):
        this_ext = "R"
    # Since Fold and Full have the same initial, A stands for All in Full
    elif (this_method=="Ff"):
        this_ext = "A"

    return this_ext


################################################################################
##                            Extract x-axis info                             ##
################################################################################

def get_xaxis(cut_str):
# Return str with short-name of the xaxis used
# Remember: integrated variables are given by nDim
    this_xax = ""

    # Get list with internal names
    l_cuts = get_l_cuts(cut_str)

    unique = True
    for x in l_cut_xaxis:
        if (x in l_cuts) and unique:
            this_xax = x
            unique = False
        elif (x in l_cuts) and not unique:
            error_msg("xaxis", "Only one variable is supported! Try Zx or Px.")

    return this_xax

def get_var_init(my_str, is_cut):
# Get initial of the str given
    my_var = get_xaxis(my_str) if is_cut else my_str
    if my_var in d_var_initial:
        my_init = d_var_initial[my_var]
    else:
        error_msg("bincode", "Initial letter for code not found :(.")

    return my_init


################################################################################
##                        *OLD* Paths and directories                         ##
################################################################################

def enum_folder(mypath):
# Adds a sequential number to the path
    # Remove end slash and last digit
    if mypath[-1] == "/":
        mypath = mypath[0:-1]
    if (mypath[-1] == "0") or (mypath[-1] == "1"):
        mypath = mypath[0:-1]

    count = 1
    mypath+="1"
    # Rename until file number is not found
    while(os.path.exists(mypath)):
        # Remove number at the end
        idx = len(str(count))
        count+=1
        mypath = mypath[0:-idx] + str(count)

    os.makedirs(mypath)
    return mypath

def create_folder(outdir, title = "", overwrite = False, enumerate = False):
# Create folder: outdir/title. Enumerate will add a number at the end.
    outpath = outdir
    if title:
        outpath = os.path.join(outdir,title)

    exists = os.path.exists(outpath)
    if exists and not enumerate:
        msg = "already exists."
        if (not overwrite):
            msg+= " Not overwritten!"
            error_msg("Create_folder", "%s %s"%(outpath, msg))
        else:
            msg+= " Recreating!"
    else:
        if enumerate:
            outpath = enum_folder(outpath)
        else:
            os.makedirs(outpath)
        msg = "created."

    info_msg("myStyle", "%s %s"%(outpath, msg))
    return outpath


################################################################################
##                                Define style                                ##
################################################################################

def force_style(use_colz = False):
# Define Style for plots with uniform margins and text format
# use_colz option gives a special margin set to see the color bar
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptFit(1011)

    ROOT.gStyle.SetPadTopMargin(marg)    #0.05
    ROOT.gStyle.SetPadRightMargin(marg)  #0.05
    ROOT.gStyle.SetPadBottomMargin(2*marg)  #0.16
    ROOT.gStyle.SetPadLeftMargin(2*marg)   #0.16

    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)

    ROOT.gStyle.SetTextFont(font)
    ROOT.gStyle.SetLabelFont(font,"x")
    ROOT.gStyle.SetTitleFont(font,"x")
    ROOT.gStyle.SetLabelFont(font,"y")
    ROOT.gStyle.SetTitleFont(font,"y")
    ROOT.gStyle.SetLabelFont(font,"z")
    ROOT.gStyle.SetTitleFont(font,"z")

    ROOT.gStyle.SetTextSize(tsize)
    ROOT.gStyle.SetLabelSize(tsize-9,"x")
    ROOT.gStyle.SetTitleSize(tsize-3,"x")
    ROOT.gStyle.SetLabelSize(tsize-9,"y")
    ROOT.gStyle.SetTitleSize(tsize-3,"y")
    ROOT.gStyle.SetLabelSize(tsize-9,"z")
    ROOT.gStyle.SetTitleSize(tsize-3,"z")

    ROOT.gStyle.SetLegendFont(font)
    ROOT.gStyle.SetLegendTextSize(tsize)
    ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gStyle.SetLegendFillColor(0)

    ROOT.gStyle.SetTitleXOffset(1.0)
    ROOT.gStyle.SetTitleYOffset(1.0)
    ROOT.gStyle.SetOptTitle(0)
    # ROOT.gStyle.SetOptStat(0)

    ROOT.gStyle.SetHistLineWidth(4)

    ROOT.gStyle.SetGridColor(921)
    ROOT.gStyle.SetGridStyle()

    # Move exponent in y-axis to the left
    ROOT.TGaxis.SetExponentOffset(-0.07, 0.0, "y")

    ROOT.gROOT.ForceStyle()

    if use_colz:
        ROOT.gStyle.SetPadRightMargin(2*marg)
        ROOT.gStyle.SetPadTopMargin(1.1*marg)
        ROOT.gStyle.SetLabelSize(tsize-10,"z")
        ROOT.gStyle.SetTitleYOffset(1.3)
        ROOT.gROOT.ForceStyle()

# TODO: Add a generalized padcenter
def get_padcenter(use_colz = False, mleft = 0, mright = 0):
# Return pad center value as ratio wrt total pad length
    center = 0.5 if use_colz else (1 + marg)/2

    return center

def create_canvas(cname = "cv"):
    canvas = ROOT.TCanvas(cname,"cv",1000,800)
    canvas.SetGrid(0,1)
    # gPad.SetTicks(1,1)
    ROOT.TH1.SetDefaultSumw2()
    ROOT.gStyle.SetOptStat(0)

    return canvas


################################################################################
##                          Header and top messages                           ##
################################################################################
# TODO: Add idea with new positions!

def draw_topL(text_bold = "", text = "", xl=0.0, yb=0.0):
# Draw text at top left corner of the pad, with reference point
# shifted to the right by xl and up by yb
    upLeft_text = ROOT.TLatex()
    upLeft_text.SetTextSize(tsize-4)
    href = 2*marg+0.005+xl
    vref = 1-marg+0.01+yb
    top_txt = "#bf{%s}"%(text_bold)
    if text:
        top_txt+= " %s"%(text)
    upLeft_text.DrawLatexNDC(href, vref, top_txt)

def draw_topR(text_bold = "", text = "", xr=0.0, yb=0.0):
# Draw text at top right corner of the pad, with reference point
# shifted to the left by xr and up by yb
    upRight_text = ROOT.TLatex()
    upRight_text.SetTextSize(tsize-4)
    upRight_text.SetTextAlign(31)
    href = 1-marg-0.005-xr
    vref = 1-marg+0.01+yb
    top_txt = "#bf{%s}"%(text_bold)
    if text:
        top_txt+= " %s"%(text)
    upRight_text.DrawLatexNDC(href, vref, top_txt)

def draw_preliminary(text = "", xl = 0.0, yb = 0.0,
                     lmarg = 2*marg, rmarg = marg,
                     bmarg = 2*marg, tmarg = marg):
# Draw top left label "Preliminary", with reference point shifted
# to the right by xl and up by yb
    # TODO: Write only the bold text at the top and add a new layer with the CLAS PRELIMINARY with Alpha~ 0.4 (opacity)
    preliminar_msg = ROOT.TLatex()
    preliminar_msg.SetTextSize(tsize+10)
    preliminar_msg.SetTextAlign(22)
    preliminar_msg.SetTextAngle(45)
    preliminar_msg.SetTextColor(ROOT.kGray)
    preliminar_msg.SetTextColorAlpha(ROOT.kGray, 0.4)
    xcenter = get_pad_center(lmarg, rmarg)
    ycenter = get_pad_center(bmarg, tmarg)
    preliminar_msg.DrawLatexNDC(xcenter, ycenter, "#bf{%s}"%("  CLAS preliminary  "*2))
    if text:
        draw_topL(text, xl=xl, yb=yb)

def draw_summary(text = "", xl=0.0, yb=0.0):
# Draw top left label "Summary", with reference point shifted
# to the right by xl and up by yb
    # draw_topL(text, "Summary", xl, yb)
    draw_topL(text, "", xl, yb)

def draw_targetinfo(target="X", fileType="SimOrData"):
# Draw top right label with target and "simulation" or "data" info
    if "targ" in target:
        draw_topR("%s, %s"%(target,fileType),"")
    else:
        draw_topR("%s target, %s"%(target,fileType),"")

def draw_bininfo(bin_name="A0B1", bin_type=0, xR=0, yT=0):
# Draw bin info such as: "0.1 GeV < nu < 1.0 GeV"
# below top text banner w.r.t. TopRight point (xR, yT)
    text = ROOT.TLatex()
    text.SetTextSize(tsize-4)
    text.SetTextAlign(33)
    title = get_bintxt(bin_name, bin_type)
    if (xR==0 and yT==0):
        text.DrawLatexNDC(1-marg-0.005,1-marg-0.01,title)
    else:
        text.DrawLatexNDC(xR,yT,title)

def get_bintxt(bin_name="A0B1", bin_type=0):
# Get text with bin info such as: "0.1 GeV < nu < 1.0 GeV" to be written using
# bin_name in bincode format and bin_type from the binning dictionary
    tmp_txt = ""

    this_dict = all_dicts[bin_type]
    list_letters = bin_name[0::2]
    list_numbers = bin_name[1::2]

    for l,letter in enumerate(list_letters):
        num_index = int(list_numbers[l]) # 0 , 1
        vmin = this_dict[letter][num_index] # 0 , 1
        vmax = this_dict[letter][num_index+1] # 1 , 2
        tmp_txt+="%.2f < %s < %.2f"%(vmin, axis_label(letter,'Latex'), vmax)
        if l<(len(list_letters)-1):
            tmp_txt+="; "

    return tmp_txt


################################################################################
##                            Markers and colors!                             ##
################################################################################

def rgb_to_root(r ,g ,b ):
# Translate color from RGB format to inner ROOT format
    this_color = ROOT.TColor.GetColor(r,g,b)
    return this_color

def get_color(color_blind = True):
# Get list with 7-color pallete (colorblind friendly by default)
    # [#kGreen+2, #kCyan+2, #kBlue, #kViolet, #kRed, #kYellow+2, #kBlue-3]
    list_color_regular = [416+2, 432+2, 600, 880, 632, 400+2, 600-3]

    # [indigo, cyan, green, olive, rose, wine]
    list_color_blind = [rgb_to_root(51,34,136), rgb_to_root(51,187,238),
                        rgb_to_root(17,119,51), rgb_to_root(153,153,51),
                        rgb_to_root(204,102,119), rgb_to_root(136,34,85),
                        rgb_to_root(128,128,128)]

    this_pallete = list_color_blind if color_blind else list_color_regular

    return this_pallete

def get_marker(filled = False):
# Get list with 6 shapes for markers, hollow by default
# [circle, square, triangle, diamond, star-inverse, inverse-triangle]
    marker_hollow = [24, 25, 26, 27, 30, 32]
    marker_filled = [20, 21, 22, 33, 29, 23]

    this_marker = marker_hollow if not filled else marker_filled

    return this_marker

# Dictionary with a color associated to each target
color_target = {'C': get_color()[0], 'Fe': get_color()[2],
                'Pb': get_color()[3], 'D': get_color()[4],
                'DC': get_color()[1], 'DFe': get_color()[5],
                'DPb': get_color()[6]}


################################################################################
##                          Binning and dictionaries                          ##
################################################################################

# Copy dictionaries of bins from Bins.py
all_dicts = list(bn.Bin_List)

# Short name of each kinematic variable of interest
d_var_initial = {
    "Q2":'Q', "Qx":'Q', "Q": 'Q', "Nu":'N', "Nx":'N', "N":'N',
    "Zh":'Z', "Zx":'Z', "Z":'Z', "Pt2":'P', "Pt":'P', "Px":'P', "P":'P',
    "Xb":'X', "Xx": 'X', "X": 'X', "PhiPQ":'I', "PQ":'I', "I": 'I',
}

# Dictionary with axis title per variable
#   <initial> : [<name>,    <axis_name_latex>,  <units>  ]
var_label = {
    'Q': ["Q2",     "Q^{2}",        "(GeV^{2})" ],
    'N': ["Nu",     "#nu",          "(GeV)"     ],
    'Z': ["Zh",     "Z_{h}",        ""          ],
    'P': ["Pt2",    "P_{t}^{2}",    "(GeV^{2})" ],
    'I': ["PhiPQ",  "#phi_{PQ}",    "(deg)"     ],
    'X': ["Xb",     "X_{b}",        ""          ],
}

def axis_label(var, text):
# Return str with text to be used as title for axis
# Usually, axis needs "LatexUnit"
    this_output = ""
    if ("Name" in text):
        this_output += var_label[var][0]
    if ("Latex" in text):
        if (this_output!=""):
            this_output+=" "
        this_output += var_label[var][1]
    if ("Unit" in text):
        if (this_output!=""):
            this_output+=" "
        this_output += var_label[var][2]

    return this_output
