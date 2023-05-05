from ROOT import TFile,TTree,TCanvas,TH1I,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
ms.ForceStyle()

gStyle.SetStatX(1 - ms.GetMargin() - 0.005)
gStyle.SetStatY(2*ms.GetMargin() + 0.205)

def PropErrorDivision(v1, e1, v2, e2, cov=0):
    this_error = TMath.Abs(v1/v2)*TMath.Sqrt((e1/v1)*(e1/v1) + (e2/v2)*(e2/v2) - 2*cov/(v1*v2))
    return this_error

def GetMatrixElem(matrix, row, col):
    this_matrix = matrix.GetMatrixArray()
    index = col + 3*row
    return this_matrix[index]

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <target>_<binType>_<Ndims>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_Z/P...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_...")

parser.add_option('-v', dest='verbose', action='store_true', default = False, help="Print values")
parser.add_option('-m', dest='mixD', action='store_true', default = False, help="Mix deuterium data from all solid targets")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False, help="Overwrite if file already exists")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

# saveAll = options.saveAll
dataset = options.Dataset
rootpath = options.rootpath
isJLab = options.JLabCluster
verbose = options.verbose

input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

### Define type of fit used
fit_type = ms.get_fit_method(plots_cuts)

mixD = False
if "MixD" in ms.get_cut_str2finallist(plots_cuts):
    mixD = True

infoDict = ms.get_name_dict(dataset) # ["Target", "BinningType", "NDims"]
nameFormatted = ms.get_name_format(dataset)

if ("D" in infoDict["Target"]):
    print("  [ParRatio] Trivial ratio with D. Try with a solid target.")
    exit()

## Cuts
# # Add fit type to the list of cuts!
# input_cuts+="_"+fit_type # Add Fold or LR extension
# plots_cuts+="_"+fit_type

useZh = False
usePt2 = False
if ("Z" in ms.get_cut_str2finallist(plots_cuts)):
    useZh = True
if ("P" in ms.get_cut_str2finallist(plots_cuts)):
    usePt2 = True

if (useZh) and (usePt2):
    print("  [ParRatio] Two binning selected. Please, choose only one of the options!")
    exit()
elif useZh:
    input_cuts+="_Zx"
    plots_cuts+="_Zx"
elif usePt2:
    input_cuts+="_Px"
    plots_cuts+="_Px"
else:
    print("  [ParRatio] Select Zx or Px as x binning!")
    exit()

## Deuterium info
solid_targ = infoDict["Target"] if not mixD else ""
dataset_D = "D%s_%s_%s"%(solid_targ,infoDict["BinningType"],infoDict["NDims"])

inputPath_D = ms.get_plots_folder("Fit", input_cuts, dataset_D, isJLab, False)
inputROOT_D = ms.get_plots_file("Fit", dataset_D, "root", fit_type)
inputfile_D = TFile(inputPath_D+inputROOT_D,"READ")

## Input
inputPath_solid = ms.get_plots_folder("Fit", input_cuts, dataset, isJLab, False)
inputROOT_solid = ms.get_plots_file("Fit", dataset, "root", fit_type)
inputfile_solid = TFile(inputPath_solid+inputROOT_solid,"READ")

## Output
outputPath = ms.get_plots_folder("ParametersRatio", plots_cuts, dataset, isJLab)
outputROOT = ms.get_plots_file("ParametersRatio", dataset, "root", fit_type)
if (not options.Overwrite and os.path.exists(outputPath+outputROOT)):
    print("  [ParRatio] Parameters ratio file already exists! Not overwriting it.")
    exit()

### Define list with fit names
list_func_names = ["crossSectionR"]
if (fit_type == "LR"):
    list_func_names.append("crossSectionL")

n_htypeReco = [0, 0, 0]

list_of_hists = inputfile_solid.GetListOfKeys().Clone()
for elem in list_of_hists:
    if (elem.ReadObj().Class_Name() != "TH1D"):
        list_of_hists.Remove(elem)

    else:
        if ("Corr_Reconstru" in elem.GetName()):
            n_htypeReco[0]+=1
        elif ("Corr_ReMtch_mc" in elem.GetName()):
            n_htypeReco[1]+=1
        elif ("Corr_ReMtch_re" in elem.GetName()):
            n_htypeReco[2]+=1

print("Corr_Reconstru: %i"%n_htypeReco[0])
print("Corr_ReMtch_mc: %i"%n_htypeReco[1])
print("Corr_ReMtch_re: %i"%n_htypeReco[2])

type_reco = ["Reconstru",] # Corr_
type_reco_short = ["Reco",]

if n_htypeReco[1]!=0:
    type_reco.append("ReMtch_mc")
    type_reco_short.append("RMmc")

if n_htypeReco[2]!=0:
    type_reco.append("ReMtch_re")
    type_reco_short.append("RMre")


ratio_th1_b_list = [[],[],[]]
ratio_th1_c_list = [[],[],[]]

for e,elem in enumerate(list_func_names):
    for t,typeR in enumerate(type_reco_short):
        this_n = n_htypeReco[t]
        if (this_n>0):
            ratio_th1_b = TH1D("f_Ratio_B%i_%s"%(e,typeR),";Bin;Ratio (b_{{{0}}}/a_{{{0}}}) / (b_{{D}}/a_{{D}})".format(infoDict["Target"]), this_n,0.0,this_n)
            ratio_th1_b_list[t].append(ratio_th1_b)

            ratio_th1_c = TH1D("f_Ratio_C%i_%s"%(e,typeR),";Bin;Ratio (c_{{{0}}}/a_{{{0}}}) / (c_{{D}}/a_{{D}})".format(infoDict["Target"]), this_n,0.0,this_n)
            ratio_th1_c_list[t].append(ratio_th1_c)

print("")
print("Parameters Ratio of target %s"%infoDict["Target"])

# index_h = 0
binIndex_htype = list(n_htypeReco) # [X, Y, Z] This will give the bins remaining in the different Reco Methods (after the loop will be full of 0s)

for i_h,h in enumerate(inputfile_solid.GetListOfKeys()):
    if (h.ReadObj().Class_Name() == "TH1D"):
        hist_solid = h.ReadObj()
        hist_name = h.GetName()
        hist_D = inputfile_D.Get(hist_name) # Corr_Reconstru_Q0N0Z0_fold

        tmp_name = "_".join(h.GetName().split("_")[1:-2]) # Reconstru
        bin_name = hist_name.split("_")[-2] # Q0N0Z0

        type_index = type_reco.index(tmp_name) # Index in ["Reconstru", "ReMtch_mc", "ReMtch_re"]

        this_binIndex = n_htypeReco[type_index] - binIndex_htype[type_index] # X-X = 0, next X-(X-1) = 1, ..., X-(X-X) = X


        for i_f,f in enumerate(list_func_names):
            # Get covariance matrix
            # name_cov = "covM" # "covM"
            # if "L" in f:
            #     name_cov+="L" # "covML"

            name_cov = "covM1" if "L" in f else "covM0"

            name_cov+="_%s_%s"%(bin_name, type_reco_short[type_index]) # "covM0_Q0N0Z0_Reco" or "covM1_Q0N0Z0_Reco" (L)

            cov_matrix_X = inputfile_solid.Get(name_cov)
            cov_matrix_D = inputfile_D.Get(name_cov)

            try:
                fit_solid = hist_solid.GetFunction(f)
            except:
                print("  [ParRatio] Solid fit not found! %s"%name_cov)
                continue

            try:
                fit_D = hist_D.GetFunction(f)
            except:
                print("  [ParRatio] D fit not found! %s"%name_cov)
                continue

            par0_X = fit_solid.GetParameter(0)
            par1_X = fit_solid.GetParameter(1)
            par2_X = fit_solid.GetParameter(2)

            err0_X = fit_solid.GetParError(0)
            err1_X = fit_solid.GetParError(1)
            err2_X = fit_solid.GetParError(2)

            par0_D = fit_D.GetParameter(0)
            par1_D = fit_D.GetParameter(1)
            par2_D = fit_D.GetParameter(2)

            err0_D = fit_D.GetParError(0)
            err1_D = fit_D.GetParError(1)
            err2_D = fit_D.GetParError(2)

            if verbose:
                print("%s Fit: %s"%(hist_name, f))
                print("Solid: (%6.2f, %5.2f, %5.2f)"%(par0_X, par1_X, par2_X))
                print("       (%6.2f, %5.2f, %5.2f)"%(par0_X/par0_X, par1_X/par0_X, par2_X/par0_X))
                print("Liquid: (%6.2f, %5.2f, %5.2f)"%(par0_D, par1_D, par2_D))
                print("        (%6.2f, %5.2f, %5.2f)"%(par0_D/par0_D, par1_D/par0_D, par2_D/par0_D))
                print("Ratio: (%5.2f, %5.2f, %5.2f)"%(par0_X/par0_D, par1_X/par1_D, par2_X/par2_D))
                print("       (%5.2f, %5.2f, %5.2f)"%( (par0_X/par0_X)/(par0_D/par0_D) , (par1_X/par0_X)/(par1_D/par0_D) , (par2_X/par0_X)/(par2_D/par0_D)))
                print("")

            ratio_th1_b_list[type_index][i_f].Fill(bin_name, 0.0)
            ratio_th1_c_list[type_index][i_f].Fill(bin_name, 0.0)

            # Get error propagated and fill B/A
            cov10_X = GetMatrixElem(cov_matrix_X, 0, 1) # Get Cov AB
            cov10_D = GetMatrixElem(cov_matrix_D, 0, 1) # Get Cov AB

            err10_X = PropErrorDivision(par1_X, err1_X, par0_X, err0_X, cov10_X)
            err10_D = PropErrorDivision(par1_D, err1_D, par0_D, err0_D, cov10_D)
            err1_XD = PropErrorDivision((par1_X/par0_X), err10_X, (par1_D/par0_D), err10_D)
            ratio_th1_b_list[type_index][i_f].SetBinContent(this_binIndex+1, (par1_X/par0_X)/(par1_D/par0_D))
            ratio_th1_b_list[type_index][i_f].SetBinError(this_binIndex+1, err1_XD)

            # Get error propagated and fill C/A
            cov20_X = GetMatrixElem(cov_matrix_X, 0, 2) # Get Cov AC
            cov20_D = GetMatrixElem(cov_matrix_D, 0, 2) # Get Cov AC

            err20_X = PropErrorDivision(par2_X, err2_X, par0_X, err0_X, cov20_X)
            err20_D = PropErrorDivision(par2_D, err2_D, par0_D, err0_D, cov20_D)
            err2_XD = PropErrorDivision((par2_X/par0_X), err20_X, (par2_D/par0_D), err20_D)
            ratio_th1_c_list[type_index][i_f].SetBinContent(this_binIndex+1, (par2_X/par0_X)/(par2_D/par0_D))
            ratio_th1_c_list[type_index][i_f].SetBinError(this_binIndex+1, err2_XD)

        binIndex_htype[type_index]-=1

print("")

canvas = TCanvas("cv","cv",1000,800)
gStyle.SetOptStat(0)
canvas.SetGrid(0,1)

### Ratio of the ratios b/a and c/a -> Solid target / D target
outputFile = TFile(outputPath+outputROOT,"RECREATE")

ymin = 0.001
ymax = 1.2
for e,elem in enumerate(list_func_names):
    for t,typeR in enumerate(type_reco_short):

        name_ext = ms.get_fit_shortmethod(fit_type, elem)

        hist_b = ratio_th1_b_list[t][e]
        hist_b.SetMinimum(ymin)
        hist_b.SetMaximum(2*ymax)

        hist_b.Write()
        hist_b.Draw("hist e")

        ms.DrawPreliminaryInfo("Ratio over D%s %s"%(solid_targ,fit_type))
        ms.DrawTargetInfo(nameFormatted, "Data")

        outputName = ms.get_plots_file("RatioD%s_B_%s"%(solid_targ,typeR), dataset, "png", name_ext)
        canvas.SaveAs(outputPath+outputName)
        canvas.Clear()

        hist_c = ratio_th1_c_list[t][e]
        hist_c.SetMinimum(ymin)
        hist_c.SetMaximum(2*ymax)

        hist_c.Write()
        hist_c.Draw("hist e")

        ms.DrawPreliminaryInfo("Ratio over D%s %s"%(solid_targ,fit_type))
        ms.DrawTargetInfo(nameFormatted, "Data")

        outputName = ms.get_plots_file("RatioD%s_C_%s"%(solid_targ,typeR), dataset, "png", name_ext)
        canvas.SaveAs(outputPath+outputName)
        canvas.Clear()

outputFile.Write()
outputFile.Close()

print("  [ParRatio] Made it to the end!\n")
inputfile_solid.Close()
inputfile_D.Close()
