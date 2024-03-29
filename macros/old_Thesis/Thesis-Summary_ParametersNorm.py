from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as mS
from array import array
import ctypes ## Needed to get pointer values

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
mS.force_style()
# font=mS.get_font()
tsize=mS.get_size()

# gStyle.SetStatX(1 - mS.get_margin() - 0.005)
# gStyle.SetStatY(2*mS.get_margin() + 0.205)

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
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_Z/P...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")

parser.add_option('-f', dest='fit',  default = "R", help="Use Fold (F), Left (L) or Right (R) fit")
parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")

# parser.add_option('-y', dest='y_symmetric', action='store_true', default = False, help="Use symmetric y-limits (default False)")
parser.add_option('-s', dest='solidTargets', action='store_true', default = False, help="Draw only solid targets (default adds D)")
parser.add_option('-a', dest='allDSplit', action='store_true', default = False, help="Draw only deuterium for different solid targets")

parser.add_option('-Z', dest='useZh',  action='store_true', default = False, help="Use bin in Zh, integrate Pt2")
parser.add_option('-P', dest='usePt2', action='store_true', default = False, help="Use bin in Pt2, integrate Zh")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster
fit = options.fit

if ("LR" in mS.get_cut_long2final(options.inputCuts) and (not "Left" in options.inputCuts) and (not "Right" in options.inputCuts)):
    print("Specify \"Left\" or \"Right\" in input when using \"LR\" method!")
    exit()

if "Fold" in mS.get_cut_long2final(options.inputCuts):
    fit = "F"
elif ("Left" in mS.get_cut_long2final(options.inputCuts) or "Left" in options.inputCuts):
    fit = "L"
elif ("Right" in mS.get_cut_long2final(options.inputCuts) or "Right" in options.inputCuts):
    fit = "R"

fit_type = "Fd" if "F" in fit else "LR"
fit_num = 0 if (fit != "L") else 1

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"

input_cuts+="_"+fit_type # Add Fold or LR extension
plots_cuts+="_"+fit_type

useZh = options.useZh
usePt2 = options.usePt2
if ("Z" in mS.get_cut_str2list(mS.get_cut_long2final(options.outputCuts))) or ("Z" in mS.get_cut_str2list(mS.get_cut_long2final(options.inputCuts))):
    useZh = True
if ("P" in mS.get_cut_str2list(mS.get_cut_long2final(options.outputCuts))) or ("P" in mS.get_cut_str2list(mS.get_cut_long2final(options.inputCuts))):
    usePt2 = True

if (useZh) and (usePt2):
    print("Two binning selected. Please, choose only one of the options!")
    exit()
elif useZh:
    input_cuts+="_Zx"
    plots_cuts+="_Zx"
elif usePt2:
    input_cuts+="_Px"
    plots_cuts+="_Px"
else:
    print("Using Zx as default x binning!")
    input_cuts+="_Zx"
    plots_cuts+="_Zx"

dataset_elemts = dataset.split("_")
try:
    if (int(dataset_elemts[0])):
        print("")
except:
    dataset = "%s_%s"%(dataset_elemts[1],dataset_elemts[2])
    dataset_elemts = dataset.split("_")
    print("")

this_binning_type = int(dataset_elemts[0])
dataset_title = mS.get_name_format("_"+dataset)
this_bin_dict = mS.all_dicts[this_binning_type]

nBinsQ = len(this_bin_dict['Q'])-1
nBinsN = len(this_bin_dict['N'])-1
nBinsZ = len(this_bin_dict['Z'])-1
nBinsP = len(this_bin_dict['P'])-1

gStyle.SetOptStat(0)
canvas_B = TCanvas("cvB","cvB",1000,800)
CanvasPartition(canvas_B, nBinsQ, nBinsN,2*mS.get_margin(),mS.get_margin(),2*mS.get_margin(),mS.get_margin(),"B")
canvas_B.SetGrid(0,1)

canvas_C = TCanvas("cvC","cvC",1000,800)
CanvasPartition(canvas_C, nBinsQ, nBinsN,2*mS.get_margin(),mS.get_margin(),2*mS.get_margin(),mS.get_margin(),"C")
canvas_C.SetGrid(0,1)

list_canvas = [canvas_B, canvas_C]

list_targets = ["C", "Fe", "Pb", "D"]
# use_ysym = options.y_symmetric
onlySolid = options.solidTargets
allD = options.allDSplit

whatsPlot = "All"
if onlySolid:
    list_targets.remove("D")
    whatsPlot = "Solid"
if allD:
    list_targets = ["DC", "DFe", "DPb"]
    whatsPlot = "D"

list_infiles = []

# Open files
for targ in list_targets:
    this_dataset = "%s_%s"%(targ, dataset)
    inputPath = mS.get_plots_folder("FitParametersNorm", input_cuts, this_dataset, isJLab, False) # "../output/"
    inputROOT = mS.get_plots_file("Parameters", this_dataset, "root", fit_type)

    inputfile = TFile(inputPath+inputROOT,"READ")
    list_infiles.append(inputfile)

list_hists = []

## Create histograms
for p,par in enumerate(["B", "C"]): # 2
    list_this_par = []
    for t,targ in enumerate(list_targets): # 4
        list_this_tar = []
        hist_par_Pos = list_infiles[t].Get("f_Norm_%s%i_Pos"%(par,fit_num))
        hist_par_Neg = list_infiles[t].Get("f_Norm_%s%i_Neg"%(par,fit_num))

        for iQ in range(nBinsQ): #nQ
            list_this_Q = []
            for iN in range(nBinsN): #nN
                bin_label = "Q%iN%i"%(iQ,iN)
                if useZh:
                    hist_tmp = TH1D("%s_%s_Q%iN%i"%(par,targ,iQ,iN),";Z_{h};%s/A"%(par),nBinsZ,array('d',this_bin_dict['Z']))

                    for iZ in range(1,nBinsZ+1):
                        this_label = "%sZ%i"%(bin_label,iZ-1)
                        this_bin = hist_par_Pos.GetXaxis().FindBin(this_label)
                        bin_value = hist_par_Pos.GetBinContent(this_bin) if hist_par_Pos.GetBinContent(this_bin)>0.0 else -hist_par_Neg.GetBinContent(this_bin)
                        bin_error = hist_par_Pos.GetBinError(this_bin) if hist_par_Pos.GetBinContent(this_bin)>0.0 else hist_par_Neg.GetBinError(this_bin)

                        hist_tmp.SetBinContent(iZ, bin_value)
                        hist_tmp.SetBinError(iZ, bin_error)
                elif usePt2:
                    hist_tmp = TH1D("%s_%s_Q%iN%i"%(par,targ,iQ,iN),";P_{t}^{2} (GeV^{2});%s/A"%(par),nBinsP,array('d',this_bin_dict['P']))

                    for iP in range(1,nBinsP+1):
                        this_label = "%sP%i"%(bin_label,iP-1)
                        this_bin = hist_par_Pos.GetXaxis().FindBin(this_label)
                        bin_value = hist_par_Pos.GetBinContent(this_bin) if hist_par_Pos.GetBinContent(this_bin)>0.0 else -hist_par_Neg.GetBinContent(this_bin)
                        bin_error = hist_par_Pos.GetBinError(this_bin) if hist_par_Pos.GetBinContent(this_bin)>0.0 else hist_par_Neg.GetBinError(this_bin)

                        hist_tmp.SetBinContent(iP, bin_value)
                        hist_tmp.SetBinError(iP, bin_error)

                list_this_Q.append(hist_tmp)
            list_this_tar.append(list_this_Q)
        list_this_par.append(list_this_tar)
        # inputfile.Close()

    list_hists.append(list_this_par) #  npar*nTarg*nQ*nN = 2*4*nQ*nN hists

par_y_lmts = [[-0.999,0.199], [-0.399,0.099]]
# Q2_bin_info_Ypos = -0.15
Q2_bin_info_Ypos = -0.22

if usePt2:
    par_y_lmts = [[-0.499,0.049], [-0.099,0.149]]
    # Q2_bin_info_Ypos = -0.22

for p,par in enumerate(["B", "C"]):
    this_canvas = list_canvas[p]
    this_canvas.cd(0)
    # mS.draw_summary("Norm %s/A %s"%(par,fit))
    if (whatsPlot=="All"):
        targs_drawn = "All_targets"
    elif (whatsPlot=="Solid"):
        targs_drawn = "Solid targets"
    elif (whatsPlot=="D"):
        targs_drawn = "Deuterium"
    # mS.draw_targetinfo(targs_drawn, "Data")

    # mS.draw_summary("%s ratio Solid/D%s %s"%(par,solid_mix,fit))
    mS.draw_preliminary("%s normalized for %s"%(par,targs_drawn))
    # mS.draw_targetinfo("Solid targets", "Data")

    l_x1, l_x2 = 0.1, 0.9
    l_y1, l_y2 = 0.60, 0.80
    if not usePt2: # Using Zh
        l_y1 = 0.1
        l_y2 = 0.3
    legend = TLegend(l_x1, l_y1, l_x2, l_y2)
    legend.SetBorderSize(0)
    legend.SetTextFont(mS.get_font())
    legend.SetTextSize(mS.get_size()-14)
    legend.SetFillStyle(0)
    legend.SetNColumns(3)

    lineZero = ROOT.TLine(0.0,0.0, 1.0,0.0)
    lineZero.SetLineColor(ROOT.kRed)
    lineZero.SetLineWidth(1)
    lineZero.SetLineStyle(9)

    for t,targ in enumerate(list_targets):
        this_canvas.cd(0)
        for iQ in range(nBinsQ):
            for iN in range(nBinsN): # iQ,iN = 0,0 (B)
                this_pad = gROOT.FindObject("pad%s_%i_%i"%(par,iQ,nBinsN-iN-1)) # -> 0,2 (A)
                this_pad.SetGrid(0,1)

                ## This selection labels xy such as:
                ##       (A)              (B)
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
                # this_hist.SetLabelSize(tsize-18,"xy")
                # this_hist.SetTitleSize(tsize-14,"xy")
                # this_hist.SetTitleOffset(2.5,"xy")
                this_hist.SetLabelSize(tsize-20,"xy")
                this_hist.SetTitleSize(tsize-16,"xy")
                this_hist.SetTitleOffset(1.0,"x")
                this_hist.SetTitleOffset(1.8,"y")

                this_hist.SetLineColor(mS.color_target[targ])
                this_hist.SetMarkerStyle(4)
                this_hist.SetMarkerColor(mS.color_target[targ])
                this_hist.Draw("same")
                # this_hist.Draw("e X0 same")
                # this_hist.Draw("hist L X0 same")

                # Draw line at ratio = 1.0
                lineZero.DrawLine(this_hist.GetXaxis().GetXmin(),0.0, this_hist.GetXaxis().GetXmax(),0.0)

                # Draw hist in last layer
                this_hist.Draw("e same")
                # this_hist.Draw("e X0 same")
                # this_hist.Draw("hist L e X0 same")

                if (iN==2):
                    text = ROOT.TLatex()
                    text.SetTextSize(tsize-14)
                    text.SetTextAlign(23)
                    # title = mS.get_bintxt("Q%iN%i"%(iQ,iN), this_binning_type)
                    title = mS.get_bintxt("Q%i"%(iQ), this_binning_type)
                    text.DrawLatexNDC(XtoPad(0.5),YtoPad(Q2_bin_info_Ypos),title)

                if (iQ==2):
                    text = ROOT.TLatex()
                    text.SetTextSize(tsize-14)
                    text.SetTextAlign(23)
                    text.SetTextAngle(90)
                    # title = mS.get_bintxt("Q%iN%i"%(iQ,iN), this_binning_type)
                    title = mS.get_bintxt("N%i"%(iN), this_binning_type)
                    text.DrawLatexNDC(XtoPad(1.05),YtoPad(0.5),title)

                if (iQ==2 and iN==0):
                    legend.AddEntry(this_hist,targ)
                    if (legend.GetListOfPrimitives().GetEntries()==len(list_targets)):
                        legend.Draw()

    this_title_gif = mS.get_summary_fullpath("Par%s_Norm%s"%(par,dataset_title), "gif", plots_cuts, isJLab, "Thesis/"+dataset_title[1:])
    this_title_gif = mS.add_str_before_ext(this_title_gif, "_%s"%(whatsPlot), "gif")
    if ("LR" in this_title_gif):
        this_title_gif = mS.add_str_before_ext(this_title_gif, "-%s"%(fit), "gif")

    this_title_pdf = mS.get_summary_fullpath("Par%s_Norm%s"%(par,dataset_title), "pdf", plots_cuts, isJLab, "Thesis/"+dataset_title[1:])
    this_title_pdf = mS.add_str_before_ext(this_title_pdf, "_%s"%(whatsPlot), "pdf")
    if ("LR" in this_title_pdf):
        this_title_pdf = mS.add_str_before_ext(this_title_pdf, "-%s"%(fit), "pdf")

    this_canvas.SaveAs(this_title_gif)
    this_canvas.SaveAs(this_title_pdf)

for t,targ in enumerate(list_targets):
    list_infiles[t].Close()
