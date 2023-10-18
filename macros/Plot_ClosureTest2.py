from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,\
TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import copy
import optparse
import myStyle as ms
import myNameFormat as nf

gROOT.SetBatch(True)

## Defining Style
ms.force_style()


def get_projection_list(infile, list_hname, list_bincode):
    list_projections = []
    for hname in list_hname:
        thSparse = infile.Get(hname)
        list_proj_bincode = ms.get_sparseproj1d_list(thSparse, list_bincode,
                                                     shift=False)
        list_projections.append(list_proj_bincode)

    return list_projections

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "",
                  help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "",
                  help="Add output cuts FE_Z_P_...")

parser.add_option('-f', dest='fracAcc', default = 50,
                  help="Stats' fraction used in Acc calculation (this/100.)")

parser.add_option('-A', dest='saveAll', action='store_true', default = False,
                  help="Save All plots")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")

# input: <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
isJLab = options.isJLab
ovr = options.Overwrite
saveAll = options.saveAll
fracAcc = int(options.fracAcc)

input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

d_bin = ms.get_name_dict(dataset)

in_obj = nf.naming_format("ClosureTest", dataset, cuts=input_cuts,
                          is_JLab=isJLab, in_output=True, fraction=fracAcc)
inputfile = TFile(in_obj.get_path_from_output(),"READ")

out_obj = nf.naming_format("ClosureTest", dataset, cuts=plots_cuts,
                          is_JLab=isJLab, fraction=fracAcc)
# outputfile = TFile(out_obj.get_path(True),"RECREATE")

# # Retrieve corrected THnSparse
# l_input_corr_hname = ["Corr_Reconstru", "Corr_ReMtch_mc", "Corr_ReMtch_re"]
# l_input_true_hname = ["True", "True_PionReco"]
# l_inTHnSparse = []
# for hname in (l_input_corr_hname + l_input_true_hname):
#     tmp_thSparse = inputfile.Get(hname)
#     l_inTHnSparse.append(tmp_thSparse)

# l_input_corr_type = ["Corrected", "Corr GMmc", "Corr GMre"]
# # l_input_true_type = ["True", "True_PionReco"]
# # limits = ms.all_dicts[d_bin["nBin"]]

# # Create list with projections
# l_bincodes = ms.get_bincode_list(d_bin["nBin"], plots_cuts)
# l_Proj1DTHnSparse = []
# # use_shift = (ms.get_fit_method(plots_cuts, True) == "Sh")
# for th in l_inTHnSparse:
#     list_proj = ms.get_sparseproj1d_list(th, l_bincodes) #, use_shift)
#     l_Proj1DTHnSparse.append(list_proj)

#########################  Make projections  #########################
l_bincodes = ms.get_bincode_list(d_bin["nBin"], plots_cuts)

# Corrected projections
l_input_corr_hname = ["Corr_Reconstru"]
if saveAll:
    l_input_corr_hname+= ["Corr_ReMtch_mc", "Corr_ReMtch_re"]
l_input_corr_type = ["Corrected", "Corr GMmc", "Corr GMre"]
l_projectedSparse_corr = get_projection_list(inputfile, l_input_corr_hname, l_bincodes)

# Thrown projections
l_input_true_hname = ["True", "True_PionReco"]
l_input_true_type = ["", "PiReco"]
l_projectedSparse_true = get_projection_list(inputfile, l_input_true_hname, l_bincodes)        

####################  Summary Closure Test info  #####################
l_summary = {"CT_value": [], "CT_error": [], "CT_error_base100": []}
for reco_meth in l_input_corr_hname:
    tmp_name = "Summary-CT%ip-Value-%s"%(fracAcc, reco_meth)
    th1_CT_value = TH1D(tmp_name, ";Closure value;Counts", 100, 0.21, 1.79)
    l_summary["CT_value"].append(th1_CT_value)

    tmp_name = "Summary-CT%ip-Error-%s"%(fracAcc, reco_meth)
    th1_CT_err = TH1D(tmp_name, ";Closure error;Counts", 100, 0.01, 0.79)
    l_summary["CT_error"].append(th1_CT_err)

    tmp_name = "Summary-CT%ip-Err100-%s"%(fracAcc, reco_meth)
    th1_CT_err100 = TH1D(tmp_name, ";Closure error %;Counts", 100, 0.0, 100.0)
    l_summary["CT_error_base100"].append(th1_CT_err100)

# Create and save output
canvas = ms.create_canvas()
canvas.SetGrid(0,1)
TH1.SetDefaultSumw2()
outputfile = TFile(out_obj.get_path(True, ovr),"RECREATE")
phi_axis_title = ms.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"

gStyle.SetTitleYOffset(1.2)

# Define axes histogram to be used
htemp = TH1F("htemp","",1,-180.,180.)
htemp.SetStats(0)
htemp.SetMinimum(0.3)
htemp.SetMaximum(1.7)
# htemp.SetLineColor(kBlack)
htemp.GetXaxis().SetTitle(phi_axis_title)
htemp.GetYaxis().SetTitle("Corr / True")

for idx,info in enumerate(l_bincodes):
    # TODO: Check why the PiReco plots are empty!
    for j,l_thrown in enumerate(l_projectedSparse_true):
        den = l_thrown[idx]
        for i,l_corr in enumerate(l_projectedSparse_corr):
            num = l_corr[idx]

            plot_obj = copy.copy(out_obj)
            plot_obj.updt_name(l_input_true_type[j], add=True)
            plot_obj.updt_acc_method(l_input_corr_hname[i])
            plot_obj.updt_bin_code(info)
            plot_obj.updt_extension("png")

            hClosure = num.Clone(plot_obj.get_hist_name())
            hClosure.Divide(num, den, 1, 1, "B")
            hClosure.SetLineColor(kBlack)

            htemp.Draw("AXIS")
            hClosure.Draw("hist e same")

            pre_title = "ClosureTest %i%% %s"%(fracAcc, l_input_corr_type[i])
            ms.draw_preliminary(pre_title)
            ms.draw_targetinfo(ms.get_name_format(dataset), "Simulation")
            ms.draw_bininfo(info, d_bin["nBin"])

            gPad.RedrawAxis("g")
            canvas.SaveAs(out_obj.get_folder_name() + plot_obj.get_file_name())

            hClosure.Write()
            canvas.Clear()

ms.info_msg("Closure Test", "Plots saved!\n")
outputfile.Close()
