import ROOT
import os
import Bins as bn


###############################
##  Define global variables  ##
###############################

marg=0.05
font=43 # Helvetica
tsize=38


####################
##      Info      ##
##  Names format  ##
####################

####
# Acceptance_%s_B%i.root      ; <Target>,<_binIndex>
# Corrected_%s_B%i_%iD.root   ; <Target>,<_binIndex>,<_binNdims (non-integrated dims)>
# ClosureTest_%s_B%i_%iD.root ; <Target>,<_binIndex>,<_binNdims (non-integrated dims)>
####


############################
##  File name and format  ##
############################

def get_name_dict(nameFormat):
# Create dictionary from input: <targ>_<nBin>_<nDim>
# with output: {"Target": <targ>, "BinningType": <nBin>, "NDims": <nDim>}
    targetDict = {}
    targetList = nameFormat.split("_")
    targetDict["Target"] = targetList[0]
    targetDict["BinningType"] = int(targetList[1])
    if (len(targetList)==2):
        targetList.append(0)
    targetDict["NDims"] = int(targetList[2])

    return targetDict

def get_name_format(nameFormat, isAcc = False):
# Give string with name formatted using input: <targ>_<nBin>_<nDim>
# with output: "<targ>_<nBin>B<nDim>"
    formDict = get_name_dict(nameFormat)
    fileName = "%s_%iB"%(formDict["Target"],formDict["BinningType"])
    if (not isAcc) and formDict["NDims"]:
        fileName+="%i"%(formDict["NDims"])

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


#############################
##  Cuts and dictionaries  ##
#############################

### Input name
########
## From python macro input to internal/input code
dict_cut_long2short = {
    "XF": "Xf", "Xf": "Xf",
    "XT_TFR": "XT", "XTFR": "XT", "Xt": "XT", "XT": "XT",
    "DeltaSector": "DS", "DSect": "DS", "DSctr": "DS", "DS": "DS",
    "BadSector": "BS", "rmBadSector": "BS", "BS": "BS",
    "PionFiducial": "PF", "PiFiducial": "PF", "Pf": "PF", "PF": "PF",
    "MirrorMatch": "MM", "MMtch": "MM", "MM": "MM",
    "MirrorMatch2": "M2", "MMtch2": "M2", "M2": "M2",
    # "Sector": "Se", "Sctr": "Se", "Sect": "Se", "Se": "Se",
    "FErr": "FE", "FullError": "FE", "Fe": "FE", "FE": "FE",
    "AccQlt": "AQ", "AccQuality": "AQ", "AQ": "AQ",
    "rmNpheElH": "Pe", "PheElH": "Pe", "PE": "Pe", "Pe": "Pe",
    "Z": "Zx", "Zx": "Zx",
    "P": "Px", "Px": "Px",
    # "Shift": "Sh", "Sh": "Sh",
    "useSin": "Fs", "FitSin": "Fs", "Fs": "Fs",
    "NPeak": "NP", "NP": "NP",
    # "Fold": "Fd", "Fd": "Fd",
    # "LR": "LR",
    # "Fullfit": "Ff", "FFit": "Ff", "Ff": "Ff",
    # "Left": "Lf", "Lf": "Lf",
    # "Right": "Rg", "Rg": "Rg",
    "MixD": "MD", "MD": "MD",
}
dict_fit_long2short = {
    "Shift": "Sh", "Sh": "Sh",
    "Fold": "Fd", "Fd": "Fd",
    "LR": "LR",
    "Fullfit": "Ff", "FFit": "Ff", "Ff": "Ff",
}

dict_cut_long2short.update(dict_fit_long2short)

### Output name
########
## From internal/input code to folder-name format
dict_cut_short2long = {
    "Xf": "Xf", "XT": "XTFR", "DS": "DSect0", "BS": "NoBadSec", "PF": "PiFid", "MM": "MMtch", "M2": "MMtch2",
    "FE": "FErr", "AQ": "AccQlt", "Pe": "dfNphe",
    "Zx": "Z", "Px": "P", #"Sh": "Shift",
    "Fs": "Sin", "NP": "NPeak",
    #"Fd": "Fold", "LR": "LR", "Ff": "Full",
    "MD": "MixD", #"Lf": "Left", "Rg": "Right",
}
dict_fit_short2long = {
    "Fd": "Fold", "LR": "LR", "Ff": "Full", "Sh": "Shift",
}

dict_cut_short2long.update(dict_fit_short2long)

### Legend name
########
## From internal/input code to Legend's text (Latex format)
dict_cut_short2legend = {
    "Xf": "#X_f CFR", "XT": "#X_f TFR", "DS": "#Delta Sect #neq 0", "BS": "No bad Sect", "PF": "Fidual cut #pi", "MM": "Mirror Match",
    "M2": "Mirror Match 2",
    "FE": "", "AQ": "", "Pe": "N_{phe}^{el} #neq N_{phe}^{h}",
    "Zx": "", "Px": "",
    "Fs": "", "NP": "",
    "MD": "",
}
dict_fit_short2legend = {
    "Fd": "Fold", "LR": "LR", "Ff": "Full", "Sh": "Shift", # "LR_Left": "Left", "LR_Right": "Right"
}

dict_cut_short2legend.update(dict_fit_short2legend)

### Define key with cuts in order of applicability (Acc, Corr, Fit, Summary)
########
cutMasterKey = ""

## Acceptance
cutMasterKey+= "Xf0XT0DS0BS0PF0MM0M20" # Yh0

## Correction
cutMasterKey+= "FE0AQ0Pe0Zx0Px0"

## Fit
cutMasterKey+= "Sh0Fs0NP0Fd0LR0Ff0"

## Summary
cutMasterKey+= "MD0"


########################
##  Format cut names  ##
########################

def get_cut_str2list(this_cut_str):
# Transform a str of cuts separated by "_" to a list
    this_list = this_cut_str.split("_")
    # Remove empty elements from input
    while ("" in this_list):
        this_list.remove("")

    return this_list

def cut_list2longstr(list_cuts):
# Take list of cuts short-name with format <cut><0-1>
# where 0 is cut not applied and 1 is applied
# Returns str with long-names of cuts applied separated by "_"
    cut_str = ""
    for c in list_cuts:
        # Skip unused cuts and empty elements
        if (c[-1] == "0" or c == ""):
            continue
        this_cut = c[0:-1]
        cut_str+="_"+dict_cut_short2long[this_cut]

    return cut_str

def cut_list2legend(list_cuts):
# Take list of cuts short-name with format <cut><0-1>
# where 0 is cut not applied and 1 is applied
# Returns str with legends of cuts applied
    cut_str = ""
    for c in list_cuts:
        if (c[-1] == "0" or c == ""):
            continue
        this_cut = c
        if (len(c) == 3):
            this_cut = c[0:2]

        if cut_str and dict_cut_short2legend[this_cut]:
            cut_str+=" "
        cut_str+=dict_cut_short2legend[this_cut]

        print(cut_str)

    print("    Final legend: %s"%cut_str)
    return cut_str

def get_cut_long2final(cut_str = "", isLegend = False):
# Takes str with format "Aaaa_Bbb_ccc_Ddd" (long-name)
# and returns str with final names for the file
# The order is defined by cutMasterKey
    the_key = cutMasterKey
    this_list = the_key.split("0")
    this_list.remove("")

    ref_list = list(this_list)

    list_input = get_cut_str2list(cut_str)

    for elem in list_input:
        if elem in dict_cut_long2short:
            this_index = ref_list.index(dict_cut_long2short[elem])
            this_list[this_index] = dict_cut_long2short[elem]+"1"
        elif (("Left" in elem) or ("Right" in elem)):
            continue
        else:
            print("  [CutStr] Cut not found! : %s"%(elem))
            exit()

    for elem in this_list:
        if (elem[-1] != "1"):
            this_index = ref_list.index(elem)
            this_list[this_index] = elem+"0"

    this_str = cut_list2longstr(this_list) if not isLegend else cut_list2legend(this_list)

    return this_str

def get_cut_str2finallist(cut_str):
# Transform a str of cuts separated by "_" to a list with output (final) names
    real_cut_str = get_cut_long2final(cut_str)
    this_finallist = get_cut_str2list(real_cut_str)

    return this_finallist


################################
##  Set study dimensionality  ##
################################

def create_phi_hist(th1_input, name, do_shift):
# Create a copy of a 1d histogram for phi_PQ
# By default, it uses x-axis within [-180, 180]
# Option do_shift plots within [0, 360]
    this_xmin = th1_input.GetXaxis().GetXmin() # -180.
    this_xmax = th1_input.GetXaxis().GetXmax() #  180.
    this_nbin = th1_input.GetNbinsX()

    if (do_shift):
        # if (this_nbin%2 == 0): # Even (0. is in a bin edge) (default)
        this_xmin =   0.
        this_xmax = 360.
        central_bin = int(this_nbin/2)+1
        # Note that if nbin is Even, central_bin is the bin at the right of the
        # central one; if it is Odd, central_bin is the real central one;

        if (this_nbin%2 == 1): # Odd (0. is in the middle of a bin)
            bin_width = th1_input.GetBinWidth(central_bin)

            # Slightly shift edges so that bins are correct
            this_xmin -= bin_width/2.
            this_xmax -= bin_width/2.

    h_tmp = ROOT.TH1D(name,";%s;Counts"%(axis_label('I',"LatexUnit")), this_nbin, this_xmin, this_xmax)

    # Fill histogram bin by bin
    for i in range(1,this_nbin+1):
        this_value = th1_input.GetBinContent(i)
        this_error = th1_input.GetBinError(i)
        # if (this_value == 0):
        #     print("    %s : Value: %i"%(name,this_value))
        #     this_value = 0.0
        #     this_error = 0.0
        bin_L_edge = th1_input.GetBinLowEdge(i)
        bin_center = th1_input.GetBinCenter(i)

        the_bin = i
        if (do_shift):
            # Move the left half to the right of the right half
            if (this_nbin%2 == 0): # Even  e.g. with 6 bins, first right bin is 4
                if (bin_L_edge < 0.0):
                    the_bin = i + central_bin -1 #  e.g. 1,2,3 bins will be 4,5,6
                else:
                    the_bin = i - central_bin + 1 # e.g. 4,5,6 bins will be 1,2,3

            elif (this_nbin%2 == 1): # Odd e.g. with 5 bins, center is 3
                if (bin_center < 0.0):
                    the_bin = i + central_bin #     e.g. 1,2 bins will be 4,5
                else:
                    the_bin = i - central_bin + 1 # e.g. 3,4,5 bins will be 1,2,3
                # Note in this case the distribution does not start at zero,
                # but at a negative number
        # Skip bins that are empty (if not, they will count as an entry with zero value)
        if (this_value != 0):
            h_tmp.SetBinContent(the_bin, this_value)
            h_tmp.SetBinError(the_bin, this_error)

    return h_tmp

def get_bincode_list(bin_vars, this_binList):
# Create a list with the short code str to identify each kinematic bin; e.g. a bin of Q2,Nu,Zh
# will integrate Pt2, so code will be QaNbZc with a,b,c some integer corresponding to the bin
#   bin_vars: str with initial of the vars used; this_binList: list with bins limits
    output_list = []
    # Change second electron variable if necessary
    template = ["Q","N","Z","P"] if ("X" not in bin_vars) else ["Q","X","Z","P"]
    nbins = [1,1,1,1]

    # Get total number of bins per variable and remove integrated ones
    for v,var in enumerate(template):
        if var not in bin_vars:
            template[v] = ""
        else:
            this_bin = len(this_binList[var]) - 1
            nbins[v] = this_bin

    totalsize = nbins[0]*nbins[1]*nbins[2]*nbins[3]
    # Fill list beginning with all bins zero and up to the total nbins per variable
    for i in range(totalsize):
        total_tmp = totalsize
        i_tmp = i
        txt_tmp = ""
        for v,var in enumerate(template):
            if (var==""):
                continue
            total_tmp /= nbins[v]
            index = i_tmp/(total_tmp)
            i_tmp -= index*total_tmp
            txt_tmp += "%s%i"%(var, index)
        output_list.append(txt_tmp)

    # Output would be ["Q0N0Z0", "Q0N0Z1", ..., "Q3N3Z9"]
    return output_list

def get_sparseproj1d_list(thnSparse, list_binstr, shift):
# Create list of phi 1d hist from thnSparse for each bin defined in
# list_binstr (list of bincodes)
    this_outlist = []
    template = ["Q","N","Z","P"] if ("X" not in list_binstr[0]) else ["Q","X","Z","P"]

    # Remove integrated variables (not in bincode)
    for l,letter in enumerate(template):
        if letter not in list_binstr[0]:
            template[l] = ""

    # Run over all n-dimensional bins
    for bincode in list_binstr:

        for l,letter in enumerate(template):
            if not letter:
                continue

            # Get letter location by its position in the string with index, then add 1 to get
            # the bin number location
            pos = int(bincode[bincode.index(letter)+1])
            thnSparse.GetAxis(l).SetRange(pos+1, pos+1)
            # Note that if range is not changed, projection will integrate over that axis!

        proj_tmp = thnSparse.Projection(4)
        proj_tmp.SetName("proj_tmp")
        this_hist = create_phi_hist(proj_tmp, thnSparse.GetName()+"_"+bincode, shift)
        this_outlist.append(this_hist)
        proj_tmp.Delete()

    return this_outlist


###########################
##  Get fit information  ##
###########################

def GetFitMethod(output_str, use_def = True):
    this_method = ""

    for fm in dict_fit_short2long:
        out_name = dict_fit_short2long[fm]

        if out_name in get_cut_long2final(output_str):
            if (this_method != ""): # and not accept_more
                print("  [FitMethod] More than one fit method selected. Please, choose only one of the options!")
                print("              Ff-Full (empty, default); LR; Fd-Fold; Sh-Shift;")
                exit()
            # elif (this_method != "" ):
            #     this_method +="_"
            this_method = fm

    ## Set default method
    if (use_def and not this_method):
        this_method = "Ff"

    # if (this_method):
    #     str_meth = this_method.replace("_", ", ")
    #     if not accept_more:
    #         print("    [FitMethod] Using %s fit method"%dict_fit_short2long[str_meth])
    #     else:
    #         print("    [FitMethod] Using %s fit method/s"%str_meth)

    return this_method

def GetFitExtension(this_method, fname):
    this_ext = this_method[0]

    if (this_method=="LR") and ("R" in fname):
        this_ext = "R"
    elif (this_method=="Ff"):
        this_ext = "A"

    return this_ext

#############################
##  Paths and directories  ##
#############################

def CreateFolder(outdir, title, overwrite = False, enumerate = True):
    outdir2 = os.path.join(outdir,title)

    if overwrite:
        os.makedirs(outdir2)
        print("  [myStyle] %s created."%outdir2)
    else:
        if not os.path.exists(outdir2):
            os.makedirs(outdir2)
            print("  [myStyle] %s created."%outdir2)
        elif enumerate:
            i = 1
            while(os.path.exists(outdir2)):
                    outdir2 = outdir2[0:-2] + str(i) + outdir2[-1]
                    i+=1
            os.mkdir(outdir2)
            print("  [myStyle] %s created."%outdir2)
        else:
            print("  [myStyle] %s already exists!."%outdir2)

    return outdir2

### /output/
########
def getOutputFolder(nameMethod, extraCuts = "", JLab_cluster = True, isOutput = True):
    this_folder = "../output/"
    if JLab_cluster: this_folder+="JLab_cluster/"

    these_cuts = get_cut_long2final(extraCuts)
    this_folder+=nameMethod+these_cuts+"/"
    if isOutput:
        CreateFolder(this_folder, "", False, False)

    return this_folder

def getOutputFile(nameMethod, nameFileExt):
    if nameMethod=="Acceptance":
        this_file = "Acceptance_"+get_name_format(nameFileExt, True)+".root"
    elif nameMethod=="Correction":
        this_file = "Corrected_"+get_name_format(nameFileExt, False)+".root"
    elif nameMethod=="Hist2D":
        this_file = "Hist2D_"+get_name_dict(nameFileExt)["Target"]+"_.root" # Remember to add "data" or "hsim" with add_str_before_ext()
    else:
        this_file = nameMethod+"_"+get_name_format(nameFileExt, False)+".root"

    return this_file

def getOutputFileWithPath(nameMethod, nameFileExt, extraCuts = "", JLab_cluster = True, isOutput = True):
    this_path = getOutputFolder(nameMethod, extraCuts, JLab_cluster, isOutput) # "../<out>/"
    this_file = getOutputFile(nameMethod, nameFileExt)

    return this_path+this_file

### /plots/
########
def getPlotsFolder(nameMethod, extraCuts = "", extraPath = "", JLab_cluster = True, isOutput = True):
    this_folder = "../macros/plots/"
    if JLab_cluster: this_folder+="JLab_cluster/"

    these_cuts = get_cut_long2final(extraCuts)
    this_folder+=nameMethod+"/"+these_cuts[1:]+"/"
    if extraPath:
        this_folder+=extraPath+"/" # <target>/
    if isOutput:
        CreateFolder(this_folder, "", False, False)

    return this_folder

def getPlotsFile(nameMethod, nameFileExt = "", fileExt = "root", plotBin = ""):
    this_file = nameMethod
    if nameFileExt:
        this_file+= "_"+get_name_format(nameFileExt, False)

    if (fileExt == "root"):
        if plotBin:
            this_file+="-"+plotBin+"."+fileExt  # Corr_Reconstructed_Fe_0B1-Fd.root
        else:
            this_file+="."+fileExt              # Corr_Reconstructed_Fe_0B1.root
    else:
        if plotBin:
            this_file+="-"+plotBin+"."+fileExt  # Corr_Reconstructed_Fe_0B1-Q0N0.gif (.pdf)
        else:
            this_file+="."+fileExt  # Corr_Reconstructed_Fe_0B1.gif (.pdf)

    return this_file

### /plots/Summary
########
def getSummaryPath(nameMethod, fileExt = "pdf", cuts = "", JLab_cluster = True, extra_path = "", name_folder = "Summary"):
    this_folder = "../macros/plots/"
    if JLab_cluster: this_folder+="JLab_cluster/"
    this_folder+="%s/"%(name_folder) ## +="Summary/"
    if extra_path:
        this_folder+=extra_path+"/"
    if cuts:
        # Remember: get_cut_long2final(cuts) has an underscore as first element
        this_folder+= get_cut_long2final(cuts)[1:] +"/"

    if not os.path.exists(this_folder):
        CreateFolder(this_folder, "", False, False)

    this_file = nameMethod
    if (cuts):
        these_cuts = get_cut_long2final(cuts)
        this_file+=these_cuts

    this_file+="."+fileExt

    return this_folder+this_file


#######################################
##  Define style and pad parameters  ##
#######################################

def ForceStyle(useCOLZ = False):
    ## Defining Style
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
    ROOT.gStyle.SetLabelSize(tsize-4,"x")
    ROOT.gStyle.SetTitleSize(tsize,"x")
    ROOT.gStyle.SetLabelSize(tsize-4,"y")
    ROOT.gStyle.SetTitleSize(tsize,"y")
    ROOT.gStyle.SetLabelSize(tsize-4,"z")
    ROOT.gStyle.SetTitleSize(tsize,"z")

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

    ROOT.gROOT.ForceStyle()

    if useCOLZ:
        ROOT.gStyle.SetPadRightMargin(2*marg)
        ROOT.gStyle.SetPadTopMargin(1.1*marg)
        ROOT.gStyle.SetLabelSize(tsize-10,"z")
        ROOT.gStyle.SetTitleYOffset(1.3)
        ROOT.gROOT.ForceStyle()

def GetMargin():
    return marg

def GetFont():
    return font

def GetSize():
    return tsize

def GetPadCenter():
    return (1 + marg)/2


#############################
##  Draw top text/summary  ##
#############################

def DrawTopLeft(text_bold = "", text = "", xl=0.0, yb=0.0):
    upLeft_text = ROOT.TLatex()
    upLeft_text.SetTextSize(tsize-4)
    upLeft_text.DrawLatexNDC(2*marg+0.005+xl,1-marg+0.01+yb,"#bf{%s} %s"%(text_bold,text))

def DrawTopRight(text_bold = "", text = "", xr=0.0, yb=0.0):
    upRight_text = ROOT.TLatex()
    upRight_text.SetTextSize(tsize-4)
    upRight_text.SetTextAlign(31)
    upRight_text.DrawLatexNDC(1-marg-0.005-xr,1-marg+0.01+yb,"#bf{%s} %s"%(text_bold,text))

def DrawPreliminaryInfo(text = "", xl=0.0, yb=0.0):
    DrawTopLeft(text, "Preliminary", xl, yb)

def DrawSummaryInfo(text = "", xl=0.0, yb=0.0):
    DrawTopLeft(text, "Summary", xl, yb)

def DrawTargetInfo(target="X", fileType="SimOrData"):
    if "targ" in target:
        DrawTopRight("%s, %s"%(target,fileType),"")
    else:
        DrawTopRight("%s target, %s"%(target,fileType),"")

def DrawBinInfo(bin_name="A0B1", bin_type=0, xR=0, yT=0):
    # Draw w.r.t. TopRight point (xR, yT)
    text = ROOT.TLatex()
    text.SetTextSize(tsize-4)
    text.SetTextAlign(33)
    title = GetBinInfo(bin_name, bin_type)
    if (xR==0 and yT==0):
        text.DrawLatexNDC(1-marg-0.005,1-marg-0.01,title)
    else:
        text.DrawLatexNDC(xR,yT,title)

def GetBinInfo(bin_name="A0B1", bin_type=0):
    tmp_txt = ""

    this_dict = all_dicts[bin_type]
    list_letters = bin_name[0::2]
    list_numbers = bin_name[1::2]

    for l,letter in enumerate(list_letters):
        num_index = int(list_numbers[l]) # 0 , 1
        vmin = this_dict[letter][num_index] # 0 , 1
        vmax = this_dict[letter][num_index+1] # 1 , 2
        tmp_txt+="%.2f < %s < %.2f"%(vmin, axis_label(letter,'Latex'), vmax)
        if l<(len(list_letters)-1):
            tmp_txt+="; "

    return tmp_txt


###############################
##  Plot markers and colors  ##
###############################

def GetColors(color_blind = False):
    colors_list = [416+2, 432+2, 600, 880, 632, 400+2, 600-3]
    ## [#kGreen+2, #kCyan+2, #kBlue, #kViolet, #kRed, #kYellow+2, #kBlue-3]
    if color_blind:
        color_RGB = [[51,34,136],[51,187,238],[17,119,51],[153,153,51],[204,102,119],[136,34,85],[128,128,128]]
        # [indigo, cyan, green, olive, rose, wine]
        
        for i in range(0,len(colors_list)):
            colors_list[i] = ROOT.TColor.GetColor(color_RGB[i][0],color_RGB[i][1],color_RGB[i][2])

    return colors_list

def GetMarkers(filled = False):
    ## [circle, square, triangle, diamond, star-inverse, inverse-triangle]
    marker_list = [24, 25, 26, 27, 30, 32] # Hollow option
    if filled:
        marker_list = [20, 21, 22, 33, 29, 23] # Filled option

    return marker_list

color_target = {'C': GetColors(True)[0], 'Fe': GetColors(True)[2], 'Pb': GetColors(True)[3], 'D': GetColors(True)[4],
                'DC': GetColors(True)[1], 'DFe': GetColors(True)[5], 'DPb': GetColors(True)[6]}


################################
##  Binning and dictionaries  ##
################################

# Copy dictionaries of bins from Bins.py
all_dicts = list(bn.Bin_List)

# Short name
varname2key = {
    "Q2":'Q', "Nu":'N', "Zh":'Z', "Pt2":'P', "PhiPQ":'I', "Xb":'X',
    "Pt":'P', "PQ":'I'
}

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
