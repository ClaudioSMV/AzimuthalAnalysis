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

def fill_th1(dict_th1, hclosure):
    for b in range(1, hclosure.GetXaxis().GetNbins()+1):
        value = hclosure.GetBinContent(b)
        error = hclosure.GetBinError(b)

        dict_th1["CT_value"].Fill(value)
        dict_th1["CT_error"].Fill(error)
        if (value!=0):
            dict_th1["CT_error_base100"].Fill(100.*error/value)
        else:
            hname = hclosure.GetName()
            print(" >> %s - Bin %i is empty :c"%(hname,b))

def draw_th1(dict_th1, canvas, output_obj):
    # TODO: Update this to use .cut or sth and extract non-integrated vars info
    var_initials = ms.get_plot_initials(output_obj.n_bin, output_obj.cuts)
    var_txt = ""
    for v in var_initials:
        var_txt+= "%s, "%ms.axis_label(v, "Latex")
    var_txt = "Bins of (%s)"%(var_txt[:-2])
    # var_txt = var_txt[:-2]
    # top_text = {
    #     "CT_value": "Closure test (%s)"%var_txt,
    #     "CT_error": "Closure error (%s)"%var_txt,
    #     "CT_error_base100": "Closure error %% (%s)"%var_txt,
    # }
    top_text = {
        "CT_value": "Closure test",
        "CT_error": "Closure error",
        "CT_error_base100": "Closure error %%",
    }

    for quantity, th1 in dict_th1.items():
        th1.SetLineColor(kBlack)
        th1.SetTitleOffset(1.3,"y")
        th1.Draw()

        ms.draw_summary(top_text[quantity], xl=0.01)
        ms.draw_preliminary(var_txt, xl=0.01, yb=-0.08)
        ms.draw_targetinfo(output_obj.target, "Simulation")
        save_path = "%s%s.png"%(output_obj.get_folder_name(), th1.GetName())
        canvas.SaveAs(save_path)
        th1.Write()
        canvas.Clear()

def get_dict_with_summary(dict_list_th1, idx):
    this_dict = {}
    for key,th1list in dict_list_th1.items():
        this_dict[key] = th1list[idx]

    return this_dict


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

##############################  Make projections  ##############################
l_bincodes = ms.get_bincode_list(d_bin["nBin"], plots_cuts)

# Corrected projections
l_input_corr_hname = ["Corr_Reconstru"]
if saveAll:
    l_input_corr_hname+= ["Corr_ReMtch_mc", "Corr_ReMtch_re"]
l_input_corr_type = ["Corrected", "Corr GMmc", "Corr GMre"]
l_projHist_corr = get_projection_list(inputfile, l_input_corr_hname, l_bincodes)

# Thrown projections
l_input_true_hname = ["True", "True_PionReco"]
l_input_true_type = ["", "PiReco"]
l_projHist_true = get_projection_list(inputfile, l_input_true_hname, l_bincodes)

#########################  Summary Closure Test info  ##########################
l_summary_dict = []
for thrown in ["", "_P"]:
    this_summary = {"CT_value": [], "CT_error": [], "CT_error_base100": []}
    for reco_meth in l_input_corr_hname:
        mname = nf.get_acc_meth(reco_meth, "S")
        tmp_name = "Summary-CT%s%ip-Value-%s"%(thrown, fracAcc, mname)
        tmp_axes = ";Closure value;Counts"
        th1_CT_value = TH1D(tmp_name, tmp_axes, 100, 0.21, 1.79)
        this_summary["CT_value"].append(th1_CT_value)

        tmp_name = "Summary-CT%s%ip-Error-%s"%(thrown, fracAcc, mname)
        tmp_axes = ";Closure error;Counts"
        th1_CT_err = TH1D(tmp_name, tmp_axes, 100, 0.01, 0.79)
        this_summary["CT_error"].append(th1_CT_err)

        tmp_name = "Summary-CT%s%ip-Err100-%s"%(thrown, fracAcc, mname)
        tmp_axes = ";Closure error %;Counts"
        th1_CT_err100 = TH1D(tmp_name, tmp_axes, 100, 0.0, 100.0)
        this_summary["CT_error_base100"].append(th1_CT_err100)
    l_summary_dict.append(this_summary)

###########################  Create and fill canvas  ###########################
canvas = ms.create_canvas()
canvas.SetGrid(0,1)
TH1.SetDefaultSumw2()
outputfile = TFile(out_obj.get_path(True, ovr),"RECREATE")
phi_axis_title = ms.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"

gStyle.SetTitleYOffset(1.3)

# Define axes histogram to be used
htemp = TH1F("htemp","",1,-180.,180.)
htemp.SetStats(0)
htemp.SetMinimum(0.3)
htemp.SetMaximum(1.7)
# htemp.SetLineColor(kBlack)
htemp.GetXaxis().SetTitle(phi_axis_title)
htemp.GetYaxis().SetTitle("Corr / True")

# NOTE: PiReco thrown ClosureTest gives an idea of how many extra events are
# reconstructed (i.e. no real ones)
for j,l_thrown in enumerate(l_projHist_true):
    dsummaries_list = l_summary_dict[j]
    for i,l_corr in enumerate(l_projHist_corr):
        dsummary = get_dict_with_summary(dsummaries_list, i)
        for idx,info in enumerate(l_bincodes):
            num = l_corr[idx]
            den = l_thrown[idx]

            plot_obj = copy.copy(out_obj)
            plot_obj.updt_name(l_input_true_type[j], add=True)
            plot_obj.updt_acc_method(l_input_corr_hname[i])
            plot_obj.updt_bin_code(info)
            plot_obj.updt_extension("png")

            hClosure = num.Clone(plot_obj.get_hist_name())
            hClosure.Divide(num, den, 1, 1, "B")
            hClosure.SetLineColor(kBlack)

            htemp.Draw("AXIS")
            gPad.RedrawAxis("g")
            hClosure.Draw("hist e same")

            pre_title = "ClosureTest %i%% %s"%(fracAcc, l_input_corr_type[i])
            pre_title = "Closure test"
            ms.draw_preliminary(pre_title)
            # ms.draw_targetinfo(ms.get_name_format(dataset), "Simulation")
            ms.draw_targetinfo(ms.get_name_dict(dataset)["Target"], "Simulation")
            ms.draw_bininfo(info, d_bin["nBin"])

            canvas.SaveAs(out_obj.get_folder_name() + plot_obj.get_file_name())

            hClosure.Write()

            # Fill summary th1
            fill_th1(dsummary, hClosure)
            canvas.Clear()
        # Draw and save summary th1s
        draw_th1(dsummary, canvas, out_obj)

ms.info_msg("Closure Test", "Plots saved!\n")
outputfile.Close()
