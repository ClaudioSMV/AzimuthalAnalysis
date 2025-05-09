
from lib_error import error_msg, info_msg, check_list_has_one_element
from lib_constants import cuts_StoL, ordered_cuts_per_stage, cuts_StoL_processed_files,\
    ordered_stages, variable_info, available_targets, get_variables_order
from Bins import Bin_List
# TODO: Update Bin list to use csv files


                                    #################
######################################  Functions  #######################################
######################################    Cuts     #######################################
                                    #################

def get_ordered_cuts_dictionary():
    return {name: list_of_cuts for (name, list_of_cuts) in ordered_cuts_per_stage}

def clean_cuts_input(cut_str):
# Remove repeated cuts and empty elements from input
    list_input_cuts = [cut for cut in cut_str.split("_") if cut] # Skip empty elements
    list_of_tags = []
    for cut in list_input_cuts:
        cut_tag = cut
        if cut in cuts_StoL.values():
            cut_tag = [key for key, val in cuts_StoL.items() if val == cut][0]
        if cut_tag in list_of_tags: # Avoid repeated elements
            continue
        list_of_tags.append(cut_tag)
    
    return list_of_tags

def check_valid_cuts(input_cuts):
# Check introduced cuts are listed in "cuts_StoL"
    if input_cuts and check_binvars_input_format(input_cuts[0]):
        input_cuts.remove(input_cuts[0])
    undefined_cuts = [cut for cut in input_cuts if cut not in cuts_StoL]
    if undefined_cuts:
        err_txt = "Unknown cuts: %s"%(undefined_cuts)
        error_msg("check_valid_cuts", err_txt)

def cuts_list_short(input_cuts, include_binvars = True, check_cuts_validity = False):
# Return a list with internal/short names
    if isinstance(input_cuts, list):
        return input_cuts
    input_cuts = clean_cuts_input(input_cuts)

    for (i, element) in enumerate(input_cuts): # Move non-integrated variable forward
        if not check_binvars_input_format(element):
            continue
        if include_binvars:
            input_cuts.insert(0, input_cuts.pop(i))
        else:
            input_cuts.remove(element)
        break

    if check_cuts_validity:
        check_valid_cuts(input_cuts)

    return input_cuts

def get_ordered_cuts_at_this_stage(this_stage, only_this_stage = False):
# Return list with possible cuts usable in this stage
    list_of_cuts = [[] for _ in range(len(ordered_cuts_per_stage))]

    for stage in ordered_stages:
        if only_this_stage and (this_stage not in stage):
            continue
        for (i, entry) in enumerate(ordered_cuts_per_stage):
            stage_name, stage_cuts = entry
            if stage in stage_name:
                list_of_cuts[i] = stage_cuts # Add this way to preserve order of cuts
        if (stage == this_stage):
            break

    return [cut for cuts_in_stage in list_of_cuts for cut in cuts_in_stage]

def get_output_cuts(input_cuts, stage, processed_files = False, use_cut_tags = False):
# Return string with all cuts selected in the correct order according to the stage
    if ("Asymmetry" in stage) or ("Ratio" in stage): # To handle summary macros
        stage = "Summary"
    input_cuts = cuts_list_short(input_cuts, include_binvars=False)
    template_ordered_cuts = get_ordered_cuts_at_this_stage(stage)
    final_cut_tags = [cut for cut in template_ordered_cuts if cut in input_cuts]
    unused_cuts = [cut for cut in input_cuts if cut not in template_ordered_cuts]
    if unused_cuts:
        if not use_cut_tags: # Short names are used internally, thus warnings are avoided
            inf_txt = "Unused cuts at this stage: %s."%(unused_cuts)
            info_msg("get_output_cuts", inf_txt)

    if processed_files: # Use names given in the processed files
        return "_".join([cuts_StoL_processed_files[cut] for cut in final_cut_tags])

    final_names = final_cut_tags
    if not use_cut_tags: # Use long names
        final_names = [cuts_StoL[cut] for cut in final_cut_tags]
    binvars = get_binvars_from_cuts(input_cuts, True, versus_x_format=(stage=="Summary"))
    if not binvars: # Post-processed plots MUST HAVE binning info!
        error_msg("get_output_cuts", "Missing binvars (non-integrated variables.)")
    final_names.insert(0, binvars)

    return "_".join(final_names)

def check_cut_is_included(cuts_to_check, input_cuts):
# Check if a cut (or list of cuts) is part of the input cuts
    if isinstance(cuts_to_check, str):
        cuts_to_check = [cuts_to_check]
    check_valid_cuts(cuts_to_check)
    input_cuts = cuts_list_short(input_cuts)
    is_in_list = [(cut in input_cuts) for cut in cuts_to_check]

    return is_in_list[0] if len(is_in_list) == 1 else is_in_list

                        ##########################################
##########################               Functions              ##########################
##########################  Non-integrated variables (binvars)  ##########################
                        ##########################################

def check_binvars_input_format(single_str, warn_bad_format = False):
# Check format of non-integrated variable (starts with "b") (ex. bQNZ)
    good_format = (single_str[0] is "b") # Make sure the format is correct
    if good_format:
        for letter in single_str[1:]: # Confirm all remaining letters are valid vars
            if letter not in variable_info:
                good_format = False
    if warn_bad_format and (not good_format):
        msg_txt = "Wrong format: %s"%(single_str)
        info_msg("check_vars_format", msg_txt)

    return good_format

def format_output_binvars(binvars, versus_x_format = False, check_format = True):
# Returns non-integrated variable (binvars) formatted (bQZN-->QNZ or bQPZ-->QvPxZ)
    if check_format and not check_binvars_input_format(binvars, warn_bad_format = True):
        return False

    # Use especial format: QZ --> QxZ; (bins of Q and function of Z)
    #                      QNZ --> QvNxZ; (2d bins of Q and N, as function of P)
    if versus_x_format:
        if len(binvars) == 4:
            formatted_str = "%sv%sx%s"%(binvars[1], binvars[2], binvars[3])
        else:
            formatted_str = "%sx%s"%(binvars[-2], binvars[-1])
    else: # If not format required, use default order [Q,N,X,Z,P]
        formatted_str = get_variables_order(binvars, use_only_reference=True)

    return str(formatted_str)

def get_binvars_from_cuts(full_cut_str, use_output_format, versus_x_format = False):
# Returns non-integrated variables string with/without format
    list_cuts = cuts_list_short(full_cut_str, include_binvars=True)
    binvars = [item for item in list_cuts if check_binvars_input_format(item)]
    if not binvars:
        return ""
    binvars = binvars[0] # Choose one and only one set of variables
    if use_output_format:
        return format_output_binvars(binvars, versus_x_format)

    return binvars[1:] # Remove initial "b" used in the format

                                     #################
#######################################  Functions  ######################################
#######################################   Bincode   ######################################
                                     #################

def get_variable_binning_limits(nbin, initial):
# Create dictionary with list of bins limits for each variable
    dictionary_with_limits = list(Bin_List)[nbin]

    return dictionary_with_limits[initial]

def generate_combinations(variables, limits):
# Create list with all combinations of indices for bincode
    counters = {char: 0 for char in variables}
    results = []
    finished = False
    while not finished:
        combo = "".join("%s%i"%(char, counters[char]) for char in variables)
        results.append(combo)
        for i in reversed(range(len(variables))):
            char = variables[i]
            counters[char] += 1
            if counters[char] < limits[char]:
                break
            counters[char] = 0
            if i == 0:
                finished = True

    return results

def create_dictionary_of_bincode_nbins(nbin, cut_str):
# Return dictionary with number of bins for this configuration
    binvars = get_binvars_from_cuts(cut_str, False)
    nbins_per_var = {}
    for var in binvars:
        binvars_limits = get_variable_binning_limits(nbin, var)
        nbins_per_var[var] = len(binvars_limits) - 1

    return nbins_per_var

def get_list_of_bincodes(info_tag, cut_str):
# Returns list with all possible bincodes for this configuration ["Q0N0Z0", "Q0N0Z1", ...]
    binvars = get_binvars_from_cuts(cut_str, False)
    nbin = get_info_tag_dictionary(info_tag)["n_bin"]
    binvars_nbins = create_dictionary_of_bincode_nbins(nbin, cut_str)

    return generate_combinations(binvars, binvars_nbins)

def extract_indices_dict(bincode):
# Create dictionary with the indices associated to each variable in bincode
    result = {}
    current_char = ""
    current_number = ""
    for char in bincode:
        if char.isdigit():
            current_number += char
        else:
            if current_char and current_number:
                result[current_char] = int(current_number)
            current_char = char
            current_number = ""
    if current_char and current_number:
        result[current_char] = int(current_number)

    return result

                                    #################
######################################  Functions  #######################################
######################################   Info tag  #######################################
                                    #################

def check_info_tag_format(tag):
# Check info tag has the proper format: <target>_<nBin>_<nDim>
    list_with_info = tag.split("_")
    if not list_with_info:
        error_msg("check_info_tag_format", "No target nor binning information!")
    if list_with_info[0] not in available_targets:
        list_with_info.insert(0, "None")
    
    if (len(list_with_info) > 3):
        error_msg("check_info_tag_format", "Too many items! Format <targ>_<nBin>_<nDim>.")

    return list_with_info

def get_info_tag_dictionary(tag):
# Returns dictionary with the information of the tag, using intuitive names as keys
    list_with_info = check_info_tag_format(tag)
    list_of_keys = [["Target", "targ"], ["BinningType", "nBin", "n_bin"],
                    ["NDims", "nDim", "n_dim"]]
    info_dictionary = {}    
    for (i, keys) in enumerate(list_of_keys):
        if (len(list_with_info) > i):
            info = list_with_info[i] if (i == 0) else int(list_with_info[i])
        else:
            info = "?"
        for key in keys:
            info_dictionary[key] = info

    return info_dictionary

def get_info_tag__title_format(tag, use_dimension = True, omit_target = False):
# Returns tag with title format: "<targ>_<nBin>B<nDim>"
    dictionary = get_info_tag_dictionary(tag)

    title_format = "%s_%iB"%(dictionary["Target"], dictionary["nBin"])
    if omit_target:
        title_format = "%sB"%(dictionary["nBin"])
    if use_dimension and (dictionary["nDim"] != "?"):
        title_format += str(dictionary["nDim"])

    return title_format

def convert_info_tag_str_to_list(tag):
# Returns info tag, composed of Target, binning code, and binning dimension
    dictionary = get_info_tag_dictionary(tag)

    return dictionary["Target"], dictionary["n_bin"], dictionary["n_dim"]

                                    ###################
######################################   Functions   #####################################
######################################  Fit methods  #####################################
                                    ###################

def get_fit_method(full_cut_str, use_default = True, show_warn = True):
# Returns fit method called in cut input string
    list_of_cuts = cuts_list_short(full_cut_str, include_binvars=False)
    available_methods = get_ordered_cuts_dictionary()["FitMethod"]
    list_of_fits = [cut for cut in list_of_cuts if cut in available_methods]
    if (not list_of_fits) and use_default:
        list_of_fits.append("Ff")

    if show_warn:
        check_list_has_one_element(list_of_fits, "get_fit_method", is_error=True,
                                   default_value="Ff"*use_default)

    return list_of_fits[0] if list_of_fits else ""

def get_fit_method_short(fit_method, reference_name = ""):
# Returns a single character as short-tag for the fit method used
    initial = fit_method[0]
    # Some functions might need to differenciate between Left and Right
    if (fit_method == "LR") and ("R" in reference_name):
        initial = "R"
    # Since Fold and Full have the same initial, "A" stands for "All" in Full
    elif (fit_method == "Ff"):
        initial = "A"

    return initial

def get_fit_method_title(fit_method, is_LR_left = False):
    available_methods = get_ordered_cuts_dictionary()["FitMethod"]
    dictionary = {fit: cuts_StoL[fit] for fit in available_methods}
    title = dictionary[fit_method]
    if (title == "LR"):
        title = "Left" if is_LR_left else "Right"

    return title

