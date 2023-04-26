from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
from array import array
import ctypes ## Needed to get pointer values

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
ms.ForceStyle()
# font=ms.GetFont()
tsize=ms.GetSize()

# gStyle.SetStatX(1 - ms.GetMargin() - 0.005)
# gStyle.SetStatY(2*ms.GetMargin() + 0.205)

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
    # print("xl: %.2f; yd: %.2f; xr: %.2f; yu: %.2f;"%(xl.value, yd.value, xr.value, yu.value))
    pw = xr.value-xl.value
    lm = gPad.GetLeftMargin()
    rm = gPad.GetRightMargin()
    fw = pw-pw*lm-pw*rm
    # print("pw: %.2f; lm: %.2f; rm: %.2f; fw: %.2f; x2pad: %.2f"%(pw, lm, rm, fw, (x*fw+pw*lm)/pw))
    return (x*fw+pw*lm)/pw

def YtoPad(y):
    xl, yd, xr, yu = ctypes.c_double(0.0), ctypes.c_double(0.0), ctypes.c_double(0.0), ctypes.c_double(0.0)
    gPad.GetPadPar(xl, yd, xr, yu)
    ph = yu.value-yd.value
    tm = gPad.GetTopMargin()
    bm = gPad.GetBottomMargin()
    fh = ph-ph*bm-ph*tm
    # print("ph: %.2f; tm: %.2f; bm: %.2f; fh: %.2f; y2pad: %.2f"%(ph, tm, bm, fh, (y*fh+bm*ph)/ph))
    return (y*fh+bm*ph)/ph


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_Z/P...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")

parser.add_option('-y', dest='y_symmetric', action='store_true', default = False, help="Use symmetric y-limits (default False)")
# parser.add_option('-s', dest='solidTargets', action='store_true', default = False, help="Draw only solid targets (default adds D)")
# parser.add_option('-a', dest='allDSplit', action='store_true', default = False, help="Draw only deuterium for different solid targets")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
rootpath = options.rootpath
isJLab = options.JLabCluster

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

useZh = False
usePt2 = False
if ("Z" in ms.get_cut_str2finallist(plots_cuts)):
    useZh = True
if ("P" in ms.get_cut_str2finallist(plots_cuts)):
    usePt2 = True

if (useZh) and (usePt2):
    print("  [SummaryNorm] Two binning selected. Please, choose only one of the options!")
    exit()
elif (not useZh) and (not usePt2):
    print("  [SummaryNorm] Select Zx or Px as x binning!")
    exit()

keyX = 'Z' if useZh else 'P'

## Define target and binning
infoDict = ms.get_name_dict(dataset)
nameFormatted = ms.get_name_format(dataset)
this_targ = infoDict["Target"]
this_binning = infoDict["BinningType"]
this_bin_dict = ms.all_dicts[this_binning]

key1 = 'N' if ("N" in this_bin_dict) else 'X'

nBinsQ = len(this_bin_dict['Q'])-1
nBinsN = len(this_bin_dict[key1])-1
nBinsZ = len(this_bin_dict['Z'])-1
nBinsP = len(this_bin_dict['P'])-1

gStyle.SetOptStat(0)
canvas_B = TCanvas("cvB","cvB",1000,800)
CanvasPartition(canvas_B, nBinsQ, nBinsN,2*ms.GetMargin(),ms.GetMargin(),2*ms.GetMargin(),ms.GetMargin(),"B")
canvas_B.SetGrid(0,1)

canvas_C = TCanvas("cvC","cvC",1000,800)
CanvasPartition(canvas_C, nBinsQ, nBinsN,2*ms.GetMargin(),ms.GetMargin(),2*ms.GetMargin(),ms.GetMargin(),"C")
canvas_C.SetGrid(0,1)

list_canvas = [canvas_B, canvas_C]

list_fitmethods = ["Full", "Right", "Left", "Fold", "Shift"]
list_fitmethodsKey = ["Ff", "LR_Right", "LR_Left", "Fd", "Sh"]

list_infiles = []

# Open files
for fm in list_fitmethodsKey:
    # this_dataset = "%s_%s"%(targ, dataset) # = nameFormatted

    this_input_cuts = input_cuts + "_%s"%fm

    tmp_methods_list = fm.split("_") # ["Ff"], ["LR", "Right"], ["LR", "Left"], ...
    this_meth = tmp_methods_list[0]
    try:
        meth_detail = tmp_methods_list[1]
    except:
        meth_detail = ""

    inputPath = ms.getPlotsFolder("ParametersNorm", this_input_cuts, ms.get_name_format_bin(dataset) +"/"+ this_targ, isJLab, False) # "../output/"
    inputROOT = ms.getPlotsFile("Parameters", dataset, "root", this_meth)

    inputfile = TFile(inputPath+inputROOT,"READ")
    list_infiles.append(inputfile)


# Define variables for different x-axis (Zh or Pt2)

x_axis_title = ms.axis_label(keyX,"LatexUnit") # "Z_{h}" or "P_{t}^{2} (GeV^{2})"
this_n = nBinsZ if useZh else nBinsP

type_reco_short = ["Reco", "RMmc", "RMre"]

list_type_reco = []

# fancy_par = ["A^{UU}_{cos#phi}", "A^{UU}_{cos(2#phi)}"]
# wt = 1.
fancy_par = ["#LTcos#phi#GT_{eA}", "#LTcos2#phi#GT_{eA}"] if "D" not in this_targ else ["#LTcos#phi#GT_{eD}", "#LTcos2#phi#GT_{eD}"]
wt = 2.

## Create histograms
for r,typeR in enumerate(type_reco_short):
    list_hists = []
    for p,par in enumerate(["B", "C"]): # 2
        list_this_par = []
        for m,meth in enumerate(list_fitmethodsKey): # 4
            list_this_meth = []

            fit_num = 0 if not "Left" in meth else 1
            hist_par = list_infiles[m].Get("f_Norm_%s%i_%s"%(par,fit_num,typeR))

            # This is in case the Reco method found is not used, so unnecessary files are not created
            if not hist_par:
                print("  [SummaryNorm_DiffFit] %s hist not found. Skipping!"%typeR)
                type_reco_short[r] = 0 # Skip reco method when does not exist!
                break

            for iQ in range(nBinsQ): #nQ
                list_this_Q = []
                for iN in range(nBinsN): #nN
                    bin_label = "Q%i%s%i"%(iQ,key1,iN) # "Q%iN%i" or "Q%iX%i"

                    hist_tmp = TH1D("%s_%s_%s-%s"%(typeR,par,this_targ,bin_label),";%s;%s"%(x_axis_title,fancy_par[p]),this_n,array('d',this_bin_dict[keyX]))
                    for i_n in range(1,this_n+1):
                        this_label = "%s%s%i"%(bin_label, keyX, i_n-1) # "Q0N0Z0" or "Q0X0P0"
                        this_bin = hist_par.GetXaxis().FindBin(this_label)
                        bin_value = hist_par.GetBinContent(this_bin)
                        bin_error = hist_par.GetBinError(this_bin)

                        hist_tmp.SetBinContent(i_n, bin_value/wt)
                        hist_tmp.SetBinError(i_n, bin_error)

                    list_this_Q.append(hist_tmp)
                list_this_meth.append(list_this_Q)
            list_this_par.append(list_this_meth)

        list_hists.append(list_this_par) #  npar*nTarg*nQ*nN = 2*4*nQ*nN hists
    list_type_reco.append(list_hists)

# par_y_lmts = [[-1.199,0.299], [-0.499,0.199]] if not usePt2 else [[-0.399,0.199], [-0.149,0.149]]
par_y_lmts = [[-0.599,0.099], [-0.299,0.099]] if not usePt2 else [[-0.299,0.049], [-0.049,0.099]]
Q2_bin_info_Ypos = -0.15 if not usePt2 else -0.22

fancy_uptitle = ["First asymmetry", "Second asymmetry"]

frst_binmiddle = (this_bin_dict[keyX][1] + this_bin_dict[keyX][0])/2.
last_binmiddle = (this_bin_dict[keyX][-1] + this_bin_dict[keyX][-2])/2.
axis_hist = TH1D("axis_hist","",1, frst_binmiddle-0.05,last_binmiddle+0.05) #this_bin_dict[keyX][0] - last_binhalfwidth, this_bin_dict[keyX][-1] + frst_binhalfwidth)

axis_hist.SetLabelSize(tsize-20,"xy")
axis_hist.SetTitleSize(tsize-16,"xy")
axis_hist.SetTitleOffset(1.0,"x")
axis_hist.SetTitleOffset(1.8,"y")

## Style
l_color = ms.GetColors(True)
list_marker = ms.GetMarkers()

for r,typeR in enumerate(type_reco_short):
    if typeR==0: # Skip reco method when does not exist!
        continue

    for p,par in enumerate(["B", "C"]):
        this_canvas = list_canvas[p]
        this_canvas.cd(0)
        # ms.DrawSummaryInfo("Norm %s/A Diff methods"%(par))
        ms.DrawSummaryInfo("%s multi fit"%(fancy_uptitle[p]))
        ms.DrawTargetInfo(this_targ, "Data")

        ## Legend
        legQ, legN = 2, 0
        legend_pad = gROOT.FindObject("pad%s_%i_%i"%(par,legQ,legN))
        legend_pad.cd()

        l_x1, l_x2 = XtoPad(0.1), XtoPad(0.9)
        l_y1, l_y2 = YtoPad(0.0), YtoPad(0.3)

        if (key1=='X'):
            l_x1, l_x2 = XtoPad(0.1), XtoPad(0.9)
            l_y1, l_y2 = YtoPad(0.7), YtoPad(0.9)

        legend = TLegend(l_x1, l_y1, l_x2, l_y2)
        legend.SetBorderSize(0)
        legend.SetTextFont(ms.GetFont())
        legend.SetTextSize(ms.GetSize()-14)
        legend.SetFillStyle(0)
        legend.SetTextAlign(22)
        legend.SetNColumns(3)
        this_canvas.cd(0)

        new_pad = True
        axis_hist.SetMinimum(par_y_lmts[p][0])
        axis_hist.SetMaximum(par_y_lmts[p][1])

        for m,meth in enumerate(list_fitmethodsKey):
            this_canvas.cd(0)
            for iQ in range(nBinsQ):
                for iN in range(nBinsN): # iQ,iN = 0,0 (B)
                    this_pad = gROOT.FindObject("pad%s_%i_%i"%(par,iQ,iN)) # -> 0,0 (A)
                    this_pad.SetGrid(0,1)

                    ## This selection labels xy such as:
                    ##       (A)              (B)
                    ##  ------------     ------------
                    ##  - 02 12 22 -     - 02 12 22 -
                    ##  - 01 11 21 - <-> - 01 11 21 -
                    ##  - 00 10 20 -     - 00 10 20 -
                    ##  ------------     ------------

                    # this_pad.Draw()
                    # this_pad.SetFillStyle(4000)
                    # this_pad.SetFrameFillStyle(4000)
                    this_pad.cd()

                    this_hist = list_type_reco[r][p][m][iQ][iN]

                    if (iQ!=0 and iN!=2): this_hist.GetYaxis().SetNoExponent(ROOT.kTRUE)

                    this_hist.SetMinimum(par_y_lmts[p][0])
                    this_hist.SetMaximum(par_y_lmts[p][1])
                    # this_hist.SetLabelSize(tsize-18,"xy")
                    # this_hist.SetTitleSize(tsize-14,"xy")
                    # this_hist.SetTitleOffset(2.5,"xy")
                    this_hist.SetLabelSize(tsize-20,"xy")
                    this_hist.SetTitleSize(tsize-16,"xy")
                    this_hist.SetTitleOffset(1.0,"x")
                    this_hist.SetTitleOffset(1.8,"y")

                    this_hist.SetLineWidth(2)
                    this_hist.SetLineColor(l_color[m])
                    this_hist.SetMarkerStyle(list_marker[m])
                    this_hist.SetMarkerColor(l_color[m])

                    if new_pad:
                        axis_hist.GetXaxis().SetTitle(this_hist.GetXaxis().GetTitle())
                        axis_hist.GetYaxis().SetTitle(this_hist.GetYaxis().GetTitle())
                        axis_hist.Draw("AXIS")
                        gPad.RedrawAxis("g")

                        # this_hist.Draw("e")
                        this_hist.Draw("hist L X0 same")
                        # this_hist.Draw("e X0")
                    else:
                        # this_hist.Draw("e same")
                        this_hist.Draw("hist L X0 same")
                        # this_hist.Draw("e X0 same")

                    this_hist.Draw("e X0 same")

                    if (iN==0):
                        text = ROOT.TLatex()
                        text.SetTextSize(tsize-14)
                        text.SetTextAlign(23)
                        title = ms.GetBinInfo("Q%i"%(iQ), this_binning)
                        text.DrawLatexNDC(XtoPad(0.5),YtoPad(Q2_bin_info_Ypos),title)

                    if (iQ==2):
                        text = ROOT.TLatex()
                        text.SetTextSize(tsize-14)
                        text.SetTextAlign(23)
                        text.SetTextAngle(90)
                        title = ms.GetBinInfo("%s%i"%(key1,iN), this_binning) # "Q%iN%i" or "Q%iX%i"
                        text.DrawLatexNDC(XtoPad(1.05),YtoPad(0.5),title)

                    if (iQ==legQ and iN==legN):
                        legend.AddEntry(this_hist,list_fitmethods[m])
                        if (legend.GetListOfPrimitives().GetEntries()==len(list_fitmethodsKey)):
                            legend.Draw()
            new_pad = False

        this_bininfo = ms.get_name_format_bin(dataset)

        this_title_png = ms.getSummaryPath("%s_%s"%(this_bininfo,typeR), "png", plots_cuts, isJLab, this_bininfo +"/"+this_targ, "Summary_DiffMethods")
        this_title_png = ms.add_str_before_ext(this_title_png, "-DiffFitNorm%s_%s"%(par,this_targ), "png")

        this_title_pdf = ms.getSummaryPath("%s_%s"%(this_bininfo,typeR), "pdf", plots_cuts, isJLab, this_bininfo +"/"+this_targ, "Summary_DiffMethods")
        this_title_pdf = ms.add_str_before_ext(this_title_pdf, "-DiffFitNorm%s_%s"%(par,this_targ), "pdf")

        this_canvas.SaveAs(this_title_png)
        this_canvas.SaveAs(this_title_pdf)

for m,meth in enumerate(list_fitmethodsKey):
    list_infiles[m].Close()
