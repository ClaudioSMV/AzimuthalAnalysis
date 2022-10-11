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

def getNameFormattedDict(nameFormat): #input: <target>_<binningType number>_<non-integrated dimensions>_<extra cuts>
    targetDict = {}
    targetList = nameFormat.split("_")
    targetDict["Target"] = targetList[0]
    targetDict["BinningType"] = int(targetList[1])
    targetDict["NDims"] = int(targetList[2])
    targetDict["Cuts"] = []
    if len(targetList)>3:
        numElem = len(targetList)
        for i in range(len(targetDict)-1,numElem):
            targetDict["Cuts"].append(targetList[i])
    return targetDict

def getNameFormatted(nameFormat, isAcc = False):
    formDict = getNameFormattedDict(nameFormat)
    fileName = "%s_B%i"%(formDict["Target"],formDict["BinningType"])
    if (not isAcc) and formDict["NDims"]:
        fileName+="_%iD"%(formDict["NDims"])
    if formDict["Cuts"]:
        for e in formDict["Cuts"]:
            fileName+="_"+e

    return fileName #output: <target>_B<binningType number>_<non-integrated dimensions>D_<extra cuts>


### Paths and directories' functions
def getInputFile(nameMethod,nameFormat, extra_path=""):
    if extra_path: extra_path+="/"
    indir = "../output/%s%s/" % (extra_path,nameMethod) # ex. Acceptance, Correction

    fileName = getNameFormatted(nameFormat)
    # Default as ClosureTest_Fe_B0_2D
    file = "%s_%s"%(nameMethod,fileName)
    if nameMethod=="Acceptance":
        fileName = getNameFormatted(nameFormat, True)
        file = "Acceptance_%s"%(fileName)
    elif nameMethod=="Correction": file = "Corrected_%s"%(fileName)
    elif nameMethod=="Hist2D":
        file = "KinVars_%s_"%(getNameFormattedDict(nameFormat)["Target"])
        return indir+file # Still needs "data" or "hsim" + .root
    return indir+file+".root"

def getOutputDir(nameMethod, target="", extra_path=""):
    if extra_path: extra_path+="/"
    outdir = "../macros/plots/%s%s/" % (extra_path,nameMethod)
    if target: outdir+=target+"/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    return outdir

def CreateFolder(outdir, title, overwrite = False):
    outdir2 = os.path.join(outdir,title)

    if overwrite:
        os.mkdir(outdir2)
    else:
        if not os.path.exists(outdir2):
                os.mkdir(outdir2)
        else:
            i = 1
            while(os.path.exists(outdir2)):
                    outdir2 = outdir2[0:-2] + str(i) + outdir2[-1]
                    i+=1
            os.mkdir(outdir2)
    print(outdir2,"created.")
    return outdir2

def GetPlotsDir(outdir, macro_title):
    outdir_tmp = os.path.join(outdir, macro_title)
    if not (os.path.exists(outdir_tmp)):
        outdir_tmp = CreateFolder(outdir, macro_title, True)

    return outdir_tmp

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

def DrawTargetInfo(target="X", fileType="SimOrData"):
    text = ROOT.TLatex()
    text.SetTextSize(tsize-4)
    text.SetTextAlign(31)
    nameCode = target.split("_")
    if len(nameCode)==1: text.DrawLatexNDC(1-marg-0.005,1-marg+0.01,"#bf{"+str(target) + " target, "+str(fileType)+"}")
    else:                text.DrawLatexNDC(1-marg-0.005,1-marg+0.01,"#bf{"+str(target) + ", "+str(fileType)+"}")

def DrawBinInfo(bin_name="X0X0"):
    text = ROOT.TLatex()
    text.SetTextSize(tsize-4)
    text.SetTextAlign(33)
    title = GetBinInfo(bin_name)
    # text.DrawLatexNDC(1-marg-0.005,1-marg-0.01,"#bf{"+title+"}")
    text.DrawLatexNDC(1-marg-0.005,1-marg-0.01,title)

def GetBinInfo(bin_name="X0X0"):
    tmp_txt = ""
    for i,c in enumerate(bin_name):
        if i%2 == 0:
            num_index = int(bin_name[i+1])
            vmin = bin_dict[c]['Bins'][num_index]
            vmax = bin_dict[c]['Bins'][num_index+1]
            tmp_txt+="%.2f < %s < %.2f"%(vmin, bin_dict[c]['Name'], vmax)
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

bin_dict = {'Q': {'Name': "Q^{2}",      'Bins': [1.00, 1.30, 1.80, 4.10]},
            'N': {'Name': "#nu",        'Bins': [2.20, 3.20, 3.70, 4.20]},
            'Z': {'Name': "Z_{h}",      'Bins': [0.00, 0.15, 0.25, 0.40, 0.70, 0.90, 1.00]}, # REMEMBER TO UPDATE THIS SO WE CAN CHENGE BETWEEN DIFFERENT BINNINGS
            'P': {'Name': "P_{t}^{2}",  'Bins': [0.00, 0.03, 0.06, 0.10, 0.18, 1.00]}}

kin_vars_list = [   ["Q2", "Nu", "Zh", "Pt2", "PhiPQ"],
                    ["Q^{2}", "#nu", "Z_{h}", "P_{t}^{2}", "#phi_{PQ}"],
                    ["(GeV^{2})", "(GeV)", "", "(GeV^{2})", "(deg)"]]
