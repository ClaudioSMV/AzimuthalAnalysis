from lib_error import error_msg, info_msg
from lib_constants import available_targets, reco_methods

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

                              ##############################
################################        Functions         ################################
################################  Reconstruction methods  ################################
                              ##############################

def format_reco_methods(use_all, format = "Analysis", add_raw = False):
    idx = ["Processed", "Analysis", "Title"].index(format)
    available_methods = []
    for (tag, names) in reco_methods:
        if (not add_raw) and (tag == "Raw"):
            continue
        elif (not use_all) and ("Match" in tag):
            continue
        available_methods.append(names[idx])

    return available_methods

def methods_under_use(input_histograms):
    available_methods = format_reco_methods(True, format="Analysis", add_raw=False)
    methods_used = []
    for name in input_histograms.keys():
        if not available_methods:
            break
        for method in available_methods:
            if method not in name:
                continue
            available_methods.remove(method)
            methods_used.append(method)
            break

    return methods_used
