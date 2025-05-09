
from lib_cuts import get_cuts_final, get_fit_method, get_info_tag_dictionary,\
    get_info_tag__title_format, get_fit_method_title

BASEPATH = "./../"

                                    #################
######################################  Functions  #######################################
######################################   Fitting   #######################################
                                    #################

def fit_function_name(fit_method):
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

                             ###############################
###############################          Functions        ################################
###############################  Extract info from names  ################################
                             ###############################

def extract_histogram_info(hname, has_fit_info = False):
# Return dictionary with info using format: h(name)(f_idx)p(par_idx)_(acc_meth)_(bincode)
    list_of_characteristics = hname.split("_")
    dictionary = {
        "hname": list_of_characteristics[0][1:], # Exclude initial "h" in the name
        "hreco_method": list_of_characteristics[1],
    }
    if (len(list_of_characteristics) == 3):
        dictionary["hbincode"] = list_of_characteristics[2]
    if has_fit_info:
        dictionary["hname"] = list_of_characteristics[0][1:-3] # Exclude fit info
        dictionary["hfit_idx"] = list_of_characteristics[0][-3]
        dictionary["hpar_idx"] = list_of_characteristics[0][-1]
        dictionary["hname_Full"] = list_of_characteristics[0][1:] # Include fit info
        dictionary["hfit_info"] = list_of_characteristics[0][-3:] # (f_idx)p(par_idx)

    return dictionary

                                  ######################
####################################  Naming classes  ####################################
                                  ######################

class analysis_format:
    # Analysis format i.e. to use in plots and histograms
    def __init__(self, stage_name, info_tag, cuts = "", run_local = False):
        self.stage_name = stage_name

        self.info_tag = info_tag
        dictionary = get_info_tag_dictionary(info_tag)
        self.target = dictionary["Target"]
        self.n_bin = dictionary["n_bin"]
        self.n_dim = dictionary["n_dim"]

        # NOTE: Cuts are shown in a specific order, priorizing non-integrated variables
        #       as the first element
        self.cuts_L = get_cuts_final(cuts, stage_name)
        self.cuts_S = get_cuts_final(cuts, stage_name, use_short_name=True)
        self.fit_method = get_fit_method(cuts, False, False) # Fit method if available
        self.run_local = run_local # Choose True to work with local generated data files

    #####################################  Methods  ######################################
    def get_common_path(self):
        this_path = BASEPATH + "analysis_output/"
        if self.run_local:
            this_path += "local/"
        this_path += self.stage_name

        return this_path + "/"

    def get_path_root_files(self):

        return self.get_common_path() + "root_files/"

    def get_path_plots(self):
        this_path = self.get_common_path()
        this_path += "plots/"

        folder = get_info_tag__title_format(self.info_tag, omit_target=True)
        if (self.cuts_L):
            folder += "_%s"%(self.cuts_L)
        else:
            folder += "_NoCuts"
        folder += "/" + self.target

        return this_path + folder + "/"

    def get_file_root_files(self):
    # Format: (name)_(info_tag)-(cuts)-f(fit_method).root
    # ex. Correction_Fe_10B1-Xf_FE-fFold.png
        file_name = self.stage_name
        file_name += "_%s"%(get_info_tag__title_format(self.info_tag))
        file_name += "-%s"%(self.cuts_S)
        if (self.fit_method) and (self.stage_name != "Correction"):
            file_name += "-f%s"%(self.fit_method)

        return self.get_path_root_files() + file_name + ".root"
    
    def get_file_plots(self, reco_method = "", bincode = "", extension = "png"):
    # Format: (name)_(info_tag)-(reco_method)-f(fit_method)-(bincode).(extension)
    # ex. Correction_Fe_10B1-Reco-fFold-Q0N0Z0.png
        file_name = self.stage_name
        file_name += "_%s"%(get_info_tag__title_format(self.info_tag))
        if (reco_method):
            file_name += "-%s"%(reco_method)
        if (self.fit_method) and (self.stage_name != "Correction"):
            file_name += "-f%s"%(self.fit_method)
        if (bincode):
            file_name += "-%s"%(bincode)

        return self.get_path_plots() + file_name + "." + extension

    def get_name_histogram(self, reco_method, bincode = "", fit_idx = -1,
                           fit_parameter_idx = -1):
    # Format: h(name)(f_idx)p(par_idx)_(acc_meth)_(bincode)
    # ex. hParameters0p1_Reco_Q0N0Z0
        hist_name = "h" + self.stage_name
        if (fit_idx >= 0) and (fit_parameter_idx >= 0):
            hist_name += "%ip%i"%(fit_idx, fit_parameter_idx)
        hist_name += "_%s"%(reco_method)
        if (bincode):
            hist_name += "_%s"%(bincode)

        return hist_name

    def get_summary_plots(self, reco_method, extension = "png", is_LR_left = False,
                          parameters_info = ""):
    # Summary format: (n_bin)B(n_dim)_(cuts)-(reco_method)-f(fit_method)-(bincode).(extension)
    # ex. 10B1_FErr_AccQlt_P_Fold-Reco-NormB.pdf
        this_path = self.get_common_path()
        this_path += "Summary/"

        folder = get_info_tag__title_format(self.info_tag, omit_target=True)
        if (self.cuts_L):
            folder += "_%s"%(self.cuts_L)
        else:
            folder += "_NoCuts"
        this_path += folder + "/"

        file_name = self.stage_name
        if (parameters_info):
            file_name += parameters_info
        file_name +=  "_%s"%(get_info_tag__title_format(self.info_tag, omit_target=True))
        file_name += "_%s"%(self.cuts_S) if (self.cuts_S) else "_NoCuts"
        file_name += "-%s"%(reco_method)
        if (self.fit_method):
            file_name += "-f%s"%(get_fit_method_title(self.fit_method, is_LR_left))

        return this_path + file_name + "." + extension

class processed_files_format:
    # Retrieve names and paths of processed files to be used in analysis as inputs
    def __init__(self, stage_name, info_tag, cuts = "", CT_fraction = 0,
                 run_local = False):
        self.stage_name = stage_name

        self.info_tag = info_tag
        dictionary = get_info_tag_dictionary(info_tag)
        self.target = dictionary["Target"]
        self.n_bin = dictionary["n_bin"]
        self.n_dim = dictionary["n_dim"]

        self.cuts = get_cuts_final(cuts, stage_name, True) # Cuts separated by "_"
        self.CT_fraction = CT_fraction # Closure Test training percentage
        self.run_local = run_local # Choose True to work with local generated data files

    #####################################  Methods  ######################################
    def get_path(self):
        this_path = BASEPATH + "output/"
        if self.run_local:
            this_path += "local/"

        folder = self.stage_name
        if (self.stage_name == "ClosureTest"):
            folder += "%ip"%(self.CT_fraction)
        if (self.cuts):
            folder += "_%s"%(self.cuts)

        return this_path + folder + "/"

    def get_file(self):
        file_name = self.stage_name
        if (self.stage_name == "Correction"):
            file_name = "Corrected"
        not_acceptance = (self.stage_name != "Acceptance")
        file_name += "_%s"%(get_info_tag__title_format(self.info_tag, not_acceptance))

        return self.get_path() + file_name + ".root"

    def get_histogram_name(self, reco_method = "Reconstru"):
        if (self.stage_name == "Acceptance"):
            hist_name = "histAcc_%s"%(reco_method)
        elif (self.stage_name == "Correction") or (self.stage_name == "ClosureTest"):
            hist_name = "Corr_" + reco_method
            if ("Pion" in reco_method):
                hist_name = "True_PionReco"
            elif ("True" in reco_method):
                hist_name = "True"
            elif ("Raw" in reco_method):
                hist_name = "Raw_data"
        # Here you can add the format of other names, like in 2D maps or reco-efficiency

        return hist_name
