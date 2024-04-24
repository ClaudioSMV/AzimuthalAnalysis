import ROOT
import os
import myStyle as ms


list_reco_long = ["Reconstru", "ReMtch_mc", "ReMtch_re"]
list_reco_shrt = ["Reco", "RMmc", "RMre"]

def idx_rec(acc_meth):
    this_idx = -1
    if "mc" in acc_meth:
        this_idx = 1
    elif ("_re" in acc_meth) or ("rc" in acc_meth) or ("RMre" in acc_meth):
        this_idx = 2
    elif "Reco" in acc_meth:
        this_idx = 0

    if ("raw" not in acc_meth.lower()) and (acc_meth is not "")\
       and (this_idx == -1):
        error_str = "Acceptance method is not found. Try Reco, "\
                    "RMmc, or RMre."
        ms.error_msg("Name", error_str)
    
    return this_idx

def get_acc_meth(meth_str, length):
    if "raw" not in meth_str.lower():
        idx = idx_rec(meth_str)
        if (idx<0):
            acc_meth = ""
        else:
            if "l" in length.lower():
                acc_meth = list_reco_long[idx]
            elif "s" in length.lower():
                acc_meth = list_reco_shrt[idx]
    else:
        acc_meth = "Raw"

    return acc_meth


class naming_format:
    def __init__(self, name, target, n_bin = 10, n_dim = 0, cuts = "",
                 acc_method = "", bin_code = "", extension = "root",
                 inputfile_type = "", is_JLab = True, in_output = False,
                 hist_tag = "", fraction = 0):
        self.name = name
        # Accept (target)_(nbin)_(ndim) format as shortcut
        if len(target.split("_"))>1:
            d_tg = ms.get_name_dict(target)
            target = d_tg["targ"]
            n_bin = d_tg["n_bin"]
            n_dim = d_tg["n_dim"]
        self.target = target
        self.n_bin = n_bin
        self.n_dim = n_dim

        self.cuts = ms.get_cut_final(cuts, name, in_output)
        self.fit_method = ms.get_fit_method(cuts, use_default=False,
                                            show_warn=False)
        self.acc_method_long = get_acc_meth(acc_method, "L")
        self.acc_method_shrt = get_acc_meth(acc_method, "S")

        self.bin_code = bin_code # Useful for saving png or pdfs
        self.extension = extension
        self.inputfile_type = inputfile_type # For Hist2D: hsim or data
        self.is_JLab = is_JLab
        self.hist_tag = hist_tag # Useful for pre-generated output files
        self.fraction = fraction # Fraction in Closure Test

    ############################  Update info  #############################
    def updt_name(self, new_name, add = False):
        name = self.name + new_name
        if not add:
            name = new_name
        self.name = name

    def updt_acc_method(self, new_meth):
        self.acc_method_long = get_acc_meth(new_meth, "L")
        self.acc_method_shrt = get_acc_meth(new_meth, "S")

    def updt_bin_code(self, new_bincode):
        self.bin_code = new_bincode

    def updt_extension(self, new_extension):
        self.extension = new_extension

    ############################  File naming  #############################
    def get_file_name(self):
        # (name)_(target)_(n_bin)B(n_dim)-(acc_meth)-(fit)-(bin_code).(ext)
        # Correction_Fe_10B1-Q0N0Z0.png
        file_name = "%s_%s_%sB"%(self.name, self.target, self.n_bin)
        if self.n_dim:
            file_name+= "%s"%(self.n_dim)

        if self.acc_method_shrt:
            file_name+= "-%s"%(self.acc_method_shrt)

        if self.fit_method:
            file_name+= "-%s"%(self.fit_method)

        if self.bin_code:
            file_name+= "-%s"%(self.bin_code)
        
        file_name+= ".%s"%(self.extension)

        return file_name
    
    def get_file_name_from_output(self):
        sname = self.name
        starg = self.target
        snbin = self.n_bin
        sndim = self.n_dim
        stype = self.inputfile_type

        if sname is "Acceptance":
            this_file = "Acceptance_%s_%sB.root"%(starg, snbin)
        elif sname is "Correction":
            if not sndim:
                error_txt = "Corrected output file requires n_bin"\
                            " (use 1 as default)"
                ms.error_msg("Name", error_txt)
            this_file = "Corrected_%s_%sB%s.root"%(starg, snbin, sndim)
        elif "Hist2D" in sname:
            # Maps names should be introduced as Hist2D_<name>
            # so that we remove the prefix to get the correct name
            map_type = sname.replace("Hist2D_","")

            # Use n_bin = 0 if binning selection is not important!
            n_bin_info = "_%sB"%(snbin) if snbin else ""

            this_file = "%s_%s%s_%s.root"%(map_type, starg, n_bin_info, stype)
        else:
            n_dim_info = sndim if sndim else ""
            this_file = "%s_%s_%sB%s.root"%(sname, starg, snbin, n_dim_info)

        return this_file
    
    def get_file_name_summary(self):
        # (n_bin)B(n_dim)_(cuts)-(corr_meth)-(name)_(bin).(ext)
        # 10B1_FErr_AccQlt_P_Fold-Reco-NormB.pdf
        file_name = "%sB%s"%(self.n_bin, self.n_dim)

        if self.cuts:
            file_name+= "-%s"%(self.cuts)
        if self.acc_method_shrt:
            file_name+= "-%s"%(self.acc_method_shrt)

        file_name+= "-%s"%(self.name)
        if self.bin_code:
            file_name+= "_%s"%(self.bin_code)
        file_name+= ".%s"%(self.extension)

        return file_name
    
    ###########################  Folder naming  ############################
    def get_folder_name(self, create = False, overwrite = False):
    # initial_path/JLab_cluster/name_folder/n_bin/cuts/target/
    # e.g.: ../macros/plots/ JLab_cluster/ Correction/ 10B1/ FErr_AccQlt/ Fe/

        folder = "../macros/plots/"

        if self.is_JLab:
            folder+="JLab_cluster/"

        folder+= "%s"%(self.name)
        if self.fraction:
            folder+= "%ip"%(self.fraction)
        folder+= "/%sB%s/"%(self.n_bin, self.n_dim)
        folder+= "%s/"%(self.cuts) if self.cuts else "NoCuts/"
        folder+= "%s/"%(self.target)

        if create:
            ms.create_folder(folder, overwrite=overwrite)

        return folder

    def get_folder_name_from_output(self):
    # initial_path/JLab_cluster/(name_folder)_(cuts)/
    # e.g.: ../output/ JLab_cluster/ Correction_FErr_AccQlt/
        folder = "../output/"

        if self.is_JLab:
            folder+="JLab_cluster/"

        fname = "%s"%(self.name)
        if self.fraction:
            fname+= "%ip"%(self.fraction)
        if self.cuts:
            fname+= "_%s"%(self.cuts)

        folder+= "%s/"%(fname)

        return folder

    def get_folder_name_summary(self, create = False, overwrite = False):
    # initial_path/JLab_cluster/Summary/name_folder/(nbin)B(nDim)/cuts/
    # e.g.: ../macros/plots/ JLab_cluster/ Summary/NormB/ 10B1/ FErr_AccQlt/

        folder = "../macros/plots/"

        if self.is_JLab:
            folder+="JLab_cluster/"

        folder+= "Summary/"
        folder+= "%s/"%(self.name)
        folder+= "%sB%s/"%(self.n_bin, self.n_dim)
        folder+= "%s/"%(self.cuts) if self.cuts else "NoCuts/"

        if create:
            ms.create_folder(folder, overwrite=overwrite)

        return folder

    ############################  Path naming  #############################
    def get_path(self, create = False, overwrite = False):
        folder = self.get_folder_name(create, overwrite)
        file = self.get_file_name()

        return folder + file

    def get_path_from_output(self):
        folder = self.get_folder_name_from_output()
        file = self.get_file_name_from_output()

        return folder + file

    def get_path_summary(self, create = False, overwrite = False):
        folder = self.get_folder_name_summary(create, overwrite)
        file = self.get_file_name_summary()

        return folder + file

    ##########################  Histogram naming  ##########################
    def get_hist_name(self):
        # h(name)_(acc_meth)_(bincode)
        # hCorrection_Reco_Q0N0Z0
        hname = "h%s"%(self.name)

        if self.acc_method_shrt:
            hname+= "_%s"%(self.acc_method_shrt)
        if self.bin_code:
            hname+= "_%s"%(self.bin_code)
        
        return hname

    def get_hist_name_from_output(self):
        if self.name is "Acceptance":
            hname = "histAcc_"
            if self.acc_method_long:
                hname+= "%s"%(self.acc_method_long)
            else:
                hname+= "Reconstru"
        elif self.name is "Correction":
            hname = "Corr_%s"%(self.acc_method_long)
            if "raw" in self.hist_tag.lower():
                hname = "Raw_data"
        elif self.name is "ClosureTest":
            hname = "Corr_%s"%(self.acc_method_long)
            if "pionreco" in self.hist_tag.lower():
                hname = "True_PionReco"
            elif "true" in self.hist_tag.lower():
                hname = "True"
        else:
            hname = self.hist_tag

        return hname

    def get_hist_name_summary(self, ffit, par):
        # h(name)(ffit)p(par)_(acc_meth)_(bincode)
        # hCorrection0p1_Reco_Q0N0Z0
        hname = "h%s%ip%i"%(self.name, ffit, par)

        if self.acc_method_shrt:
            hname+= "_%s"%(self.acc_method_shrt)
        if self.bin_code:
            hname+= "_%s"%(self.bin_code)

        return hname

    ###############################  Others  ###############################
    def get_l_fitnames(self):
        l_fnames = ["crossSectionR"]
        if (self.fit_method == "LR"):
            l_fnames.append("crossSectionL")

        return l_fnames

    def get_matrix_name(self, name, number):
        # M(name)(number)_(acc_meth)_(bincode)
        # Mcov1_Reco_Q0N0Z0
        tail = "_%s_%s"%(self.acc_method_shrt, self.bin_code)
        name_M = "M%s%i%s"%(name, number, tail)

        return name_M


###########################  Get info from a title  ############################

def get_hist_dict(hname):
    # h(name)_(acc_meth)_(bincode)
    # hCorrection_Reco_Q0N0Z0
    d_att = {}
    l_att = hname.split("_")

    d_att["hname"] = l_att[0][1:]
    if len(l_att) > 1:
        d_att["hmeth"] = l_att[1]
    if len(l_att) > 2:
        d_att["hbincode"] = l_att[2]

    return d_att

def get_hist_summary_dict(hname):
    # h(name)(ffit)p(par)_(acc_meth)_(bincode)
    # hCorrection0p1_Reco_Q0N0Z0
    d_att = {}
    d_tmp = get_hist_dict(hname)

    d_att["hname"] = d_tmp["hname"][0:-3]
    d_att["hffit"] = d_tmp["hname"][-3]
    d_att["hnpar"] = d_tmp["hname"][-1]
    d_att["hfullname"] = d_tmp["hname"]
    if "hmeth" in d_tmp:
        d_att["hmeth"] = d_tmp["hmeth"]
    if "hbincode" in d_tmp:
        d_att["hbincode"] = d_tmp["hbincode"]

    return d_att

def get_hist_hname(full_name):
    d_att = get_hist_dict(full_name)
    if d_att["hname"][-2] == "p":
        d_att = get_hist_summary_dict(full_name)

    return d_att["hname"]

def get_hist_hmeth(full_name):
    d_att = get_hist_dict(full_name)

    return d_att["hmeth"]

def get_hist_hbincode(full_name):
    d_att = get_hist_dict(full_name)

    return d_att["hbincode"]

def get_hist_hfullname(full_name):
    d_att = get_hist_summary_dict(full_name)
    summary_name = "%s%sp%s"%(d_att["hname"], d_att["hffit"], d_att["hnpar"])
    if summary_name != d_att["hfullname"]:
        err_txt = "Wrong naming function! Use get_hist_hname() or "\
                  "make sure it is a summary naming format"
        ms.error_msg("Naming", err_txt)

    return d_att["hfullname"]

def get_hist_hffit(full_name):
    d_att = get_hist_summary_dict(full_name)

    return d_att["hffit"]

def get_hist_hnpar(full_name):
    d_att = get_hist_summary_dict(full_name)

    return d_att["hnpar"]
