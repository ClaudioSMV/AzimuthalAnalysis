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

def getNameFormattedDict(nameFormat): #input: <target>_<binningType number>_<non-integrated dimensions>
    targetDict = {}
    targetList = nameFormat.split("_")
    targetDict["Target"] = targetList[0]
    targetDict["BinningType"] = int(targetList[1])
    if targetList[2]: targetDict["NDims"] = int(targetList[2])

    return targetDict

def getNameFormatted(nameFormat):
    formDict = getNameFormattedDict(nameFormat)
    fileName = "%s_B%i"%(formDict["Target"],formDict["BinningType"])
    if formDict["NDims"]:
        fileName+="_%iD"%(formDict["NDims"])

    return fileName #output: <target>_B<binningType number>_<non-integrated dimensions>D


### Paths and directories' functions
def getInputFile(nameMethod,nameFormat):
    indir = "../output/%s/" % nameMethod # ex. Acceptance, Correction
    fileName = getNameFormatted(nameFormat)
    file = "%s_%s"%(nameMethod,fileName)
    return indir+file+".root"

def getOutputDir(nameMethod):
    outdir = "../macros/plots/%s/" % nameMethod
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
    upLeft_text.DrawLatexNDC(2*marg+0.005,1-marg+0.01,"#bf{%s}"%(text))

    prelimilar = ROOT.TLatex()
    prelimilar.SetTextSize(tsize-4)
    prelimilar.DrawLatexNDC(2*marg+0.005,1-marg+0.01,"#bf{Preliminary}")

def DrawTargetInfo(target="X", fileType="SimOrData"):
    text = ROOT.TLatex()
    text.SetTextSize(tsize-4)
    text.SetTextAlign(31)
    text.DrawLatexNDC(1-marg-0.005,1-marg+0.01,"#bf{"+str(target) + " target, "+str(fileType)+"}")

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