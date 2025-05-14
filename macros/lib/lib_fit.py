from lib_error import error_msg, info_msg
from lib_constants import ordered_stages, fit_methods

                                    #################
######################################  Functions  #######################################
######################################   Fitting   #######################################
                                    #################

def fit_function_name(fit_method): # TODO: Change this to use fit_methods, and handle LR with "Sides"
    list_of_fit_names = ["crossSectionR"]
    if (fit_method == "LR"):
        list_of_fit_names.append("crossSectionL")

    return list_of_fit_names

def fit_matrix_name(naming_info, matrix_type, reco_method, bincode,
                    function_name = "crossSectionR"):
# Return name for matrix objects so that they are unique
    matrix_name = "M%s"%(matrix_type)
    fit_name_idx = fit_function_name(naming_info.fit_method).index(function_name)
    matrix_name += str(fit_name_idx)
    matrix_name += "_%s_%s"%(reco_method, bincode)

    return matrix_name


                                    ###################
######################################   Functions   #####################################
######################################  Fit methods  #####################################
                                    ###################

def check_fit_method_exists(method_name, stage):
    shift_exception = ((method_name == "Sh") and (stage == "Correction"))
    if (ordered_stages.index(stage) <= ordered_stages.index("Correction")):
        return "" if not shift_exception else "Sh" # Use shift in corrected distribution
    if method_name not in fit_methods:
        error_msg("check_fit_method_exists", "Non-existent fit method!")

    return method_name

def get_fit_name(method_tag):
    return fit_methods[method_tag]["Name"]

# def get_fit_method(full_cut_str, use_default = True, show_warn = True):
# # Returns fit method called in cut input string
#     list_of_cuts = cuts_list_short(full_cut_str)
#     available_methods = get_ordered_cuts_dictionary()["FitMethod"]
#     list_of_fits = [cut for cut in list_of_cuts if cut in available_methods]
#     if (not list_of_fits) and use_default:
#         list_of_fits.append("Ff")
#     if show_warn:
#         check_list_has_one_element(list_of_fits, "get_fit_method", is_error=True,
#                                    default_value="Ff"*use_default)

#     return list_of_fits[0] if list_of_fits else ""


# def get_fit_method_title(fit_method, is_LR_left = False):
#     available_methods = get_ordered_cuts_dictionary()["FitMethod"]
#     dictionary = {fit: cuts_StoL[fit] for fit in available_methods}
#     title = dictionary[fit_method]
#     if (title == "LR"):
#         title = "Left" if is_LR_left else "Right"

#     return title
