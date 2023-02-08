import ROOT
import os
import Bins as bn

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
    targetList = nameFormat.split("_")              # [ <targ> , <nBin>, <nDim> ]
    targetDict["Target"] = targetList[0]            # <targ>
    # binList = targetList[1].split("B")            # { <nBin> , <nDim> }
    targetDict["BinningType"] = int(targetList[1])  # <nBin>
    if (len(targetList)==2):
        targetList.append(0)
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
                "BadSector": "BS", "rmBadSector": "BS", "BS": "BS",
                "PionFiducial": "PF", "PiFiducial": "PF", "PF": "PF",
                # "Sector": "Se", "Sctr": "Se", "Sect": "Se", "Se": "Se",
                "FErr": "FE", "FullError": "FE", "FE": "FE",
                "Z": "Zx", "Zx": "Zx",
                "P": "Px", "Px": "Px",
                "useSin": "Fs", "FitSin": "Fs", "Fs": "Fs",
                "Fold": "Fd", "Fd": "Fd",
                "LR": "LR",
                # "Left": "Lf", "Lf": "Lf",
                # "Right": "Rg", "Rg": "Rg",
                "MixD": "MD", "MD": "MD",
                }

dict_CutCode2Name = {   "Xf": "Xf", "DS": "DSect0", "BS": "NoBadSec", "PF": "PiFid", "FE": "FErr",
                        "Zx": "Z", "Px": "P",
                        "Fs": "Sin", "Fd": "Fold", "LR": "LR", "MD": "MixD", #"Lf": "Left", "Rg": "Right",
                    }
cutMasterKey = "Xf0DS0BS0PF0FE0Zx0Px0Fs0Fd0LR0MD0" # Yh0 ; Write options in order of applicability (Acc, Corr, Fit, Summary)

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
def getSummaryPath(nameMethod, fileExt = "pdf", cuts = "", JLab_cluster = True, extra_path = ""):
    this_folder = "../macros/plots/"
    if JLab_cluster: this_folder+="JLab_cluster/"
    this_folder+="Summary/"
    if extra_path:
        this_folder+=extra_path+"/"

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


def DrawPreliminaryInfo(text = "", xl=0.0, yb=0.0):
    upLeft_text = ROOT.TLatex()
    upLeft_text.SetTextSize(tsize-4)
    upLeft_text.DrawLatexNDC(2*marg+0.005+xl,1-marg+0.01+yb,"#bf{%s} Preliminary"%(text))

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
    if "targ" not in target: text.DrawLatexNDC(1-marg-0.005,1-marg+0.01,"#bf{"+str(target) + " target, "+str(fileType)+"}")
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
            vmin = this_dict[c][num_index] # 0 , 1
            vmax = this_dict[c][num_index+1] # 1 , 2
            tmp_txt+="%.2f < %s < %.2f"%(vmin, axis_label(c,'Latex'), vmax)
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

# Copy dictionaries of bins from Bins.py
all_dicts = list(bn.Bin_List)

varname2key = { "Q2":'Q', "Nu":'N', "Zh":'Z', "Pt2":'P', "PhiPQ":'I', "Xb":'X',
                "Pt":'P', "PQ":'I'} # Short name

#        <initial> : [<name>,   <axis_name_latex>, <units>  ]
var_label = {   'Q': ["Q2",     "Q^{2}",        "(GeV^{2})" ],
                'N': ["Nu",     "#nu",          "(GeV)"     ],
                'Z': ["Zh",     "Z_{h}",        ""          ],
                'P': ["Pt2",    "P_{t}^{2}",    "(GeV^{2})" ],
                'I': ["PhiPQ",  "#phi_{PQ}",    "(deg)"     ],
                'X': ["Xb",     "X_{b}",        ""          ],}

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
