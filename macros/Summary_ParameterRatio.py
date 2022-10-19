from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle
import math
import numpy as np
from array import array
import ctypes ## Needed to get pointer values

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
myStyle.ForceStyle()
# font=myStyle.GetFont()
tsize=myStyle.GetSize()

# gStyle.SetStatX(1 - myStyle.GetMargin() - 0.005)
# gStyle.SetStatY(2*myStyle.GetMargin() + 0.205)

def CanvasPartition(canvas, nx, ny, lMarg, rMarg, bMarg, tMarg, extra_name=""):
    ## Labelling xy:
    ##  ------------
    ##  - 02 12 22 -
    ##  - 01 11 21 -
    ##  - 00 10 20 -
    ##  ------------

    vSpacing = 0.0
    vStep  = (1.- bMarg - tMarg - (ny-1) * vSpacing) / ny
    
    hSpacing = 0.0
    hStep  = (1.- lMarg - rMarg - (nx-1) * hSpacing) / nx

    for i in range(nx):
        if (i==0):
            hposl = 0.0
            hposr = lMarg + hStep
            hfactor = hposr-hposl
            hmarl = lMarg / hfactor
            hmarr = 0.0
        elif (i == nx-1):
            hposl = hposr + hSpacing
            hposr = hposl + hStep + rMarg
            hfactor = hposr-hposl
            hmarl = 0.0
            hmarr = rMarg / (hposr-hposl)
        else:
            hposl = hposr + hSpacing
            hposr = hposl + hStep
            hfactor = hposr-hposl
            hmarl = 0.0
            hmarr = 0.0

        for j in range(ny):
            if (j==0):
                vposd = 0.0
                vposu = bMarg + vStep
                vfactor = vposu-vposd
                vmard = bMarg / vfactor
                vmaru = 0.0
            elif (j == ny-1):
                vposd = vposu + vSpacing
                vposu = vposd + vStep + tMarg
                vfactor = vposu-vposd
                vmard = 0.0
                vmaru = tMarg / (vposu-vposd)
            else:
                vposd = vposu + vSpacing
                vposu = vposd + vStep
                vfactor = vposu-vposd
                vmard = 0.0
                vmaru = 0.0

            canvas.cd(0)
            name = "pad%s_%i_%i"%(extra_name,i,j)
            pad = gROOT.FindObject(name)
            if pad: pad.Delete()
            pad = ROOT.TPad(name,"",hposl,vposd,hposr,vposu)

            pad.SetLeftMargin(hmarl)
            pad.SetRightMargin(hmarr)
            pad.SetBottomMargin(vmard)
            pad.SetTopMargin(vmaru)
    
            pad.SetFrameBorderMode(0)
            pad.SetBorderMode(0)
            pad.SetBorderSize(0)
    
            pad.Draw()

def XtoPad(x):
    xl, yd, xr, yu = ctypes.c_double(0.0), ctypes.c_double(0.0), ctypes.c_double(0.0), ctypes.c_double(0.0)
    gPad.GetPadPar(xl, yd, xr, yu)
    pw = xr.value-xl.value
    lm = gPad.GetLeftMargin()
    rm = gPad.GetRightMargin()
    fw = pw-pw*lm-pw*rm
    # print((x*fw+pw*lm)/pw)
    return (x*fw+pw*lm)/pw

def YtoPad(y):
    xl, yd, xr, yu = ctypes.c_double(0.0), ctypes.c_double(0.0), ctypes.c_double(0.0), ctypes.c_double(0.0)
    gPad.GetPadPar(xl, yd, xr, yu)
    ph = yu.value-yd.value
    tm = gPad.GetTopMargin()
    bm = gPad.GetBottomMargin()
    fh = ph-ph*bm-ph*tm
    return (y*fh+bm*ph)/ph


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-f', dest='fit',  default = "Fold", help="Use Fold (F), Left (L) or Right (R) fit")
parser.add_option('-s', dest='symmetric', action='store_true', default = False, help="Use symmetric y-limits (default False)")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

# saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
dataset_elemts = dataset.split("_")
if options.JLabCluster: rootpath = "JLab_cluster"
fit = options.fit
if fit=="Fold": fit="F"
use_sym = options.symmetric

try:
    if (int(dataset_elemts[0])):
        print("")
except:
    dataset = "%s_%s"%(dataset_elemts[1],dataset_elemts[2])
    print("")

this_binning_type = int(dataset[0])
this_bin_dict = myStyle.all_dicts[this_binning_type]

nBinsQ = len(this_bin_dict['Q']['Bins'])-1
nBinsN = len(this_bin_dict['N']['Bins'])-1
nBinsZ = len(this_bin_dict['Z']['Bins'])-1

gStyle.SetOptStat(0)
canvas_B = TCanvas("cvB","cvB",1000,800)
CanvasPartition(canvas_B, nBinsQ, nBinsN,2*myStyle.GetMargin(),myStyle.GetMargin(),2*myStyle.GetMargin(),myStyle.GetMargin(),"B")
canvas_B.SetGrid(0,1)

canvas_C = TCanvas("cvC","cvC",1000,800)
CanvasPartition(canvas_C, nBinsQ, nBinsN,2*myStyle.GetMargin(),myStyle.GetMargin(),2*myStyle.GetMargin(),myStyle.GetMargin(),"C")
canvas_C.SetGrid(0,1)

list_canvas = [canvas_B, canvas_C]

# par_list = ["B", "C"]
list_targets = ["C", "Fe", "Pb", "D"]
fold_or_LR = "Fold" if "F" in fit else "LR"
fit_num = 0 if (fit != "R") else 1

list_infiles = []

# Open files
for targ in list_targets:
    this_dataset = "%s_%s"%(targ, dataset)
    # infoDict = myStyle.getNameFormattedDict(this_dataset)
    nameFormatted = myStyle.getNameFormatted(this_dataset)

    inputPath = myStyle.getOutputDir("ParameterRatio",targ,rootpath)
    inputfile = TFile("%s%s_ParameterRatio_%s.root"%(inputPath,nameFormatted,fold_or_LR),"READ")
    list_infiles.append(inputfile)


list_hists = []

## Create histograms
for p,par in enumerate(["B", "C"]): # 3
    list_this_par = []
    for t,targ in enumerate(list_targets): # 4
        list_this_tar = []
        hist_par_Pos = list_infiles[t].Get("f_X_%s%i_Pos"%(par,fit_num))
        hist_par_Neg = list_infiles[t].Get("f_X_%s%i_Neg"%(par,fit_num))

        for iQ in range(nBinsQ): #nQ
            list_this_Q = []
            for iN in range(nBinsN): #nN
                bin_label = "Q%iN%i"%(iQ,iN)
                hist_tmp = TH1D("%s_%s_Q%iN%i"%(par,targ,iQ,iN),";Z_{h};%s/A"%(par),nBinsZ,array('d',this_bin_dict['Z']['Bins']))
                # hist_tmp_N = TH1D("%s_%s_Neg_Q%iN%i"%(par,targ,iQ,iN),";Z_{h};%s/A"%(par),nBinsZ,array('d',this_bin_dict['Z']['Bins']))

                for iZ in range(1,nBinsZ+1):
                    this_label = "%sZ%i"%(bin_label,iZ-1)
                    this_bin = hist_par_Pos.GetXaxis().FindBin(this_label)
                    bin_value = hist_par_Pos.GetBinContent(this_bin) if hist_par_Pos.GetBinContent(this_bin)>0.0 else -hist_par_Neg.GetBinContent(this_bin)
                    bin_error = hist_par_Pos.GetBinError(this_bin) if hist_par_Pos.GetBinContent(this_bin)>0.0 else hist_par_Neg.GetBinError(this_bin)

                    hist_tmp.SetBinContent(iZ, bin_value)
                    hist_tmp.SetBinError(iZ, bin_error)

                list_this_Q.append(hist_tmp)
            list_this_tar.append(list_this_Q)
        list_this_par.append(list_this_tar)
        # inputfile.Close()

    list_hists.append(list_this_par) #  npar*nTarg*nQ*nN = 3*4*nQ*nN hists

outputPath = myStyle.getOutputDir("Summary","",rootpath)

# par_y_lmts = [[-1.2,1.2], [-0.6,0.6]] if use_sym else [[-1.2,0.3], [-0.5,0.2]]
par_y_lmts = [[-1.199,1.199], [-0.599,0.599]] if use_sym else [[-1.199,0.299], [-0.499,0.199]]

for p,par in enumerate(["B", "C"]):
    this_canvas = list_canvas[p]
    this_canvas.cd(0)
    myStyle.DrawPreliminaryInfo("Summary %s/A ratio %s"%(par,fit))
    myStyle.DrawTargetInfo("All_targets", "Data")

    l_x1, l_x2 = 0.3, 0.7
    l_y1, l_y2 = 0.5, 0.7
    if not use_sym:
        l_y1 = 0.1
        l_y2 = 0.3
    legend = TLegend(l_x1, l_y1, l_x2, l_y2)
    legend.SetBorderSize(0)
    legend.SetTextFont(myStyle.GetFont())
    legend.SetTextSize(myStyle.GetSize()-14)
    legend.SetFillStyle(0)
    legend.SetNColumns(2)

    for t,targ in enumerate(list_targets):
        this_dataset = "%s_%s"%(targ, dataset)
        infoDict = myStyle.getNameFormattedDict(this_dataset)
        nameFormatted = myStyle.getNameFormatted(this_dataset)

        this_canvas.cd(0)

        for iQ in range(nBinsQ):
            for iN in range(nBinsN): # iQ,iN = 0,0
                this_pad = gROOT.FindObject("pad%s_%i_%i"%(par,iQ,nBinsN-iN-1)) # -> 0,2
                this_pad.SetGrid(0,1)

                ## This selection labels xy such as:
                ##  ------------     ------------
                ##  - 02 12 22 -     - 00 10 20 -
                ##  - 01 11 21 - --> - 01 11 21 -
                ##  - 00 10 20 -     - 02 12 22 -
                ##  ------------     ------------

                # this_pad.Draw()
                # this_pad.SetFillStyle(4000)
                # this_pad.SetFrameFillStyle(4000)
                this_pad.cd()

                this_hist = list_hists[p][t][iQ][iN]

                if (iQ!=0 and iN!=2): this_hist.GetYaxis().SetNoExponent(ROOT.kTRUE)

                this_hist.SetMinimum(par_y_lmts[p][0])
                this_hist.SetMaximum(par_y_lmts[p][1])
                this_hist.SetLabelSize(tsize-18,"xy")
                this_hist.SetTitleSize(tsize-14,"xy")
                this_hist.SetTitleOffset(2.5,"xy")

                this_hist.SetLineColor(myStyle.color_target[targ])
                this_hist.SetMarkerStyle(4)
                this_hist.SetMarkerColor(myStyle.color_target[targ])
                this_hist.Draw("e same")

                if (iN==2):
                    text = ROOT.TLatex()
                    text.SetTextSize(tsize-14)
                    text.SetTextAlign(23)
                    # title = myStyle.GetBinInfo("Q%iN%i"%(iQ,iN), this_binning_type)
                    title = myStyle.GetBinInfo("Q%i"%(iQ), this_binning_type)
                    text.DrawLatexNDC(XtoPad(0.5),YtoPad(-0.15),title)

                if (iQ==2):
                    text = ROOT.TLatex()
                    text.SetTextSize(tsize-14)
                    text.SetTextAlign(23)
                    text.SetTextAngle(90)
                    # title = myStyle.GetBinInfo("Q%iN%i"%(iQ,iN), this_binning_type)
                    title = myStyle.GetBinInfo("N%i"%(iN), this_binning_type)
                    text.DrawLatexNDC(XtoPad(1.05),YtoPad(0.5),title)

                if (iQ==2 and iN==0):
                    legend.AddEntry(this_hist,targ)
                    if (legend.GetListOfPrimitives().GetEntries()==len(list_targets)):
                        legend.Draw()

    this_canvas.cd(0)
    gPad.RedrawAxis("g")
    this_canvas.SaveAs("%sParRatio_%s_%s.gif"%(outputPath,par,fit))

for t,targ in enumerate(list_targets):
    list_infiles[t].Close()
