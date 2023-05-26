import ROOT
import os
import myStyle as ms


list_reco_long = ["Reconstru", "ReMtch_mc", "ReMtch_re"]
list_reco_shrt = ["Reco", "RMmc", "RMre"]

def idx_rec(acc_method):
    this_idx = -1
    if "Reco" in acc_method:
        this_idx = 0
    elif "mc" in acc_method:
        this_idx = 1
    elif "re" in acc_method:
        this_idx = 2

    if (acc_method is not "") and (this_idx == -1):
        error_str = "Acceptance method is not found. Try Reco, "\
                    "RMmc, or RMre."
        ms.error_msg("Name", error_str)
    
    return this_idx


class naming_format:
    def __init__(self, name, target, n_bin, n_dim = 0, cuts = "",
                 acc_method = "", bin_code = "", extension = "root",
                 inputfile_type = "", is_JLab = True, in_output = False,
                 hist_tag = ""):
        self.name = name
        self.target = target
        self.n_bin = n_bin
        self.n_dim = n_dim
        self.cuts = ms.get_cut_final(cuts, name, in_output)
        self.fit_method = ms.get_fit_method(cuts,False)
        idx_r = idx_rec(acc_method)
        self.acc_method_long = list_reco_long[idx_r] if acc_method else ""
        self.acc_method_shrt = list_reco_shrt[idx_r] if acc_method else ""
        self.bin_code = bin_code # Useful for saving png or pdfs
        self.extension = extension
        self.inputfile_type = inputfile_type # For Hist2D: hsim or data
        self.is_JLab = is_JLab
        self.hist_tag = hist_tag # Useful for pre-generated output files

    def get_file_name(self):
        # (name)_(target)_(n_bin)B(n_dim)-(fit)-(bin_code).(ext)
        # Correction_Fe_10B1-Q0N0Z0.png
        file_name = "%s_%s_%sB"%(self.name, self.target, self.n_bin)
        if self.n_dim:
            file_name+= "%s"%(self.n_dim)

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
        # (n_bin)B(n_dim)_(cuts)-(corr_meth)-(name).(ext)
        # 10B1_FErr_AccQlt_P_Fold-D-Reco-NormB.pdf
        file_name = "%sB%s"%(self.n_bin, self.n_dim)

        if self.cuts:
            file_name+= "-%s"%(self.cuts)
        if self.acc_method_shrt:
            file_name+= "-%s"%(self.acc_method_shrt)

        file_name+= "-%s.%s"%(self.name, self.extension)

        return file_name
    
    def get_folder_name(self):
    # initial_path/JLab_cluster/name_folder/n_bin/cuts/target/
    # e.g.: ../macros/plots/ JLab_cluster/ Correction/ 10B1/ FErr_AccQlt/ Fe/

        folder = "../macros/plots/"

        if self.is_JLab:
            folder+="JLab_cluster/"

        folder+= "%s/"%(self.name)
        folder+= "%sB%s/"%(self.n_bin, self.n_dim)
        folder+= "%s/"%(self.cuts) if self.cuts else "NoCuts/"
        folder+= "%s/"%(self.target)

        return folder

    def get_folder_name_from_output(self):
    # initial_path/JLab_cluster/(name_folder)_(cuts)/
    # e.g.: ../output/ JLab_cluster/ Correction_FErr_AccQlt/
        folder = "../output/"

        if self.is_JLab:
            folder+="JLab_cluster/"

        fname = "%s"%(self.name)
        if self.cuts:
            fname+= "_%s"%(self.cuts)

        folder+= "%s/"%(fname)

        return folder

    def get_folder_name_summary(self):
    # initial_path/JLab_cluster/name_folder/nbin/cuts/
    # e.g.: ../macros/plots/ JLab_cluster/ Summary/NormB/ 10B1/ FErr_AccQlt/

        folder = "../macros/plots/"

        if self.is_JLab:
            folder+="JLab_cluster/"

        folder+= "Summary/"
        folder+= "%s/"%(self.name)
        folder+= "%sB%s/"%(self.n_bin, self.n_dim)
        folder+= "%s/"%(self.cuts) if self.cuts else "NoCuts/"

        return folder

    def get_path(self):
        folder = self.get_folder_name()
        file = self.get_file_name()

        return folder + file
    
    def get_path_from_output(self):
        folder = self.get_folder_name_from_output()
        file = self.get_file_name_from_output()

        return folder + file
    
    def get_path_summary(self):
        folder = self.get_folder_name_summary()
        file = self.get_file_name_summary()

        return folder + file


    def get_hist_name(self):
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
