from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
import myNameFormat as nf

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
ms.force_style()


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>_<Ndims>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False, help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "", help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "", help="Add output cuts FE_Z_P_...")

parser.add_option('-A', dest='saveAll', action='store_true', default = False, help="Save All plots")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False, help="Overwrite if file already exists")

# input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0_2
options, args = parser.parse_args()

dataset = options.Dataset
isJLab = options.isJLab
saveAll = options.saveAll

d_bin = ms.get_name_dict(dataset)

input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

in_obj = nf.naming_format("Correction", dataset, cuts=input_cuts,
                          is_JLab=isJLab, in_output=True)
inputfile = TFile(in_obj.get_path_from_output(),"READ")

out_obj = nf.naming_format("Correction", dataset, cuts=plots_cuts,
                          is_JLab=isJLab)
# outputfile = TFile(out_obj.get_path(),"READ")

# Retrieve THnSparse
l_in_hname = ["Corr_Reconstru", "Corr_ReMtch_mc", "Corr_ReMtch_re", "Raw_data"]
l_inTHnSparse = []
for hname in l_in_hname:
    tmp_thSparse = inputfile.Get(hname)
    l_inTHnSparse.append(tmp_thSparse)

# l_in_pref = ["Corrected", "Corr GoodGen_mc", "Corr GoodGen_re", "Raw data"]
l_in_pref = ["Corrected", "Corr GMmc", "Corr GMre"] + ["Raw data"]
limits = ms.all_dicts[d_bin["nBin"]]

binstr = "Q"
binstr+= "N" if "X" not in limits else "X"
binstr+= ms.get_var_init(plots_cuts, True) # Z or P


# Create list with projections
l_bincodes = ms.get_bincode_list(binstr, limits)
l_Proj1DTHnSparse = []
use_shift = (ms.get_fit_method(plots_cuts, False) == "Sh")
for th in l_inTHnSparse:
    list_proj = ms.get_sparseproj1d_list(th, l_bincodes, use_shift)
    l_Proj1DTHnSparse.append(list_proj)

# Create and save output
canvas = ms.create_canvas()
outputfile = TFile(out_obj.get_path(True),"RECREATE")
phi_axis_title = ms.axis_label('I',"LatexUnit") # "#phi_{PQ} (deg)"

ROOT.TGaxis.SetExponentOffset(-0.07, 0.0, "y")

for i,info in enumerate(l_bincodes):
    for p,proj in enumerate(l_Proj1DTHnSparse):
        if (("GM" in l_in_pref[p]) and (not saveAll)):
            continue

        this_proj = proj[i]

        x_min = this_proj.GetXaxis().GetXmin()
        x_max = this_proj.GetXaxis().GetXmax()

        htemp = TH1F("htemp","",1, x_min,x_max)
        htemp.SetStats(0)
        htemp.SetMinimum(0.0001)
        # ylim = 30000
        ylim = this_proj.GetMaximum()*1.2
        htemp.SetMaximum(ylim)
        # htemp.SetLineColor(kBlack)
        htemp.GetXaxis().SetTitle(phi_axis_title)

        htemp.GetYaxis().SetMaxDigits(3)
        htemp.GetYaxis().SetTitle("Counts")
        htemp.Draw("AXIS")

        this_proj.SetLineColor(kBlack)

        # gPad.RedrawAxis("g")

        this_proj.Draw("hist e same")

        # legend.Draw();
        ms.draw_preliminary(l_in_pref[p])
        ms.draw_targetinfo(ms.get_name_format(dataset), "Data")
        ms.draw_bininfo(info, d_bin["nBin"])

        out_obj.updt_acc_method(l_in_hname[p])
        out_obj.updt_bin_code(info)
        out_obj.updt_extension("png")

        canvas.SaveAs(out_obj.get_path())

        this_proj.Write()
        htemp.Delete()
        canvas.Clear()

ms.info_msg("Correction", "Correction plots saved!\n")
outputfile.Close()

