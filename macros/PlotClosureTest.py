from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
myStyle.ForceStyle()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-a', dest='saveAll', action='store_true', default = False, help="Save All plots")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")
parser.add_option('-f', dest='fracAcc', default = 50., help="Fraction of the stats used in Acc calculation (this/100.)")

parser.add_option('-e', dest='errorFull', action='store_true', default = False, help="Use FullError")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
isJLab = options.JLabCluster

fracAcc = options.fracAcc

infoDict  = myStyle.getDictNameFormat(dataset)
nameFormatted = myStyle.getNameFormatted(dataset)

## Cuts
input_cuts = options.inputCuts
plots_cuts = options.inputCuts + "_" + options.outputCuts
if options.errorFull:
    input_cuts+="_FE"
    plots_cuts+="_FE"

# useZh = options.useZh
# usePt2 = options.usePt2
useZh = False
usePt2 = False
# print(myStyle.getCutStrFromStr(options.outputCuts))
if ("Z" in myStyle.getCutsAsList(myStyle.getCutStrFromStr(options.outputCuts))) or ("Z" in myStyle.getCutsAsList(myStyle.getCutStrFromStr(options.inputCuts))):
    useZh = True
if ("P" in myStyle.getCutsAsList(myStyle.getCutStrFromStr(options.outputCuts))) or ("P" in myStyle.getCutsAsList(myStyle.getCutStrFromStr(options.inputCuts))):
    usePt2 = True

if (useZh) and (usePt2):
    print("  [ClosureTest] Two binning selected. Please, choose only one of the options!")
    exit()
elif useZh:
    plots_cuts+="_Zx"
elif usePt2:
    plots_cuts+="_Px"
else:
    print("  [ClosureTest] No binning selected. Please, choose Zh (Zx) or Pt2 (Px) as x binning (integrate the other)!")
    exit()

## Input
inputPath = myStyle.getOutputFolder("ClosureTest%ip"%int(fracAcc), input_cuts, isJLab, False) # "../output/"
inputName = myStyle.getOutputFile("ClosureTest", dataset) # "../output/"
inputfile = TFile(inputPath+inputName,"READ")

## Output
outputPath = myStyle.getPlotsFolder("ClosureTest%ip"%int(fracAcc), plots_cuts, myStyle.getBinNameFormatted(dataset) + "/" + infoDict["Target"], isJLab)
outputROOT = myStyle.getPlotsFile("ClosureTest", dataset, "root")

histCorr_Reconstru = inputfile.Get("Corr_Reconstru")
histCorr_ReMtch_mc = inputfile.Get("Corr_ReMtch_mc")
histCorr_ReMtch_re = inputfile.Get("Corr_ReMtch_re")
histTrue           = inputfile.Get("True")
histTrue_PionRec   = inputfile.Get("True_PionReco")

inputTHnSparse_list = [histCorr_Reconstru, histCorr_ReMtch_mc, histCorr_ReMtch_re, histTrue, histTrue_PionRec]
prefixType = ["Correction", "Correct Match_mc", "Correct Match_rec", "True", "True GoodPionRec"]
type_reco_short = ["Reco", "RMmc", "RMre"]

bins_list = [] # [3, 3, 10, 1]
default_conf = [1,1,0,0] # 2D bins -> Q2 and Nu, integrate Zh and Pt2
this_conf = [1,1,0,0]

### REVISIT THIS!
# Set default shown binning by BinningType
if (infoDict["BinningType"] == 0): # 0: Small binning
    default_conf[2] = 0
    default_conf[3] = 0
elif (infoDict["BinningType"] >= 1): # 1: SplitZh
    default_conf[2] = 1
    default_conf[3] = 0
# elif (infoDict["BinningType"] == 2): # 2: ThinZh bin, so it is intended to shown results as function of Zh
#     default_conf[2] = 1
#     default_conf[3] = 0

# Change binning using input (or use default)
if (useZh):
    this_conf[2] = 1
    this_conf[3] = 0
elif (usePt2):
    this_conf[2] = 0
    this_conf[3] = 1
else:
    this_conf = default_conf # Plot Z


# Retrieve 5d-hists, get projections and save them, along with a label to identify the bin
totalsize = 1
for i,i_bool in enumerate(this_conf):
    if i_bool:
        nbins = histCorr_Reconstru.GetAxis(i).GetNbins()
        totalsize*=nbins
        bins_list.append(nbins)
    else:
        bins_list.append(1)

list_binName = []
Proj1DTHnSparse_list = [[],[],[],[],[]]
symbol_list = ["Q","N","Z","P"]

if ('X' in myStyle.all_dicts[infoDict["BinningType"]]):
    symbol_list[1] = "X"

print("  [ClosureTest] Using variables [%s]"%(', '.join(symbol_list)))

for i in range(totalsize):
    total_tmp = totalsize
    i_tmp = i
    txt_tmp = ""
    # for j,nbin in enumerate(bins_list):
    for j,j_bool in enumerate(this_conf):
        if j_bool:
            total_tmp /= bins_list[j]
            index = i_tmp/(total_tmp)
            i_tmp -= index*total_tmp
            txt_tmp += (symbol_list[j]+str(index))

            for t in inputTHnSparse_list:
                t.GetAxis(j).SetRange(index+1, index+1)

            # histCorr_Reconstru.GetAxis(j).SetRange(index+1, index+1)

    for n,newRangeInput in enumerate(inputTHnSparse_list):
        proj_tmp = newRangeInput.Projection(4)
        proj_tmp.SetName(newRangeInput.GetName()+"_"+txt_tmp)

        Proj1DTHnSparse_list[n].append(proj_tmp)

    list_binName.append(txt_tmp)

## Create TH1 summary ClosureTest

list_th1_CT = []
list_th1_CT_err = []
list_th1_CT_err100 = []
for reco_meth in type_reco_short:
    tmp_h1d_CT = TH1D("CT%ip_%s-Summary"%(fracAcc, reco_meth), ";Closureness;Counts", 100,0.21,1.79)
    list_th1_CT.append(tmp_h1d_CT)

    tmp_h1d_CT_err = TH1D("CT%ip_%s-SummaryErr"%(fracAcc, reco_meth), ";Closureness error;Counts", 100,0.01,0.79)
    list_th1_CT_err.append(tmp_h1d_CT_err)

    tmp_h1d_CT_err100 = TH1D("CT%ip_%s-SummaryErr100"%(fracAcc, reco_meth), ";Closureness error %;Counts", 100,0.0,100.0)
    list_th1_CT_err100.append(tmp_h1d_CT_err100)


canvas = TCanvas("cv","cv",1000,800)
canvas.SetGrid(0,1)
# gPad.SetTicks(1,1)
TH1.SetDefaultSumw2()
gStyle.SetOptStat(0)


# Plot 2D histograms
outputfile = TFile(outputPath+outputROOT,"RECREATE")
phi_axis_title = myStyle.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"

# for pt,pref in enumerate(prefixType):
for pt,pref in enumerate(type_reco_short):
    canvas.Clear()
    th1_ct = list_th1_CT[pt]
    th1_ct_err = list_th1_CT_err[pt]
    th1_ct_err100 = list_th1_CT_err100[pt]
    for i,info in enumerate(list_binName):
        # if saveAll:
        #     for p,proj in enumerate(Proj1DTHnSparse_list):
        #         this_proj = proj[i]
        #         htemp = TH1F("htemp","",1,-180.,180.)
        #         htemp.SetStats(0)
        #         htemp.SetMinimum(0.0001)
        #         # ylim = 30000
        #         ylim = this_proj.GetMaximum()*1.2
        #         htemp.SetMaximum(ylim)
        #         # htemp.SetLineColor(kBlack)
        #         htemp.GetXaxis().SetTitle(phi_axis_title)
        #         htemp.GetYaxis().SetTitle("Counts")
        #         htemp.Draw("AXIS")

        #         this_proj.SetLineColor(kBlack)
        #         # list_Corr_Reconstru[i].SetTitle(info.title)
        #         # list_Corr_Reconstru[i].GetXaxis().SetTitle(info.xlabel)
        #         # list_Corr_Reconstru[i].GetXaxis().SetRangeUser(-0.32, 0.32)
        #         # list_Corr_Reconstru[i].GetYaxis().SetTitle(info.ylabel)

        #         # gPad.RedrawAxis("g")

        #         # htemp.Draw("AXIS same")
        #         # list_Corr_Reconstru[i].Draw("AXIS same")
        #         this_proj.Draw("hist e same")

        #         # legend.Draw();
        #         myStyle.DrawPreliminaryInfo(prefixType[p])
        #         myStyle.DrawTargetInfo(nameFormatted, "Simulation")
        #         myStyle.DrawBinInfo(info, infoDict["BinningType"])

        #         histName = "_".join(this_proj.GetName().split("_")[0:-1]) # Corr_A_B_Q1N2 -> Corr_A_B
        #         outputName = myStyle.getPlotsFile(histName, dataset, "png", info)
        #         canvas.SaveAs(outputPath+outputName)
        #         # canvas.SaveAs(outputPath+nameFormatted+"-"+this_proj.GetName()+".png")
        #         this_proj.Write()
        #         htemp.Delete()

        # if ("Corr" in pref):

        # Get ClosureTest
        htemp = TH1F("htemp","",1,-180.,180.)
        htemp.SetStats(0)
        htemp.SetMinimum(0.3)
        htemp.SetMaximum(1.7)
        # htemp.SetLineColor(kBlack)
        htemp.GetXaxis().SetTitle(phi_axis_title)
        htemp.GetYaxis().SetTitle("Corr / True")
        htemp.Draw("AXIS")

        this_name = "CT%ip_%s"%(int(fracAcc),pref)

        hCT = Proj1DTHnSparse_list[pt][i].Clone(this_name+"-%s"%info) # pt=0 -> Correction
        hCT.Divide(Proj1DTHnSparse_list[pt][i],Proj1DTHnSparse_list[3][i],1,1,"B") # RE DO THIS WITH THE OTHER RAW ONE

        hCT.SetLineColor(kBlack)
        # hCT.GetXaxis().SetTitle(info.xlabel)
        # hCT.GetXaxis().SetRangeUser(-0.32, 0.32)
        # hCT.GetYaxis().SetTitle(info.ylabel)

        # gPad.RedrawAxis("g")

        hCT.Draw("hist e same")

        myStyle.DrawPreliminaryInfo("ClosureTest %s"%pref)
        myStyle.DrawTargetInfo(nameFormatted, "Simulation")
        myStyle.DrawBinInfo(info, infoDict["BinningType"])

        gPad.RedrawAxis("g")

        outputName = myStyle.getPlotsFile(this_name, dataset, "png", info)
        canvas.SaveAs(outputPath+outputName)
        # canvas.SaveAs(outputPath+nameFormatted+"-ClosureTest_"+info+ext_error+".png")
        hCT.Write()

        ### Fill CT projection
        for b in range(1, hCT.GetXaxis().GetNbins()+1):
            value = hCT.GetBinContent(b)
            error = hCT.GetBinError(b)

            th1_ct.Fill(value)
            th1_ct_err.Fill(error)
            if (value!=0):
                th1_ct_err100.Fill(100.*error/value)
            else:
                print("%s - Bin %i is empty :c"%(pref,b))

        htemp.Delete()

    ## Draw and save summary Closure values
    canvas.Clear()
    th1_ct.SetLineColor(kBlack)
    th1_ct.SetTitleOffset(1.3,"y")
    th1_ct.Draw()
    top_label = "Z_{h}" if useZh else "P_{t}^{2}"
    if (pref != "Reco"):
        top_label+=" %s"%pref
    myStyle.DrawSummaryInfo("Closure value %s"%(top_label))
    myStyle.DrawTargetInfo(nameFormatted, "Simulation")

    outputName_png = myStyle.getPlotsFile(th1_ct.GetName(), dataset, "png")
    canvas.SaveAs(outputPath+outputName_png)
    outputName_pdf = myStyle.getPlotsFile(th1_ct.GetName(), dataset, "pdf")
    canvas.SaveAs(outputPath+outputName_pdf)
    th1_ct.Write()

    ## Draw and save summary Closure errors
    canvas.Clear()
    th1_ct_err.SetLineColor(kBlack)
    th1_ct_err.SetTitleOffset(1.3,"y")
    th1_ct_err.Draw()
    myStyle.DrawSummaryInfo("Closure error %s"%pref)
    myStyle.DrawTargetInfo(nameFormatted, "Simulation")

    outputName = myStyle.getPlotsFile(th1_ct_err.GetName(), dataset, "png")
    canvas.SaveAs(outputPath+outputName)
    th1_ct_err.Write()

    ## Draw and save summary Closure errors in 100 base
    canvas.Clear()
    th1_ct_err100.SetLineColor(kBlack)
    th1_ct_err100.SetTitleOffset(1.3,"y")
    th1_ct_err100.Draw()
    myStyle.DrawSummaryInfo("Closure error %% %s"%pref)
    myStyle.DrawTargetInfo(nameFormatted, "Simulation")

    outputName = myStyle.getPlotsFile(th1_ct_err100.GetName(), dataset, "png")
    canvas.SaveAs(outputPath+outputName)
    th1_ct_err100.Write()

print("  [ClosureTest] Closure Test finished and saved!")
outputfile.Close()

