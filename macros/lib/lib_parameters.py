from ROOT import TMath
from lib_naming import extract_histogram_info

def propagate_error_division(v1, e1, v2, e2, cov = 0):
# Propagate error using proper formula with covariance included
    r1 = e1 / v1
    r2 = e2 / v2
    error_value = TMath.Abs(v1 / v2) * TMath.Sqrt(r1**2 + r2**2 - 2 * cov / (v1 * v2))

    return error_value

def get_matrix_element(matrix, row, col):
# Return element in position row,col of matrix
    matrix_array = matrix.GetMatrixArray()
    index = col + matrix.GetNcols() * row

    return matrix_array[index]

def create_parameters_histograms(template, naming_obj, listed_reco_method, n_fits,
                                 n_parameters):
    histograms_to_fill = {}
    for i in range(n_fits):
        for j in range(n_parameters):
            for method in listed_reco_method:
                name = naming_obj.get_name_histogram(method, fit_idx=i,
                                                     fit_parameter_idx=j)
                histograms_to_fill[name] = template.Clone(name) # Bare parameters

                name_info = extract_histogram_info(name, has_fit_info=True)
                asymmetry_name = name.replace(name_info["Name"], "Asymmetry")
                histograms_to_fill[asymmetry_name] = template.Clone(asymmetry_name)

    return histograms_to_fill

def extract_fit_values(fit, parameter, is_asymmetry, covariance_matrix, prenormalized):
    value = fit.GetParameter(parameter)
    error = fit.GetParError(parameter)
    if is_asymmetry: # Modify parameter since asymmetry is defined as <cos\phi> = B/2A
        if prenormalized: # p1 = B/2piA, so we remove the pi factor and move to degrees
            value = 180. * value
            error = 180. * error
        else:
            value_p0 = fit.GetParameter(0)
            error_p0 = fit.GetParError(0)
            covariance = get_matrix_element(covariance_matrix, 0, parameter)
            error = propagate_error_division(value, error, value_p0, error_p0, covariance)
            value = value / (2. * value_p0)
            error = error / 2. # Error scales too

    return value, error
    
    # if ("Asymmetry" in name) and (not is_prenormalized):
    #     # Remember the factor 1/2 to match the definition!
    #     weight = 1./2
    #     # Get info of first parameter
    #     value0 = fit.GetParameter(0)
    #     error0 = fit.GetParError(0)
    #     cov = get_matrix_element(covariance_matrix, 0, p)
    #     # Get normalization
    #     asym_value = value/value0
    #     asym_error = propagate_error_division(value, error, value0, error0, cov)
    #     # Update final numbers with correct weights
    #     value = weight * asym_value
    #     error = weight * asym_error
    # elif ("Asymmetry" in name) and is_prenormalized:
    #     # Prenormalization gives p1 = B/2piA, so to be consistent with the
    #     # asymmetry definition a pi factor must be added
    #     # NOTE: The factor is transformed from \pi radians to 180. degrees
    #     # because the x-axis is given in degrees!
    #     value = 180. * value
    #     error = 180. * error

# def fill_parameters_histogram(histograms, fit, fit_idx, covariance_matrix,
#                    is_prenormalized = False):
#     # name = name_obj.name
#     # n_parameters = 
#     # function_idx = 0 if "R" in fit.GetName() else 1

#     # for histogram in histograms:
#     #     info = extract_histogram_info(histogram.GetName(), has_fit_info=True)
#     #     if (int(info["Fit_idx"]) != fit_idx):
#     #         continue
#     #     parameter = int(info["Par_idx"])

#     # for parameter in range(fit.GetNpar()):
#     #     new_name = 
#     #     histogram = histogram_template.Clone(new_name)

#     #     hname_pars = name_obj.get_hist_name_parameters(function_idx, par=p,
#     #                                                    show_bincode=False)
#     #     # # Create histograms if not in dictionary!
#     #     # if hname_pars not in dictionary_hist:
#     #     #     # Create histogram with bincodes in x-axis to fill with parameters
#     #     #     hist = create_bincode_histogram(hname_pars, list_bincodes)
#     #     #     dictionary_hist[hname_pars] = hist

#         # Get parameters and errors from fit
#         value = fit.GetParameter(p)
#         error = fit.GetParError(p)
#         # Modify parameter according to definition of asymmetry <cos\phi> = B/2A
#         if ("Asymmetry" in name) and (not is_prenormalized):
#             # Remember the factor 1/2 to match the definition!
#             weight = 1./2
#             # Get info of first parameter
#             value0 = fit.GetParameter(0)
#             error0 = fit.GetParError(0)
#             cov = get_matrix_element(covariance_matrix, 0, p)
#             # Get normalization
#             asym_value = value/value0
#             asym_error = propagate_error_division(value, error, value0, error0, cov)
#             # Update final numbers with correct weights
#             value = weight * asym_value
#             error = weight * asym_error
#         elif ("Asymmetry" in name) and is_prenormalized:
#             # Prenormalization gives p1 = B/2piA, so to be consistent with the
#             # asymmetry definition a pi factor must be added
#             # NOTE: The factor is transformed from \pi radians to 180. degrees
#             # because the x-axis is given in degrees!
#             value = 180. * value
#             error = 180. * error

#         # Get histogram and fill
#         histogram = dictionary_hist[hname_pars]
#         hbin = histogram.GetXaxis().FindBin(name_obj.bin_code)
#         histogram.SetBinContent(hbin, value)
#         histogram.SetBinError(hbin, error)
