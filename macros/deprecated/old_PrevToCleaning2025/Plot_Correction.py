from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,\
TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
import myNameFormat as nf

## Defining Style
ms.force_style()
gStyle.SetTitleYOffset(1.2)


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
parser.add_option('-b', dest='nonIntegratedVars', default = "",
                  help="Add non-integratedd bins like in QNZ")
parser.add_option('-i', dest='inputCuts', default = "",
                  help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "",
                  help="Add output cuts FE_Z_P_...")

parser.add_option('-A', dest='save_all', action='store_true', default = False,
                  help="Save All plots")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")

# input: <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
isJLab = options.isJLab
ovr = options.Overwrite
save_all = options.save_all

bin_set = options.nonIntegratedVars
input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts
if bin_set:
    plots_cuts+= "_b%s"%bin_set

in_obj = nf.naming_format("Correction", dataset, cuts=input_cuts,
                          is_JLab=isJLab, in_output=True)
inputfile = TFile(in_obj.get_path_from_output(),"READ")

out_obj = nf.naming_format("Correction", dataset, cuts=plots_cuts,
                          is_JLab=isJLab)

# Get dataset info
dataset_info = ms.get_name_dict(dataset)
nbin_dataset = dataset_info["nBin"]
target = dataset_info["Target"]

# Retrieve THnSparse from input file
list_hname = ["Corr_Reconstru", "Corr_ReMtch_mc", "Corr_ReMtch_re", "Raw_data"]
list_thnSparse = [inputfile.Get(hname) for hname in list_hname]

# long/old name: ["Corrected", "Corr GoodGen_mc", "Corr GoodGen_re", "Raw data"]
list_title = ["Corrected", "Corr GMmc", "Corr GMre"] + ["Raw data"]

# Remove extra correction methods if needed (i.e. keep first and last elements)
if not save_all:
    list_hname = list_hname[::3]
    list_thnSparse = list_thnSparse[::3]
    list_title = list_title[::3]

# Create list with projections
list_bincodes = ms.get_bincode_list(nbin_dataset, plots_cuts)
use_shift = (ms.cut_is_included("Sh", plots_cuts))
list_projections = []
for ths in list_thnSparse:
    list_histograms = [ms.create_sparse_1Dprojection(ths, bc, use_shift) for bc in list_bincodes]
    list_projections.append(list_histograms)

# Create canvas
canvas = ms.create_canvas()
outputfile = TFile(out_obj.get_path(True, ovr),"RECREATE")

# Draw and save histograms with the correct style
axis_title_phi = ms.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"
for m,list_hprojection_method in enumerate(list_projections):
    # Update output object to get correct name
    out_obj.updt_acc_method(list_hname[m])
    out_obj.updt_extension("png")

    title_method = list_title[m]
    for bc,hist_projection in enumerate(list_hprojection_method):
        # Update output object to get correct name
        bincode = list_bincodes[bc]
        out_obj.updt_bin_code(bincode)
        hist_projection.SetName(out_obj.get_hist_name())

        # Create temporary histogram with required axis style
        xmin = hist_projection.GetXaxis().GetXmin()
        xmax = hist_projection.GetXaxis().GetXmax()
        ymax = hist_projection.GetMaximum() * 1.2

        htemp = TH1F("htemp", "", 1, xmin, xmax)
        htemp.SetStats(0)
        htemp.SetMinimum(0.0001)
        htemp.SetMaximum(ymax)
        # htemp.SetLineColor(kBlack)
        htemp.GetXaxis().SetTitle(axis_title_phi)
        htemp.GetYaxis().SetMaxDigits(3)
        htemp.GetYaxis().SetTitle("Counts")
        htemp.Draw("AXIS")

        # Draw projection
        hist_projection.SetLineColor(kBlack)
        # gPad.RedrawAxis("g")
        hist_projection.Draw("hist e same")

        ms.draw_preliminary(title_method)
        # ms.draw_targetinfo(target + nbin_dataset, "Data")
        ms.draw_targetinfo(target, "Data")
        ms.draw_bininfo(bincode, nbin_dataset)

        canvas.SaveAs(out_obj.get_path())
        hist_projection.Write()
        htemp.Delete()
        canvas.Clear()

ms.info_msg("Correction", "Correction plots saved!\n")
outputfile.Close()
