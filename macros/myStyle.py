import ROOT
import os

## Define global variables
marg=0.05
font=43 # Helvetica
# tsize=32
tsize=38 #35

### Names' formats
# Acceptance_%s_B%i.root      ; <Target>,<_binIndex>
# Corrected_%s_B%i_%iD.root   ; <Target>,<_binIndex>,<_binNdims (non-integrated dims)>
# ClosureTest_%s_B%i_%iD.root ; <Target>,<_binIndex>,<_binNdims (non-integrated dims)>

def getDictNameFormat(nameFormat):                  #input: <targ>_<nBin>_<nDim>   --->   <targ>_<nBin>B<nDim>
    targetDict = {}
    targetList = nameFormat.split("_")              # { <targ> , <nBin>, <nDim> }
    targetDict["Target"] = targetList[0]            # <targ>
    # binList = targetList[1].split("B")            # { <nBin> , <nDim> }
    targetDict["BinningType"] = int(targetList[1])  # <nBin>
    targetDict["NDims"] = int(targetList[2])        # <nDim>
    # targetDict["Cuts"] = []
    # if len(targetList)>3:
    #     numElem = len(targetList)
    #     for i in range(len(targetDict)-1,numElem):
    #         targetDict["Cuts"].append(targetList[i])
    return targetDict                               # <targ>_<nBin>B<nDim>

def getNameFormatted(nameFormat, isAcc = False): #input: Fe_0_1 ; <targ>_<nBin>_<nDim>
    formDict = getDictNameFormat(nameFormat)
    fileName = "%s_%iB"%(formDict["Target"],formDict["BinningType"])
    if (not isAcc) and formDict["NDims"]:
        fileName+="%i"%(formDict["NDims"])
    # if formDict["Cuts"]:
    #     for e in formDict["Cuts"]:
    #         fileName+="_"+e

    return fileName #output: Fe_0B1 ; <target>_<binningType number>B<non-integrated dimensions>

def addBeforeRootExt(path, before_dot, other_extension = "root"):
    new_path = path.split(".%s"%other_extension)[0]
    return new_path + before_dot + "." + other_extension

### Cuts
dict_Cut2Code = {"XF": "Xf", "Xf": "Xf",
                "DeltaSector": "DS", "DSect": "DS", "DSctr": "DS", "DS": "DS",
                # "Sector": "Se", "Sctr": "Se", "Sect": "Se", "Se": "Se",
                "FErr": "FE", "FullError": "FE", "FE": "FE",
                "Z": "Zx", "Zx": "Zx",
                "P": "Px", "Px": "Px",
                "Fold": "Fd", "Fd": "Fd",
                "LR": "LR",
                # "Left": "Lf", "Lf": "Lf",
                # "Right": "Rg", "Rg": "Rg",
                "MixD": "MD", "MD": "MD",
                }

dict_CutCode2Name = {"Xf": "Xf", "DS": "DSect0","FE": "FErr", "Zx": "Z", "Px": "P", "Fd": "Fold", "LR": "LR", "MD": "MixD", #"Lf": "Left", "Rg": "Right",
                    }
cutMasterKey = "Xf0DS0FE0Zx0Px0Fd0LR0MD0" # Yh0 ; Write options in order of applicability (Acc, Corr, Fit, Summary)

def getCutStrFormat(list_cuts):
    cut_str = ""
    for c in list_cuts:
        if (c[-1] == "0" or c == ""):
            continue
        this_cut = c
        if (len(c) == 3):
            this_cut = c[0:2]
        cut_str+="_"+dict_CutCode2Name[this_cut]
    return cut_str

def getCutStrFromStr(cut_str = ""): # Aaaa_Bbb_ccc_Ddd
    # Format: AA0BB1CC0EE1
    #           AA: First two letters of the cut name
    #           0 or 1: Do (1) or don't (0) apply cut
    this_Key = cutMasterKey
    this_list = this_Key.split("0")
    this_list.remove("")

    ref_list = list(this_list)

    list_input = cut_str.split("_")
    while ("" in list_input):
        list_input.remove("") # = cut_str.split("_")[1:-1]

    for elem in list_input:
        try:
            if dict_Cut2Code[elem]:
                this_index = ref_list.index(dict_Cut2Code[elem])
                this_list[this_index] = dict_Cut2Code[elem]+"1"
        except:
            if (("Left" in elem) or ("Right" in elem)):
                continue
            else:
                print("Cut not found! : %s"%(elem))
                exit()

    for elem in this_list:
        if (elem[-1] != "1"):
            this_index = ref_list.index(elem)
            this_list[this_index] = elem+"0"
    # print(this_list)
    this_str = getCutStrFormat(this_list)
    # print(this_str)
    return this_str

def getCutsAsList(this_cut_str): # Intro should be output of getCutStrFormat()
    this_list = this_cut_str.split("_")
    while ("" in this_list):
        this_list.remove("")
    return this_list

### Paths and directories' functions
### /output/
def getOutputFolder(nameMethod, extraCuts = "", JLab_cluster = True, isOutput = True):
    this_folder = "../output/"
    if JLab_cluster: this_folder+="JLab_cluster/"

    these_cuts = getCutStrFromStr(extraCuts)
    this_folder+=nameMethod+these_cuts+"/"
    if isOutput:
        CreateFolder(this_folder, "", False, False)
    return this_folder

def getOutputFile(nameMethod, nameFileExt):
    if nameMethod=="Acceptance":
        this_file = "Acceptance_"+getNameFormatted(nameFileExt, True)+".root"
    elif nameMethod=="Correction":
        this_file = "Corrected_"+getNameFormatted(nameFileExt, False)+".root"
    elif nameMethod=="Hist2D":
        this_file = "Hist2D_"+getDictNameFormat(nameFileExt)["Target"]+"_.root" # Remember to add "data" or "hsim" with addBeforeRootExt()
    else:
        this_file = nameMethod+"_"+getNameFormatted(nameFileExt, False)+".root"

    return this_file

def getOutputFileWithPath(nameMethod, nameFileExt, extraCuts = "", JLab_cluster = True, isOutput = True):
    this_path = getOutputFolder(nameMethod, extraCuts, JLab_cluster, isOutput) # "../<out>/"
    this_file = getOutputFile(nameMethod, nameFileExt)

    return this_path+this_file

### /plots/
def getPlotsFolder(nameMethod, extraCuts = "", extraPath = "", JLab_cluster = True, isOutput = True):
    this_folder = "../macros/plots/"
    if JLab_cluster: this_folder+="JLab_cluster/"

    these_cuts = getCutStrFromStr(extraCuts)
    this_folder+=nameMethod+these_cuts+"/"
    if extraPath:
        this_folder+=extraPath+"/" # <target>/
    if isOutput:
        CreateFolder(this_folder, "", False, False)
    return this_folder

def getPlotsFile(nameMethod, nameFileExt, fileExt = "root", plotBin = ""):
    this_file = nameMethod+"_"+getNameFormatted(nameFileExt, False)
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
def getSummaryPath(nameMethod, fileExt = "pdf", cuts = "", JLab_cluster = True):
    this_folder = "../macros/plots/"
    if JLab_cluster: this_folder+="JLab_cluster/"
    this_folder+="Summary/"

    if not os.path.exists(this_folder):
        CreateFolder(this_folder, "", False, False)

    this_file = nameMethod
    if (cuts):
        these_cuts = getCutStrFromStr(cuts)
        this_file+=these_cuts

    this_file+="."+fileExt
    return this_folder+this_file

###
def CreateFolder(outdir, title, overwrite = False, enumerate = True):
    outdir2 = os.path.join(outdir,title)

    if overwrite:
        os.makedirs(outdir2)
        print(outdir2,"created.")
    else:
        if not os.path.exists(outdir2):
            os.makedirs(outdir2)
            print(outdir2,"created.")
        elif enumerate:
            i = 1
            while(os.path.exists(outdir2)):
                    outdir2 = outdir2[0:-2] + str(i) + outdir2[-1]
                    i+=1
            os.mkdir(outdir2)
            print(outdir2,"created.")
        else:
            print(outdir2," already exists!")
    return outdir2

### Style functions
def ForceStyle():
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


def DrawPreliminaryInfo(text = ""):
    upLeft_text = ROOT.TLatex()
    upLeft_text.SetTextSize(tsize-4)
    upLeft_text.DrawLatexNDC(2*marg+0.005,1-marg+0.01,"#bf{%s} Preliminary"%(text))

    # prelimilar = ROOT.TLatex()
    # prelimilar.SetTextSize(tsize-4)
    # prelimilar.DrawLatexNDC(2*marg+0.005,1-marg+0.01,"#bf{Preliminary}")

def DrawSummaryInfo(text = ""):
    upLeft_text = ROOT.TLatex()
    upLeft_text.SetTextSize(tsize-4)
    upLeft_text.DrawLatexNDC(2*marg+0.005,1-marg+0.01,"#bf{%s} Summary"%(text))

def DrawTargetInfo(target="X", fileType="SimOrData"):
    text = ROOT.TLatex()
    text.SetTextSize(tsize-4)
    text.SetTextAlign(31)
    nameCode = target.split("_")
    if len(nameCode)==1: text.DrawLatexNDC(1-marg-0.005,1-marg+0.01,"#bf{"+str(target) + " target, "+str(fileType)+"}")
    else:                text.DrawLatexNDC(1-marg-0.005,1-marg+0.01,"#bf{"+str(target) + ", "+str(fileType)+"}")

def DrawBinInfo(bin_name="X0X0", bin_type=0, xR=0, yT=0):
    text = ROOT.TLatex()
    text.SetTextSize(tsize-4)
    text.SetTextAlign(33)
    title = GetBinInfo(bin_name, bin_type)
    # text.DrawLatexNDC(1-marg-0.005,1-marg-0.01,"#bf{"+title+"}")
    if (xR==0 and yT==0): text.DrawLatexNDC(1-marg-0.005,1-marg-0.01,title)
    else: text.DrawLatexNDC(xR,yT,title)

def GetBinInfo(bin_name="X0X0", bin_type=0):
    tmp_txt = ""

    this_dict = all_dicts[bin_type]
    for i,c in enumerate(bin_name): # "A0B1"
        if i%2 == 0: # A , B
            num_index = int(bin_name[i+1]) # 0 , 1
            vmin = this_dict[c]['Bins'][num_index] # 0 , 1
            vmax = this_dict[c]['Bins'][num_index+1] # 1 , 2
            tmp_txt+="%.2f < %s < %.2f"%(vmin, this_dict[c]['Name'], vmax)
            if i<(len(bin_name)-2): tmp_txt+="; "
    return tmp_txt

def GetMargin():
    return marg

def GetFont():
    return font

def GetSize():
    return tsize

def GetPadCenter():
    return (1 + marg)/2

def GetColors(color_blind = False):
    colors_list = [416+2, 432+2, 600, 880, 632, 400+2, 600-3]
    ## [#kGreen+2, #kCyan+2, #kBlue, #kViolet, #kRed, #kYellow+2, #kBlue-3]
    if color_blind:
        color_RGB = [[51,34,136],[51,187,238],[17,119,51],[153,153,51],[204,102,119],[136,34,85],[128,128,128]]
        # [indigo, cyan, green, olive, rose, wine]
        
        for i in range(0,len(colors_list)):
            colors_list[i] = ROOT.TColor.GetColor(color_RGB[i][0],color_RGB[i][1],color_RGB[i][2])

    return colors_list

color_target = {'C': GetColors(True)[0], 'Fe': GetColors(True)[2], 'Pb': GetColors(True)[3], 'D': GetColors(True)[4],
                'DC': GetColors(True)[1], 'DFe': GetColors(True)[5], 'DPb': GetColors(True)[6]}

bin_dict        = { 'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
                    'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
                    'Z': {'Name': "Z_{h}",      'Bins': [0.00, 0.15, 0.25, 0.40, 0.70, 1.00]},
                    'P': {'Name': "P_{t}^{2}",  'Bins': [0.00, 0.03, 0.06, 0.10, 0.18, 1.00]}}

bin_dict_SplitZ = { 'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
                    'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
                    'Z': {'Name': "Z_{h}",      'Bins': [0.00, 0.15, 0.25, 0.40, 0.70, 0.90, 1.00]},
                    'P': {'Name': "P_{t}^{2}",  'Bins': [0.00, 0.03, 0.06, 0.10, 0.18, 1.00]}}

bin_dict_ThinZh = { 'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
                    'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
                    'Z': {'Name': "Z_{h}",      'Bins': [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]},
                    'P': {'Name': "P_{t}^{2}",  'Bins': [0.00, 0.03, 0.06, 0.10, 0.18, 1.00]}}

bin_dict_ThinPt = { 'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
                    'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
                    'Z': {'Name': "Z_{h}",      'Bins': [0.00, 0.15, 0.25, 0.40, 0.70, 0.90, 1.00]},
                    'P': {'Name': "P_{t}^{2}",  'Bins': [0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0]}}

bin_dict_ThinZP = { 'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
                    'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
                    'Z': {'Name': "Z_{h}",      'Bins': [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]},
                    'P': {'Name': "P_{t}^{2}",  'Bins': [0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0]}}

bin_dict_ThinZh_CoarsePhi = {   'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
                                'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
                                'Z': {'Name': "Z_{h}",      'Bins': [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]},
                                'P': {'Name': "P_{t}^{2}",  'Bins': [0.00, 0.03, 0.06, 0.10, 0.18, 1.00]},
                                'I': {'Name': "#phi_{PQ}", 'Bins': [-180.00, -162.00, -144.00, -126.00, -108.00, -90.00, -72.00, -54.00,
                                                                     -36.00, -18.00, 0.00, 18.00, 36.00, 54.00, 72.00, 90.00, 108.00,
                                                                     126.00, 144.00, 162.00, 180.00]}}

bin_dict_ThinZP_CoarsePhi = {   'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
                                'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
                                'Z': {'Name': "Z_{h}",      'Bins': [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]},
                                'P': {'Name': "P_{t}^{2}",  'Bins': [0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0]},
                                'I': {'Name': "#phi_{PQ}", 'Bins': [-180.00, -162.00, -144.00, -126.00, -108.00, -90.00, -72.00, -54.00,
                                                                     -36.00, -18.00, 0.00, 18.00, 36.00, 54.00, 72.00, 90.00, 108.00,
                                                                     126.00, 144.00, 162.00, 180.00]}}

bin_dict_ThinZP_OddPhi = {  'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
                            'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
                            'Z': {'Name': "Z_{h}",      'Bins': [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]},
                            'P': {'Name': "P_{t}^{2}",  'Bins': [0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0]},
                            'I': {'Name': "#phi_{PQ}",  'Bins': [-180.00, -156.00, -132.00, -108.00, -84.00, -60.00, -36.00, -12.00,
                                                                   12.00, 36.00, 60.00, 84.00, 108.00, 132.00, 156.00, 180.00]}}

all_dicts = [   bin_dict, bin_dict_SplitZ, bin_dict_ThinZh, bin_dict_ThinPt, bin_dict_ThinZP, bin_dict_ThinZh_CoarsePhi,
                bin_dict_ThinZP_CoarsePhi, bin_dict_ThinZP_OddPhi]

kin_vars_list = [   ["Q2", "Nu", "Zh", "Pt2", "PhiPQ"],
                    ["Q^{2}", "#nu", "Z_{h}", "P_{t}^{2}", "#phi_{PQ}"],
                    ["(GeV^{2})", "(GeV)", "", "(GeV^{2})", "(deg)"]]
