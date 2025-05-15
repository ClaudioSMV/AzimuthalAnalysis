import sys; sys.path.append('lib')
from ROOT import TFile, TH1F, kBlack
import optparse
from lib_style import force_style, create_canvas, draw_preliminary, draw_targetinfo,\
    draw_bininfo
from lib_cuts import get_list_of_bincodes
from lib_info_tag import convert_info_tag_str_to_list
from lib_error import info_msg
import lib_histograms as hi
import lib_naming as naming

force_style() # Defining Style

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', help="Dataset format: <targ>_<binType>_<Ndims>")
parser.add_option('-L', dest='run_local', action='store_true', default = False,
                  help="Run local files (Default uses folder from JLab_cluster)")
parser.add_option('-B', dest='bin_vars', default = "",
                  help="Work with these non-integratedd variables. Ex.: QNZ")
parser.add_option('-C', dest='cuts', default = "", help="Add input cuts FE_AQ_Xf_Yb_...")
parser.add_option('-s', dest='shift', action='store_true', default = False,
                  help="Moves x-axis to make shift fit later")

parser.add_option('-A', dest='save_all', action='store_true', default = False,
                  help="Save All plots")
parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")
options, args = parser.parse_args()

dataset = options.Dataset
run_local = options.run_local
binvars = options.bin_vars

in_obj = naming.processed_files_format("Correction", dataset, cuts=options.cuts,
                                       run_local=run_local)
inputfile = TFile(in_obj.get_file(), "READ")

out_obj = naming.analysis_format("Correction", dataset, binvars, cuts=options.cuts,
                                 run_local=run_local, fit_method="Sh"*options.shift)
outputfile_name = out_obj.get_file_root_files(options.Overwrite, True)

reco_methods = ["Reconstru", "Raw"]
if options.save_all: # Save regular correction method and raw data only
    reco_methods = ["Reconstru", "ReMtch_mc", "ReMtch_re", "Raw"]
input_hnames = [in_obj.get_histogram_name(method) for method in reco_methods]
input_histograms = [inputfile.Get(name) for name in input_hnames]

list_of_bincodes = get_list_of_bincodes(dataset, binvars)
list_of_projections_per_method = []
for (i, hist) in enumerate(input_histograms):
    projections_per_method = []
    for bincode in list_of_bincodes:
        name = out_obj.get_name_histogram(reco_methods[i], bincode)
        projection = hi.create_1D_projection_from_sparse(hist, name, bincode,
                                                         shift=options.shift)
        projections_per_method.append(projection)
    list_of_projections_per_method.append(projections_per_method)

# Create canvas
canvas = create_canvas()
outputfile = TFile(outputfile_name, "RECREATE")
target, nbin, _ = convert_info_tag_str_to_list(dataset)

for (i, list_projections) in enumerate(list_of_projections_per_method):
    for (j, projection) in enumerate(list_projections):
        bincode = list_of_bincodes[j]
        reco_method = reco_methods[i]
        # Create temporary histogram with required axis style
        xmin, xmax = projection.GetXaxis().GetXmin(), projection.GetXaxis().GetXmax()
        ymax = projection.GetMaximum() * 1.2 # Make every distribution fully visible!
        haxes = TH1F("haxes", "", 1, xmin, xmax)
        haxes.SetStats(0)
        haxes.SetMinimum(0.0001)
        haxes.SetMaximum(ymax)
        haxes.GetXaxis().SetTitle(projection.GetXaxis().GetTitle())
        haxes.GetYaxis().SetMaxDigits(3)
        haxes.GetYaxis().SetTitle(projection.GetYaxis().GetTitle())
        haxes.Draw("AXIS")

        # Draw projection
        projection.SetLineColor(kBlack)
        # gPad.RedrawAxis("g")
        projection.Draw("hist e same")

        # Draw annotations
        draw_preliminary(reco_method)
        # draw_targetinfo("%s_%i"%(target, nbin), "Data")
        draw_targetinfo(target, "Data")
        draw_bininfo(bincode, nbin=nbin)

        canvas.SaveAs(out_obj.get_file_plots(reco_method, bincode))
        projection.Write()
        haxes.Delete()
        canvas.Clear()

info_msg("Correction", "Correction plots saved!\n")
outputfile.Close()
