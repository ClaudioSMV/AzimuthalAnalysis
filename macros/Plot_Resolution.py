from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,\
TLegend,TEfficiency,TLine,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle as ms
import myNameFormat as nf
import math

gROOT.SetBatch(True)
gStyle.SetOptFit(1011)

## Defining Style
ms.force_style()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-D', dest='Dataset', default = "",
                  help="Dataset in format <targ>_<binType>")
parser.add_option('-J', dest='isJLab', action='store_true', default = False,
                  help="Use folder from JLab_cluster")
parser.add_option('-i', dest='inputCuts', default = "",
                  help="Add input cuts Xf_Yb_...")
parser.add_option('-o', dest='outputCuts', default = "",
                  help="Add output cuts FE_...")

parser.add_option('-O', dest='Overwrite', action='store_true', default = False,
                  help="Overwrite if file already exists")
parser.add_option('-d', dest='debugMode', action='store_true', default = False,
                  help="Run debug mode")

options, args = parser.parse_args()

dataset = options.Dataset
isJLab = options.isJLab
ovr = options.Overwrite
use_debug = options.debugMode

input_cuts = options.inputCuts
plots_cuts = options.inputCuts +"_"+ options.outputCuts

d_bin = ms.get_name_dict(dataset)

in_obj = nf.naming_format("Acceptance", dataset, cuts=input_cuts,
                          is_JLab=isJLab, in_output=True)
inputfile = TFile(in_obj.get_path_from_output(),"READ")

out_obj = nf.naming_format("Resolution", dataset, cuts=plots_cuts,
                          is_JLab=isJLab)
# outputfile = TFile(out_obj.get_path(True),"RECREATE")

# Create and save output
canvas = ms.create_canvas()
outputfile = TFile(out_obj.get_path(True, ovr), "RECREATE")

fit_limits = {
    'Q': [0.9, 1.1],
    'N': [1.1, 0.8],
    'Z': [0.9, 1.0],
    'P': [0.8, 0.8],
    'I': [1.1, 1.1],
    'X': [0.8, 1.0],
}

for v in ms.var_label.keys():
    var_name = ms.axis_label(v, "Name")
    var_axis_latex = ms.axis_label(v, "Latex")
    var_axis_units = ms.axis_label(v, "Unit")

    # Skip Xb or Nu when not in the file
    if (not inputfile.Get("res%s"%(var_name))):
        continue

    ##### Hist 1D #####
    fmin, fmax = fit_limits[v]
    h_res = inputfile.Get("res%s"%(var_name))

    myMean, myRMS = h_res.GetMean(), h_res.GetRMS()
    fit = TF1('fit', 'gaus', myMean - fmin*myRMS, myMean + fmax*myRMS)
    h_res.Fit(fit, "Q", "", myMean - fmin*myRMS, myMean + fmax*myRMS)
    h1_axis_title = "{0} - mc_{0} {1}".format(var_axis_latex, var_axis_units)
    h_res.GetXaxis().SetTitle(h1_axis_title)
    h_res.Draw("hist e")
    fit.Draw("same")

    ms.draw_preliminary("Resolution")
    ms.draw_targetinfo(ms.get_name_format(dataset), "Simulation")

    out_obj.updt_extension("png")
    out_name = "Resolution_1D-%s.%s"%(var_name, out_obj.extension)
    canvas.SaveAs("%s%s"%(out_obj.get_folder_name(), out_name))
    canvas.Clear()

    ##### Hist 2D - Projection #####
    h_migration2d = inputfile.Get("histMigrationMatrix%s"%var_name)
    h_mig_nbins = h_migration2d.GetXaxis().GetNbins()
    h_mig_xmin = h_migration2d.GetXaxis().GetXmin()
    h_mig_xmax = h_migration2d.GetXaxis().GetXmax()

    hname = "ResolutionVsX_%s"%(var_name)
    htitle = ";True %s;Resolution %s"%(var_axis_latex, var_axis_units)
    h_res_vs_x = TH1D(hname, htitle, h_mig_nbins, h_mig_xmin, h_mig_xmax)

    out_obj.updt_extension("png")
    for b in range(1, h_mig_nbins+1):
        totalEvents = h_migration2d.GetEntries()
        tmpHist = h_migration2d.ProjectionY("py",b,b)
        myMean = tmpHist.GetMean()
        myRMS = tmpHist.GetRMS()
        myRMSError = tmpHist.GetRMSError()
        nEvents = tmpHist.GetEntries()
        fitlow = myMean - 1.1*myRMS
        fithigh = myMean + 1.1*myRMS
        value = myRMS
        error = myRMSError

        minEvtsCut = totalEvents/h_mig_nbins

        if (nEvents > 0.05*minEvtsCut):
            fit = TF1('fit','gaus',fitlow,fithigh)
            tmpHist.Fit(fit,"Q", "", fitlow, fithigh)
            myMPV = fit.GetParameter(1)
            mySigma = fit.GetParameter(2)
            mySigmaError = fit.GetParError(2)
            value = mySigma
            error = mySigmaError
            
            # For Debugging
            if use_debug:
                tmpHist.Draw("hist")
                fit.Draw("same")
                res_msg = "Bin %i (%s = "%(b, var_name)
                res_msg+= "%.3f) "%(h_migration2d.GetXaxis().GetBinCenter(b))
                res_msg+= "with resolution %.3f +/- %.3f"%(value, error)
                print(res_msg)

                out_obj.updt_extension("png")
                dfolder = ms.create_folder(out_obj.get_folder_name(), "Debug", False, True)
                deb_name = "%sRes_vs_x-%s-%i.%s"%(dfolder, var_name, b, out_obj.extension)
                canvas.SaveAs(deb_name)
                canvas.Clear()
        else:
            print("Bin %i doesn't have enough statistics."%b)
            value = 0.0
            error = 0.0

        h_res_vs_x.SetBinContent(b,value)
        h_res_vs_x.SetBinError(b,error)


    h_res_vs_x.GetYaxis().SetRangeUser(0.0, 1.2*h_res_vs_x.GetMaximum())
    h_res_vs_x.Draw("hist e")
    ms.draw_preliminary("Resolution vs x")
    ms.draw_targetinfo(ms.get_name_format(dataset), "Simulation")

    out_obj.updt_extension("png")
    out_name = "Resolution_vs_x-%s.%s"%(var_name, out_obj.extension)
    canvas.SaveAs("%s%s"%(out_obj.get_folder_name(), out_name))

inputfile.Close()
