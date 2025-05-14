
from lib_cuts import get_output_cuts, get_ordered_cuts_at_this_stage, check_valid_cuts\
    , format_output_binvars
from lib_info_tag import get_info_tag_dictionary, get_info_tag__title_format
from lib_fit import check_fit_method_exists, get_fit_name
from lib_error import info_msg, error_msg
import os
import sys

BASEPATH = "./../"

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

                               ##########################
#################################      Functions       ###################################
#################################  Manage directories  ###################################
                               ##########################

def consecutive_number(path):
# Add a sequential number to the path
    if (path[-1] == "/"):
        path = path[:-1]
    count = 1
    while(os.path.exists(path + str(count))):
        count += 1

    return path + str(count)

def create_folder(outdir, title = "", enumerate = False, silence = True):
# Create folder: outdir/title. Enumerate adding a consecutive number at the end.
    outpath = os.path.join(outdir, title) if title else outdir
    if enumerate:
        outpath = consecutive_number(outpath)
    exists = os.path.exists(outpath)
    if not exists:
        info_msg("create_folder", "Creating folder: %s."%(outpath))
        os.makedirs(outpath)
    elif not silence:
        info_msg("create_folder", "%s already exists!"%(outpath))

    return outpath

def check_file_exists(path, filename, overwrite = False):
    full_path = os.path.join(path, filename)
    if not os.path.exists(full_path):
        return
    if not overwrite:
        error_msg("check_file_exists", "%s already exists! Left as it is."%(full_path))
        sys.exit(1)
    info_msg("check_file_exists", "%s already exists! Overwriting it."%(full_path))

                                  ######################
####################################  Naming classes  ####################################
                                  ######################

class analysis_format:
    # Analysis format i.e. to use in plots and histograms
    def __init__(self, stage_name, info_tag, binvars, cuts = "", fit_method = "",
                 run_local = False):
        self.stage_name = stage_name

        self.info_tag = info_tag
        dictionary = get_info_tag_dictionary(info_tag)
        self.target = dictionary["Target"]
        self.n_bin = dictionary["n_bin"]
        self.n_dim = dictionary["n_dim"]

        self.binvars = binvars
        self.cuts_list, _ = get_ordered_cuts_at_this_stage(stage_name, cuts)
        self.fit_method = check_fit_method_exists(fit_method, stage_name)
        self.run_local = run_local # Choose True to work with local generated data files

    #####################################  Methods  ######################################
    def get_common_path(self):
        this_path = BASEPATH + "analysis_output/"
        if self.run_local:
            this_path += "local/"
        this_path += self.stage_name

        return this_path + "/"

    def get_path_root_files(self):
        return create_folder(self.get_common_path(), "root_files")

    def get_path_plots(self):
        this_path = self.get_common_path()
        this_path += "plots/"

        folder = get_info_tag__title_format(self.info_tag, omit_target=True)
        folder += "_%s"%(format_output_binvars(self.binvars))
        if (self.fit_method):
            folder += "_%s"%(get_fit_name(self.fit_method))
        folder += "_%s"%(get_output_cuts(self.cuts_list, self.stage_name))
        folder += "/" + self.target

        return create_folder(this_path, folder)

    def get_file_root_files(self, overwrite = False, check_validity = False):
    # Format: (name)_(info_tag)-b(binvars)-(cuts)-f(fit_method).root
    # ex. Correction_Fe_10B1-Xf_FE-fFold.png
        folder = self.get_path_root_files()
        file_name = self.stage_name
        file_name += "_%s"%(get_info_tag__title_format(self.info_tag))
        file_name += "-b%s"%(format_output_binvars(self.binvars))
        if check_validity:
            check_valid_cuts(self.cuts_list)
        if self.cuts_list:
            file_name += "-%s"%(get_output_cuts(self.cuts_list, self.stage_name,
                                                use_cut_tags=True, warn_unused=True))
        else:
            file_name += "-NoCuts"
        if (self.fit_method):
            file_name += "-f%s"%(self.fit_method)
        file_name += ".root"
        check_file_exists(folder, file_name, overwrite)

        return os.path.join(folder, file_name)
    
    def get_file_plots(self, reco_method = "", bincode = "", extension = "png"):
    # Format: (name)_(info_tag)-(reco_method)-f(fit_method)-(bincode).(extension)
    # ex. Correction_Fe_10B1-Reco-fFold-Q0N0Z0.png
        folder = self.get_path_plots()
        file_name = self.stage_name
        file_name += "_%s"%(get_info_tag__title_format(self.info_tag))
        if (reco_method):
            file_name += "-%s"%(reco_method)
        if (self.fit_method):
            file_name += "-f%s"%(self.fit_method)
        if (bincode):
            file_name += "-%s"%(bincode)
        file_name += ".%s"%(extension)

        return os.path.join(folder, file_name)

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

        self.cuts = get_output_cuts(cuts, stage_name, processed_files=True)
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

class summary_format: # TODO: UPDATE THIS TO WORK!
    # Naming for summary
    def __init__(self, stage_name, info_tag, binvars, cuts = "", fit_method = "",
                 run_local = False):
        self.stage_name = stage_name

        self.info_tag = info_tag
        dictionary = get_info_tag_dictionary(info_tag)
        self.target = dictionary["Target"]
        self.n_bin = dictionary["n_bin"]
        self.n_dim = dictionary["n_dim"]

        self.binvars = binvars
        self.cuts_list, _ = get_ordered_cuts_at_this_stage(stage_name, cuts)
        self.fit_method = check_fit_method_exists(fit_method, stage_name)

        self.run_local = run_local # Choose True to work with local generated data files

    #####################################  Methods  ######################################

    def get_summary_plots(self, reco_method, extension = "png", is_LR_left = False,
                          parameters_info = ""):
    # Summary format: (n_bin)B(n_dim)-(binvars)-(cuts)/(stage)(parameters_info)-(cuts)-
    # Summary format: (n_bin)B(n_dim)-(binvars)-(cuts)-(reco_method)-f(fit_method)-(bincode).(extension)
    # ex. 10B1_FErr_AccQlt_P_Fold-Reco-NormB.pdf
        folder = get_info_tag__title_format(self.info_tag, omit_target=True)
        folder += "-%s"%(format_output_binvars(self.binvars, True))
        if self.cuts_list:
            folder += "-%s"%(get_output_cuts(self.cuts_list, self.stage_name))
        else:
            folder += "-NoCuts"
        path = os.path.join(self.get_common_path(), "Summary", folder)

        file = self.stage_name
        if (parameters_info):
            file += parameters_info
        if self.cuts_list:
            file += "-%s"%(get_output_cuts(self.cuts_list, self.stage_name, use_cut_tags=True))
        else:
            file += "-NoCuts"
        file += "-%s"%(reco_method)
        if (self.fit_method):
            file += "-%s"%(get_fit_name(self.fit_method))

        return path + file + "." + extension
