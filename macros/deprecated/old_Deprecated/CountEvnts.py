from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2D,TH2F,TLatex,TMath,TColor,TLegend,TEfficiency,TGraphAsymmErrors,gROOT,gPad,TF1,gStyle,kBlack,kWhite,TH1
import ROOT
import os
import optparse
import myStyle

###############################################
###############################################
###############   DEPRECATED!   ###############
###############################################
#####   Check checkAccQuality.C instead   #####
###############################################
###############################################

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)

## Defining Style
myStyle.force_style()

# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
# parser.add_option('-x','--xlength', dest='xlength', default = 4.0, help="X axis range [-x, x]")
# parser.add_option('-y','--ylength', dest='ylength', default = 200.0, help="Y axis upper limit")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset in format <targ>_<binType>. Acc doesn't have <Ndim>")
parser.add_option('-p', dest='rootpath', default = "", help="Add path to files, if needed")
parser.add_option('-a', dest='saveAll', action='store_true', default = False, help="Save All plots")
parser.add_option('-J', dest='JLabCluster', action='store_true', default = False, help="Use folder from JLab_cluster")

# IDEA: input format->  <target>_<binningType number>_<non-integrated dimensions> ; ex: Fe_0
options, args = parser.parse_args()

saveAll = options.saveAll
rootpath = options.rootpath
dataset = options.Dataset
if options.JLabCluster: rootpath = "JLab_cluster"

infoDict = myStyle.get_name_dict(dataset)

inputPath = myStyle.getInputFile("Acceptance",dataset,rootpath) # Acceptance/Acceptance_Fe_B0.root
inputfile = TFile(inputPath,"READ")

outputPath = myStyle.getOutputDir("CountEvnts","",rootpath)

histTrue     = inputfile.Get("histTrue")
histReco     = inputfile.Get("histReco_rec")
histMtch_mc  = inputfile.Get("histReco_mc")
histMtch_rec = inputfile.Get("histTrue_rec")

list_THnSparse = [histTrue, histReco, histMtch_mc, histMtch_rec]
prefixType = ["True", "Reco", "Mtch_mc", "Mtch_rec"]


## MAKE THIS MACRO TO RUN OVER ALL THE BINS IN A THNSPARSE AND STORE THE FRACTION OF EVENTS, BOTH AS:
##      this_evnts / Total_bins     &       this_evnts / Total_FILLED_bins
## Store this in a 1D histogram and check what happens...
## Later I could get different "projections" by using GetBinContent(2,a), where a stores the bin numbers per axis

nameFormatted = myStyle.get_name_format(dataset)
outputfile = TFile(outputPath+"Count_"+infoDict["Target"]+".root","RECREATE")

list_EvntsOverTotal = []
list_EvntsOverFilled = []
list_EvntsOverTotal_NoEmpty = []
list_EvntsOverFilled_NoEmpty = [] ## COULD SAVE RATIO OF EVNTS/ EXPECTED VALUE! THIS LAST IS TOT_EVTS/NBINS
for p,pref in enumerate(prefixType):
    hist_EvntsOverTotal  = TH1F("EvntsTotal_%s"%pref,  "Events over expected, Total, %s;Evnt/ExpTotal;Counts"%pref,  400, 0.0, 10.0)
    list_EvntsOverTotal.append(hist_EvntsOverTotal)
    hist_EvntsOverFilled = TH1F("EvntsFilled_%s"%pref, "Events over expected, Filled, %s;Evnt/ExpFilled;Counts"%pref, 400, 0.0, 10.0)
    list_EvntsOverFilled.append(hist_EvntsOverFilled)

    hist_EvntsOverTotal_NoEmpty  = TH1F("EvntsTotal_NoEmpty_%s"%pref,  "Events over expected, No empty total, %s;Evnt/ExpTotal;Counts"%pref,  400, 0.0, 10.0)
    list_EvntsOverTotal_NoEmpty.append(hist_EvntsOverTotal_NoEmpty)
    hist_EvntsOverFilled_NoEmpty = TH1F("EvntsFilled_NoEmpty_%s"%pref, "Events over expected, No empty filled, %s;Evnt/ExpFilled;Counts"%pref, 400, 0.0, 10.0)
    list_EvntsOverFilled_NoEmpty.append(hist_EvntsOverFilled_NoEmpty)

tot_bins = 1
for i in range(5):
    tot_bins*= histTrue.GetAxis(i).GetNbins()

for h,hist in enumerate(list_THnSparse):
    filled_bins = hist.GetNbins()

    tot_evnts = hist.GetEntries()
    expected_evnts_tot = tot_evnts/tot_bins
    expected_evnts_fill = tot_evnts/filled_bins
    for i in range(1,tot_bins+1):
        evnts_in_bin = hist.GetBinContent(i)
        # if i<5: print("Totl: %.3f"%(evnts_in_bin/tot_evnts))
        # if i<5: print("Fill: %.3f"%(evnts_in_bin/filled_bins))
        list_EvntsOverTotal[h].Fill(evnts_in_bin/expected_evnts_tot)
        list_EvntsOverFilled[h].Fill(evnts_in_bin/expected_evnts_fill)
        if evnts_in_bin!=0:
            list_EvntsOverTotal_NoEmpty[h].Fill(evnts_in_bin/expected_evnts_tot)
            list_EvntsOverFilled_NoEmpty[h].Fill(evnts_in_bin/expected_evnts_fill)



canvas = TCanvas("cv","cv",1000,800)
# canvas.SetGrid(0,1)
# gPad.SetTicks(1,1)
# TH1.SetDefaultSumw2()
# gStyle.SetOptStat(0)


# Plot histograms
for h,hist in enumerate(list_THnSparse):
    list_EvntsOverTotal[h].Draw()
    canvas.SaveAs(outputPath+"CountTotal_"+infoDict["Target"]+"_"+prefixType[h]+".png")
    canvas.Clear()

    list_EvntsOverFilled[h].Draw()
    canvas.SaveAs(outputPath+"CountFill_"+infoDict["Target"]+"_"+prefixType[h]+".png")
    canvas.Clear()

    list_EvntsOverTotal_NoEmpty[h].Draw()
    canvas.SaveAs(outputPath+"CountTotal_NoEmpty_"+infoDict["Target"]+"_"+prefixType[h]+".png")
    canvas.Clear()

    list_EvntsOverFilled_NoEmpty[h].Draw()
    canvas.SaveAs(outputPath+"CountFill_NoEmpty_"+infoDict["Target"]+"_"+prefixType[h]+".png")
    canvas.Clear()

print("Finished!")
outputfile.Write()
outputfile.Close()

