import sys
from lib_error import error_msg, info_msg, check_list_has_one_element
from lib_constants import cuts_StoL, ordered_cuts_per_stage, cuts_StoL_processed_files,\
    ordered_stages, variable_info, get_variables_order
from lib_dataset_info import get_info_tag_dictionary
from Bins import List_of_binning


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
    undefined_cuts = [cut for cut in input_cuts if cut not in cuts_StoL]
    if undefined_cuts:
        err_txt = "Unknown cuts: %s"%(undefined_cuts)
        error_msg("check_valid_cuts", err_txt)

def cuts_list_short(input_cuts, check_cuts_validity = False):
# Return a list with internal/short names
    if isinstance(input_cuts, list):
        return input_cuts
    input_cuts = clean_cuts_input(input_cuts)
    if check_cuts_validity:
        check_valid_cuts(input_cuts)

    return input_cuts

def available_cuts_at_this_stage(this_stage, only_this_stage = False):
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

def get_ordered_cuts_at_this_stage(stage, input_cuts):
# Return ordered lists of available and unused cuts at this stage
    input_cuts = cuts_list_short(input_cuts)
    template_ordered_cuts = available_cuts_at_this_stage(stage)
    final_cut_tags = [cut for cut in template_ordered_cuts if cut in input_cuts]
    unused_cuts = [cut for cut in input_cuts if cut not in template_ordered_cuts]

    return final_cut_tags, unused_cuts

def get_output_cuts(input_cuts, stage, processed_files = False, use_cut_tags = False,
                    warn_unused = False):
# Return string with all cuts selected in the correct order according to the stage
    final_cut_tags, unused_cuts = get_ordered_cuts_at_this_stage(stage, input_cuts)
    if warn_unused and unused_cuts:
        info_msg("get_output_cuts", "Unused cuts at this stage: %s."%(unused_cuts))
    if processed_files: # Use names given in the processed files
        if "Sh" in final_cut_tags: # Avoid error since dictionary has not shift included
            final_cut_tags.remove("Sh")
        return "_".join([cuts_StoL_processed_files[cut] for cut in final_cut_tags])
    final_names = final_cut_tags
    if not use_cut_tags: # Use long names
        final_names = [cuts_StoL[cut] for cut in final_cut_tags]

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

def check_binvars_are_ok(single_str):
# Check non-integrated variables exist (ex. QNZ)
    for letter in single_str: # Confirm all letters are valid variables
        if letter not in variable_info:
            error_msg("check_binvars_are_ok", "Wrong variables included: %s"%(single_str))

def format_output_binvars(binvars, versus_x_format = False):
# Return binvars in order and formatted (QZN -> QNZ or QPZ -> QvPxZ)
    check_binvars_are_ok(binvars)

    # Use especial format: QZ --> QxZ; (bins of Q and function of Z)
    #                      QNZ --> QvNxZ; (2d bins of Q and N, as function of P)
    if versus_x_format:
        if len(binvars) == 3:
            formatted_str = "%sv%sx%s"%(binvars[0], binvars[1], binvars[2])
        else:
            formatted_str = "%sx%s"%(binvars[-2], binvars[-1])
    else: # If not format required, use default order [Q,N,X,Z,P]
        formatted_str = get_variables_order(binvars, use_only_reference=True)

    return str(formatted_str)

                                     #################
#######################################  Functions  ######################################
#######################################   Bincode   ######################################
                                     #################

def get_variable_binning_limits(nbin, initial):
# Create dictionary with list of bins limits for each variable
    dictionary_with_limits = list(List_of_binning)[nbin]
    var = variable_info[initial][0]

    return dictionary_with_limits[var]

def generate_combinations(variables, dict_max_indices):
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
            if counters[char] < dict_max_indices[char]:
                break
            counters[char] = 0
            if i == 0:
                finished = True

    return results

def create_dictionary_binvars(nbin, binvars):
# Create dictionary with the limits and bins number for each variable in binvars
    dictionary = {}
    for var in binvars:
        limits = get_variable_binning_limits(nbin, var)
        dictionary[var] = {"Limits": limits, "Nbins": len(limits) - 1}

    return dictionary

def get_list_of_bincodes(info_tag, binvars):
# Returns list with all possible bincodes for this configuration ["Q0N0Z0", "Q0N0Z1", ...]
    nbin = get_info_tag_dictionary(info_tag)["n_bin"]
    binvars_info = create_dictionary_binvars(nbin, binvars)
    max_indices = {var: info["Nbins"] for (var, info) in binvars_info.items()}

    return generate_combinations(binvars, max_indices)

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

def create_bincode(dictionary):
    variables = [var for var in dictionary.keys() if var] # Skip empty elements
    ordered_variables = format_output_binvars(variables)
    listed_elements = [var + str(dictionary[var]) for var in ordered_variables]

    return "".join(listed_elements)
