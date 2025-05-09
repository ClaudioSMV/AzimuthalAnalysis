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

def only_one_element_msg(list_elements, stage_title, stage_text,
                         example = "", show_wrong_input = False,
                         empty_2nd_bool = True, default_value = "",
                         is_error = False):
    # Send warning only if there is a default value
    if (not list_elements) and default_value:
        msg = "No %s introduced. "%(stage_text)
        msg+= "Using %s as default!"%(default_value)
        is_error = False
    # Break if no element in list
    elif (not list_elements) and empty_2nd_bool:
        msg = "Choose one %s."%(stage_text)
        if example:
            msg+= " Ex. %s"%(example)
    # Break if more than one element in list
    elif len(list_elements) > 1:
        msg = "Only ONE %s is supported!"%(stage_text)
        if show_wrong_input:
            msg+= " You introduced %s."%(list_elements)
        if example:
            msg+= " Ex. %s."%(example)

    # Print message
    if (not list_elements) or (len(list_elements) > 1):
        if is_error:
            error_msg(stage_title, msg)
        else:
            info_msg(stage_title, msg)

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
d_cuts_legend.update(d_cut_leg_fit)
d_cuts_legend.update(d_cut_leg_sum)
d_cuts_legend.update(d_cut_leg_tar)
d_cuts_legend.update(d_fit_leg_met)


######################  List with cuts in correct order  #######################
l_cut_tar = ["sl", "lq",]
l_fit_met = ["Sh", "Fd", "LR", "Ff",]
l_cut_acc = ["Xf", "XT", "DS", "BS", "PF", "MM", "M2",]
l_cut_cor = ["FE", "AQ", "Pe",]
l_cut_fit = ["Fs", "NP", "Nm",]
l_cut_sum = ["MD",]

l_cuts = []
l_cuts.extend(l_cut_tar)
l_cuts.extend(l_fit_met)
l_cuts.extend(l_cut_acc)
l_cuts.extend(l_cut_cor)
l_cuts.extend(l_cut_fit)
l_cuts.extend(l_cut_sum)


def get_list_summary_targets(cut_str, get_legend = False):
# Return list with targets used in liquid or solid set
    d_lists = {"sl": ["C", "Fe", "Pb"], "lq": ["DC", "DFe", "DPb"]}

    # Get list with internal names
    list_cuts = get_list_cuts_short(cut_str)
    # Create list with "sl" or "lq" if existing
    list_target_set = [tar for tar in list_cuts if tar in d_lists]
    only_one_element_msg(list_target_set, "Target-set summary", "set of targets",
                         example="Solid (sl) or liquid (lq)", is_error=True)
    target_set = list_target_set[0]
    output = d_lists[target_set] if not get_legend else d_cut_leg_tar[target_set]

    return output


################################################################################
##                                Format cuts                                 ##
################################################################################

def get_list_cuts_short(initial_cut_str):
# Transform initial string with selected cuts into a list using the
# internal/short names
    list_cuts = initial_cut_str.split("_")
    # Remove empty elements
    while("" in list_cuts):
        list_cuts.remove("")

    # Update list_cuts to have only internal/short names
    list_short = []
    for cut in list_cuts:
        # Check if the cut name is in the dictionary with all the possible
        # names and variations of existing cuts
        if cut in d_cuts:
            list_short.append(d_cuts[cut])
        # Send error if the cut is NOT the bin info (non-integrated vars)!
        elif not check_vars_format(cut):
            err_txt = "\"%s\" cut not found in any list."%(cut)
            error_msg("Cut", err_txt)
        # Or add in case it IS the bin info
        else:
            list_short.insert(0, cut)
    # Remove repeated elements if existing
    list_cuts = list(set(list_short))

    return list_cuts

def get_cut_final(initial_str = "", stage = "", is_output = False):
# Obtain final string with cuts following a specific order according to
# the stage we are (Correction, Fit, Closure Test, etc.) or following a
# different convention (defined for /output/)
# initial_str should be like "Aa_Bb_Cccc"
    stage = stage.lower()
    # Select summary stage if using one of these names
    if ("asymmetry" in stage) or ("ratio" in stage):
        stage = "summary"
    # Create "reference list" (ref_list) with ALL the existing cuts in order
    ref_list = list(l_cuts)
    # Create "forbidden list" (unwanted_cuts) with cuts that are not possible
    # at this stage or in output
    unwanted_cuts = []
    if is_output:
        # Omit all cuts coming after processing (i.e. from correction and later)
        unwanted_cuts.extend(l_cut_tar)
        # unwanted_cuts.extend(l_cut_xaxis)
        unwanted_cuts.extend(l_fit_met)
        unwanted_cuts.extend(l_cut_fit)
        unwanted_cuts.extend(l_cut_sum)
        if "acc" in stage:
            unwanted_cuts.extend(l_cut_cor)
    elif (not is_output) and ("closure" in stage):
        # Omit all cuts that are not part of Closure test
        unwanted_cuts.extend(l_cut_tar)
        unwanted_cuts.extend(l_fit_met)
        unwanted_cuts.extend(l_cut_fit)
        unwanted_cuts.extend(l_cut_sum)
        unwanted_cuts.remove("Sh")
    else:
        higher_stage = False
        if ("acc" in stage) or higher_stage:
            unwanted_cuts.extend(l_cut_cor)
            # unwanted_cuts.extend(l_cut_xaxis)
            higher_stage = True
        if ("corr" in stage) or higher_stage:
            unwanted_cuts.extend(l_cut_fit)
            unwanted_cuts.extend(l_fit_met)
            if not higher_stage:
                unwanted_cuts.remove("Sh")
            higher_stage = True
        if ("sum" not in stage) or higher_stage:
            unwanted_cuts.extend(l_cut_tar)
            unwanted_cuts.extend(l_cut_sum)
            higher_stage = True
    # Remove duplicated cuts if existing
    unwanted_cuts = list(set(unwanted_cuts))
    # Remove selected elements from reference, thus using
    # the "real" reference of this stage
    for ucut in unwanted_cuts:
        ref_list.remove(ucut)

    # Get list with cuts inserted (this uses the internal/short names)
    list_inserted_cuts = get_list_cuts_short(initial_str)

    # Remove input cuts that don't apply at this stage
    wrong_stage = [icut for icut in unwanted_cuts if icut in list_inserted_cuts]
    for ucut in wrong_stage:
        list_inserted_cuts.remove(ucut)
    if wrong_stage:
        inf_txt = "Cuts not used at this stage: %s."%(wrong_stage)
        info_msg("Input-cut", inf_txt)

    # Save list with final-name cuts in the reference order
    list_final_cuts = []
    for possible_cut in ref_list:
        if possible_cut not in list_inserted_cuts:
            continue
        final_name = d_cuts_final[possible_cut]
        if is_output:
            # If in /output/ use the correct dictionary
            final_name = d_cuts_output[possible_cut]
        list_final_cuts.append(final_name)
        list_inserted_cuts.remove(possible_cut)

    # Select the non-integrated variables ("bins of")
    if not is_output:
        vs_x_format = True if ("sum" in stage) else False
        temp_cut_str = "_".join(list_inserted_cuts)
        vars_set = get_non_integrated_vars(temp_cut_str, warn_bad_format=True,
                                           versus_x_format=vs_x_format)
        list_final_cuts.insert(0, vars_set)
    # Remove non-integrated variables ("bins of") from the list
    for cut in list(list_inserted_cuts):
        if check_vars_format(cut):
            list_inserted_cuts.remove(cut)

    # Send a warning if at least one inserted cut is still not used
    # (i.e. it's not in the reference list, it's not vars info, etc)
    if list_inserted_cuts:
        inf_txt = "Elements not used as cuts: %s."%(list_inserted_cuts)
        info_msg("Cut", inf_txt)

    # Return final-name cuts in the reference order as a single string
    final_str = "_".join(list_final_cuts)
    return final_str

def cut_is_included(cut_name, full_str):
# Check if cut_name is part of the full_str input
    # Get list with internal names
    list_cuts = get_list_cuts_short(full_str)
    # Get cut_name in internal/short form
    cut_name = d_cuts[cut_name]
    is_included = (cut_name in list_cuts)

    return is_included

def get_non_integrated_vars(cut_str, warn_bad_format = False, versus_x_format = False,
                            return_original_name = False):
# Return string with the non-integrated variables in the format required
    # Get list with internal names
    list_cuts = get_list_cuts_short(cut_str)
    # Create list with all cuts introduced if existing
    list_vars_set = [cut for cut in list_cuts if check_vars_format(cut, warn_bad_format)]
    only_one_element_msg(list_vars_set, "Input-vars", "list of vars",
                         example="bQNZ", is_error=True, show_wrong_input=True)

    set_of_variables = format_non_integrated_vars(list_vars_set[0],
                                                versus_x_format=versus_x_format)
    if return_original_name:
        set_of_variables = list_vars_set[0]

    return set_of_variables

def check_vars_format(single_str, warn_bad_format = False):
# Check if single_str has the correct format of non-integrated vars (ex. bQNZ)
    # Make sure the format is correct
    good_format = (single_str[0] is "b")
    if good_format:
        # Confirm all remaining letters are valid vars
        for letter in single_str[1:]:
            if letter not in var_label:
                good_format = False
        if (not good_format) and warn_bad_format:
            msg_txt = "Wrong non-integrated vars format \"%s\""%(single_str)
            info_msg("Bin_vars", msg_txt)
    elif warn_bad_format:
        msg_txt = "Cut is not vars-related, wrong format! (%s)"%(single_str)
        info_msg("Bin_vars", msg_txt)

    return good_format

def format_non_integrated_vars(single_str, versus_x_format= False):
# Return single_str with the format required (bQZN-->QNZ or bQPZ-->QvPxZ)
    formatted_str = ""
    # Maintain order given and add extra info of VS and x-axis (for Summary)
    if versus_x_format:
        # Transforms QZ --> QxZ; ZP --> ZxP (bins of Z and function of P)
        formatted_str = "%sx%s"%(single_str[-2], single_str[-1])
        # If there is one letter before, then QNZ --> QvNxZ; QZP --> QvZxP
        # Which means: 2d bins of Q and Z, as function of P, for instance
        if len(single_str[1:]) == 3:
            formatted_str = "%sv%s"%(single_str[1], formatted_str)
    # Else change single_str to use default order [Q,N,X,Z,P]
    else:
        for letter in ["Q","N","X","Z","P"]:
            if letter not in single_str[1:]:
                continue
            formatted_str+= letter
    kinematic_vars = str(formatted_str)

    return kinematic_vars


################################################################################
##                      Bincode and variables' functions                      ##
################################################################################

def get_bins_limits(nbin, init):
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
    for var in initials:
        this_bin = len(all_dicts[nbin][var]) - 1
        nbins[var] = this_bin

    return nbins

def get_bincode_info(nbin, cut_str):
# Returns non-integrated variables, each number of bins, and their limits
    # Get non-integrated variable set
    vars_set = get_non_integrated_vars(cut_str)
    # Get number of bins of each non-integrated variable
    dictionary_nbins_per_var = get_bincode_nbins_dict(nbin, vars_set)
    # Get list of bin limits of each non-integrated variable
    dictionary_limits_per_var = {var: get_bins_limits(nbin, var) for var in vars_set}

    return vars_set, dictionary_nbins_per_var, dictionary_limits_per_var

def get_bincode_list(nbin, cut_str):
# Create list with all bincode combinations of the nbin configuration given
    # Retrieve bins info of the non-integrated variables selected
    vars_set, dict_nbins, _ = get_bincode_info(nbin, cut_str)

    # Go over sorted non-integrated variables set to fill output_list
    output_list = [""]
    for var in vars_set:
        var_nbins = dict_nbins[var]

        # Create a temporary list with the indices associated to this variable only
        list_idx_this_var = []
        for i in range(0, var_nbins):
            str_bin = str(var) + str(i)
            list_idx_this_var.append(str_bin)

        # Update output extending current elements with the new variable info
        new_list_first_idx = len(output_list)
        for str_var in list(output_list):
            for str_idx in list(list_idx_this_var):
                output_list.append(str_var + str_idx)

        # Remove old (incomplete) elements from the list
        output_list = output_list[new_list_first_idx:]

    # Elements should be sorted, but re-sorting just in case!
    output_list.sort()

    # Output in the form ["Q0N0Z0", "Q0N0Z1", ..., "Q3N3Z9"]
    return output_list

def get_bincode_varidx(bincode, var_initial):
# Get number of the bin that the variable <init> has in the bincode given
# ex. in "Q0N2Z4", init="Z" will return 4, and init="Q" will return 0
    # Make sure initial is actually the correct initial
    var_initial = d_var_initial[var_initial]
    # Get position of the first digit after the requested initial
    n1 = bincode.index(var_initial) + 1
    # Get position of the last digit
    n2 = int(n1)
    imax = len(bincode) - 1
    while(bincode[n2].isdigit()):
        if n2 == imax:
            break
        n2+= 1
    # Extract index and transform into an int
    number_idx = int(bincode[n1:]) if n2 == imax else int(bincode[n1: n2])

    return number_idx


################################################################################
##                         Histograms and projections                         ##
################################################################################

def copy_histogram_phiPQ(th1, new_name, shift_center = False):
# Create a copy of a 1d projection of phi_PQ. By default, x-axis limits
# are [-180, 180], but <shift_center> change them to [0, 360]
    # General variables ([-180, 180] always, but retrieving just in case)
    xmin = th1.GetXaxis().GetXmin() # -180.
    xmax = th1.GetXaxis().GetXmax() #  180.
    nbins = th1.GetNbinsX()

    # Redifine limits if shifting center
    if (shift_center):
        # Set limits to be [0, 360]. If required, slightly change these numbers
        # so that the position of the bins is correct
        central_bin = th1.FindBin(0.0)
        left_edge = th1.GetBinLowEdge(central_bin)
        xmin = 0.0 + left_edge
        xmax = 360. + left_edge

    axis_name = ";%s;Counts"%(axis_label('I',"LatexUnit"))
    hist_phiPQ = ROOT.TH1D(new_name, axis_name, nbins, xmin, xmax)

    # Fill histogram bin by bin
    for i in range(1, nbins+1):
        value = th1.GetBinContent(i)
        error = th1.GetBinError(i)

        bin_phiPQ = i
        if (shift_center):
            # Move bins of the first half after the second half
            if i < central_bin:
                bin_phiPQ = i + (nbins - central_bin) + 1
            # And vice versa
            else:
                bin_phiPQ = i - central_bin + 1

        # Skip bins that are empty to avoid counting them as a zero value entry
        if (value != 0):
            hist_phiPQ.SetBinContent(bin_phiPQ, value)
            hist_phiPQ.SetBinError(bin_phiPQ, error)

    return hist_phiPQ


def create_sparse_1Dprojection(thSparse, bincode, shift = False):
    # ["Q","N" or "X","Z","P"]
    variables = ["Q","N","Z","P"]
    if ("X" in bincode):
        variables[1] = "X"

    # Set bins per axis
    for i,var in enumerate(variables):
        if var not in bincode:
            continue
        # Get bin number of non-integrated variables (+1 because of convention)
        var_bin = get_bincode_varidx(bincode, var) + 1
        # Change range to get a single bin in a non-integrated variable
        # If not changed, the variable is integrated!
        thSparse.GetAxis(i).SetRange(var_bin, var_bin)

    # Make projection over PhiPQ
    projection = thSparse.Projection(4)
    projection.SetName("projection_temp")
    final_name = "%s_%s"%(thSparse.GetName(), bincode)

    # Create a copy of the projection
    histogram_phiPQ = copy_histogram_phiPQ(projection, final_name, shift)
    projection.Delete()

    return histogram_phiPQ


################################################################################
##                            Fit method functions                            ##
################################################################################

def get_fit_method(cut_str, use_default = True, show_warn = True):
# Return string with fit method introduced in cut_str
    # Get list with internal names
    list_cuts = get_list_cuts_short(cut_str)
    # Create list with all cuts introduced if existing
    list_fits = [cut for cut in list_cuts if cut in l_fit_met]
    if show_warn:
        only_one_element_msg(list_fits, "fit_method", "fit method",
                             is_error=True, show_wrong_input=True,
                             default_value="Ff")
    # If no fit method is introduced use default if selected
    if (not list_fits) and use_default:
        list_fits.append("Ff")

    fit_selected = list_fits[0] if list_fits else ""

    return fit_selected

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
# Return initial of the xaxis used
    # Get list with internal names
    list_cuts = get_list_cuts_short(cut_str)
    # Create list with all of the cuts with the correct non-integrated format
    list_variables = [niv for niv in list_cuts if check_vars_format(niv)]
    only_one_element_msg(list_variables, "xaxis", "x-axis selection",
                         is_error=True, show_wrong_input=True, example="QNZ")

    # Return x-axis variable only
    x_axis = format_non_integrated_vars(list_variables[0], versus_x_format=True)[-1]

    return x_axis

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

def change_margins(get=False, mtop=marg, mright=marg, mbot=2*marg, mleft=2*marg):
# Define new margins and get their values if needed
    ROOT.gStyle.SetPadTopMargin(mtop)
    ROOT.gStyle.SetPadRightMargin(mright)
    ROOT.gStyle.SetPadBottomMargin(mbot)
    ROOT.gStyle.SetPadLeftMargin(mleft)
    ROOT.gROOT.ForceStyle()
    # Return margin values only if needed
    if get:
        return [mtop, mright, mbot, mleft]

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
    preliminar_msg = ROOT.TLatex()
    preliminar_msg.SetTextSize(tsize+10)
    preliminar_msg.SetTextAlign(22)
    preliminar_msg.SetTextAngle(45)
    preliminar_msg.SetTextColor(ROOT.kGray)
    preliminar_msg.SetTextColorAlpha(ROOT.kGray, 0.4)
    xcenter = get_pad_center(lmarg, rmarg)
    ycenter = get_pad_center(bmarg, tmarg)
    msg = "#bf{%s}"%("  CLAS preliminary  "*2)
    preliminar_msg.DrawLatexNDC(xcenter, ycenter, msg)
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

def draw_bininfo(bin_name="A0B1", bin_type=0, xR=0, yT=0,
                 lmarg = 2*marg, rmarg = marg,
                 bmarg = 2*marg, tmarg = marg):
# Draw bin info such as: "0.1 GeV < nu < 1.0 GeV"
    text = ROOT.TLatex()
    text.SetTextSize(tsize-4)
    title = get_bincode_explicit_range(bin_name, bin_type)

    # Draw w.r.t. center or TopRight point (xR, yT)
    align = 23 if not xR else 33
    text.SetTextAlign(align)
    xcenter = get_pad_center(lmarg, rmarg) if not xR else xR
    ycenter = 1 - tmarg - 0.02 if not yT else yT

    text.DrawLatexNDC(xcenter, ycenter, title)

def get_bincode_explicit_range(bincode, nbin):
# Get formatted side text according to nbin limits
# Ex. "N0" -> "0.1 GeV < nu < 1.0 GeV"
    side_text = []
    variables = ["Q","N","Z","P"]
    if ("X" in bincode):
        variables[1] = "X"

    dictionary_limits = all_dicts[nbin]
    for var in variables:
        if var not in bincode:
            continue
        idx = get_bincode_varidx(bincode, var)
        value_min = dictionary_limits[var][idx]
        value_max = dictionary_limits[var][idx + 1]
        var_latex = axis_label(var, 'Latex')
        info = "%.2f #leq %s < %.2f"%(value_min, var_latex, value_max)
        side_text.append(info)
    side_text = "; ".join(side_text)

    return side_text

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
