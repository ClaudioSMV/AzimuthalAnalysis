#define Acceptance_cxx
#include "Binning.h"
#include "Acceptance.h"
#include "Utility.h"
#include "Style.h"
#include <TEfficiency.h>
#include <TH1.h>
#include <TH2.h>
#include <TH3.h>
#include <THnSparse.h>
#include <TMath.h>
#include <TStyle.h>
#include <TCanvas.h>

#include <iostream>
#include <vector>
#include <string>

// Don't forget to define >> using namespace DIS_original; << Inside every method, depending on the binning needed.

inline float DEG2RAD(float x)
{
    return 0.017453293 * x;
}

void Acceptance::ActivateBranches()
{
    fChain->SetBranchStatus("*",0);
    std::vector<string> activeBranches = {"TargType", "Q2", "Nu", "Xb", "Yb", "W", "vyec", "Zh", "Pt2", "PhiPQ", "pid"}; // , "Nphe"}; //, "Xf"};
    std::vector<string> activeBranches_mc = {"mc_TargType", "mc_Q2", "mc_Nu", "mc_Xb", "mc_Yb", "mc_W", "mc_Zh", "mc_Pt2", "mc_PhiPQ", "mc_pid"}; //, "mc_Xf"};
    for (const auto &activeBranch : activeBranches)
    {
        fChain->SetBranchStatus(activeBranch.c_str(), 1);
    }

    if (!_isData)
    {
        for (const auto &activeBranch : activeBranches_mc)
        {
            fChain->SetBranchStatus(activeBranch.c_str(), 1);
        }
    }
}

void Acceptance::Loop(bool SaveAcceptance=true)
{
    //   In a ROOT session, you can do:
    //      root> .L Acceptance.C
    //      root> Acceptance t
    //      root> t.GetEntry(12); // Fill t data members with entry number 12
    //      root> t.Show();       // Show values of entry 12
    //      root> t.Show(16);     // Read and show values of entry 16
    //      root> t.Loop();       // Loop on all entries
    //

    //     This is the loop skeleton where:
    //    jentry is the global entry number in the chain
    //    ientry is the entry number in the current Tree
    //  Note that the argument to GetEntry must be:
    //    jentry for TChain::GetEntry
    //    ientry for TTree::GetEntry and TBranch::GetEntry
    //
    //       To read only selected branches, Insert statements like:
    // METHOD1:
    //    fChain->SetBranchStatus("*",0);  // disable all branches
    //    fChain->SetBranchStatus("branchname",1);  // activate branchname

    using namespace DIS_original;
    ActivateBranches();

    TFile *fout;
    if (SaveAcceptance) fout = TFile::Open(Form("../output/Acceptance_%s.root", getNameTarget().c_str()), "RECREATE");
    else                fout = TFile::Open("../output/Acc_ClosureTest.root", "RECREATE");

    std::cout << "\n\nBeginning Acceptance calculations for " << _nameTarget << " target\n" << std::endl;

    // Define binning
    // OR : Original: {3, 3, 5, 5, 12} = 2700
	// CP : PhiPQ central peak: {3, 3, 5, 5, 40} = 9000 // PhiPQ binning is really important due to the features seen!
	// Int_t nbins[5] = {3, 3, 5, 5, 40};
    double* minbins = &DISLimits[0][0];
    double* maxbins = &DISLimits[1][0];

    // Set variable width bins
	Double_t *Q2_Lmts  = &Q2_binng[0]; // {1.0, 1.3, 1.8, 4.1};
	Double_t *Nu_Lmts  = &Nu_binng[0]; // {2.2, 3.2, 3.7, 4.2};
	Double_t *Zh_Lmts  = &Zh_binng[0]; // {0.0, 0.15, 0.25, 0.4, 0.7, 1.0};
	Double_t *Pt2_Lmts = &Pt2_binng[0];// {0.0, 0.03, 0.06, 0.1, 0.18, 1.0};
    Double_t *PhiPQ_Lmts = &PhiPQ_binng[0];

    // TH1::SetDefaultSumw2();

    //// Define Histograms
    // one-dimensional efficiency histogramss
    TEfficiency* effZh = new TEfficiency("effZh", "effZh;z_{h};Reconstruction Efficiency", 20, DISLimits[0][2], DISLimits[1][2]);
    TEfficiency* effPt2 = new TEfficiency("effPt2", "effPt2;p_{T}^{2} (GeV^{2});Reconstruction Efficiency", 20, DISLimits[0][3], DISLimits[1][3]);
    TEfficiency* effPhiPQ = new TEfficiency("effPhiPQ", "effPhiPQ;#phi_{PQ} (deg);Reconstruction Efficiency", 60, DISLimits[0][4], DISLimits[1][4]);

    // bin Migration
    TH2F* histMigrationMatrixZh = new TH2F("histMigrationMatrixZh", "MigrationZh;True z_{h}; Reco z_{h}", 50, DISLimits[0][2], DISLimits[1][2], 50, DISLimits[0][2], DISLimits[1][2]);
    TH2F* histMigrationMatrixPt2 = new TH2F("histMigrationMatrixPt2", "MigrationPt2;True p_{T}^{2} (GeV^{2});Reco p_{T}^{2} (GeV^{2})", 50, DISLimits[0][3], DISLimits[1][3], 50, DISLimits[0][3], DISLimits[1][3]);
    TH2F* histMigrationMatrixPhiPQ = new TH2F("histMigrationMatrixPhiPQ", "MigrationPhiPQ;True #phi_{PQ} (deg);Reco #phi_{PQ} (deg)", 120, DISLimits[0][4], DISLimits[1][4], 120, DISLimits[0][4], DISLimits[1][4]);

    // THnSparse
    THnSparse *histTrue = new THnSparseD("histTrue","True", 5,nbins,minbins,maxbins);
    THnSparse *histReco_rec = new THnSparseD("histReco_rec","Reconstructed only", 5,nbins,minbins,maxbins);
    THnSparse *histReco_mc = new THnSparseD("histReco_mc","Good reconstructed with mc_vars", 5,nbins,minbins,maxbins);
    THnSparse *histTrue_rec = new THnSparseD("histTrue_rec","Good reconstructed with reco_vars", 5,nbins,minbins,maxbins);
	// THnSparse *histAcce_mc  = new THnSparseD("histAcce_mc","Acceptance with mc_vars", 5,nbins,minbins,maxbins);
	// THnSparse *histAcce_rec  = new THnSparseD("histAcce_rec","Acceptance with reco_vars", 5,nbins,minbins,maxbins);

    SetVariableSize(histTrue, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);     // Good Generated (Doesn't care of Reco), filled with Generated kinematic vars
    SetVariableSize(histReco_rec, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts); // Good Reco (Doesn't care of Generated), filled with Reco kinematic vars
    SetVariableSize(histReco_mc, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);  // Good Reco & Generated, filled with Generated kinematic vars
    SetVariableSize(histTrue_rec, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts); // Good Reco & Generated, filled with Reco kinematic vars
    // SetVariableSize(histAcce_mc,  nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    // SetVariableSize(histAcce_rec,  nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);

	histTrue->Sumw2();
	histReco_rec->Sumw2();
	histReco_mc->Sumw2();
	histTrue_rec->Sumw2();
	// histAcce_mc->Sumw2();
	// histAcce_rec->Sumw2();

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    unsigned int entries_to_process;
    if (SaveAcceptance) entries_to_process = nentries;
    else                entries_to_process = nentries/2;
    int global_bin=-1, inclusive_count=0;
    int vec_entries_MC=0, vec_entries=0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;

    std::map<std::string, unsigned int> general_El_count = {{"Total mc_El",0}, {"Total rec_El",0}, {"Different vector size",0}};
    std::map<std::string, unsigned int> mc_El_Reject_count = {{"Wrong mc_TargType",0}, {"Out of DIS range",0}, {"Not accepted",0}};
    std::map<std::string, unsigned int> mc_El_Accept_count = {{"Well reconstructed",0}};
    std::map<std::string, unsigned int> rec_El_Reject_count = {{"Wrong TargType",0}, {"Out of DIS range",0}, {"Out of VertexY Correction",0},{"Not good El",0}};
    std::map<std::string, unsigned int> rec_El_Accept_count = {{"Good match with mc",0}, {"Bad match with mc",0}};
    std::map<std::string, unsigned int> general_Pi_count = {{"Total mc_Pi",0}, {"Total rec_Pi",0}};
    std::map<std::string, unsigned int> mc_Pi_Reject_count = {{"Wrong mc_pid",0}, {"Out of DIS range",0}, {"Not accepted",0}};
    std::map<std::string, unsigned int> mc_Pi_Accept_count = {{"Well reconstructed",0}};
    std::map<std::string, unsigned int> rec_Pi_Reject_count = {{"Wrong pid",0}, {"Out of DIS range",0}, {"Not accepted",0}};
    std::map<std::string, unsigned int> rec_Pi_Accept_count = {{"Good match with mc",0}, {"Bad match with mc",0}};

    // std::map<std::string, unsigned int> mc_Pi_Good_count = {{"Leading mc_Pion",0}, {"No Leading mc_Pion",0}};
    // std::map<std::string, unsigned int> rec_Pi_Good_count = {{"Good Reco Pi",0}}; // ,{"Leading Pion",0}, {"No Leading Pion",0}};

    std::vector<double> leptonic_vars_mc, leptonic_vars;
    for (unsigned int jentry = 0; jentry < entries_to_process; jentry++)
    {
        if (jentry % 1000000 == 0)
            printf("Processing entry %9u, progress at %6.2f%%\n",jentry,100.*(double)jentry/(entries_to_process));

        // std::cout << "Processing entry " << jentry << ", progress at " << 100.*(double) jentry / (entries_to_process) << "%" << std::endl;
        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        // if (Cut(ientry) < 0) continue;
        good_electron_mc = false, good_electron = false;

        if (GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
            general_El_count["Total mc_El"]++;
        }
        else
        {
            mc_El_Reject_count["Not accepted"]++;
            if (mc_TargType!=_targTypeCut) mc_El_Reject_count["Wrong mc_TargType"]++;
            if (mc_Q2<DISLimits[0][0] || DISLimits[1][0]<mc_Q2 || 0.85<mc_Yb || mc_W<2 || mc_Nu<DISLimits[0][1] || DISLimits[1][1]<mc_Nu) mc_El_Reject_count["Out of DIS range"]++;
        }

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
            general_El_count["Total rec_El"]++;
            if (good_electron_mc)
            {
                rec_El_Accept_count["Good match with mc"]++;
                mc_El_Accept_count["Well reconstructed"]++;
            }
            else rec_El_Accept_count["Bad match with mc"]++;
        }
        else
        {
            rec_El_Reject_count["Not good El"]++;
            if (TargType!=_targTypeCut) rec_El_Reject_count["Wrong TargType"]++;
            if (Q2<DISLimits[0][0] || DISLimits[1][0]<Q2 || 0.85<Yb || W<2 || Nu<DISLimits[0][1] || DISLimits[1][1]<Nu) rec_El_Reject_count["Out of DIS range"]++;
            if (vyec<-1.4 || 1.4<vyec) rec_El_Reject_count["Out of VertexY Correction"]++;
        }

        leptonic_vars = {Q2, Nu};
        global_bin = GlobalVarPosition(&leptonic_vars, &leptonic_limits);

        vec_entries = PhiPQ->size();
        vec_entries_MC = mc_PhiPQ->size();
        if (vec_entries!=vec_entries_MC)
        {
            general_El_count["Different vector size"]++;
            continue;
        }

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;
            bool pion_passed(false);
            inclusive_count++;

            if (good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
                general_Pi_count["Total mc_Pi"]++;
            }
            else
            {
                mc_Pi_Reject_count["Not accepted"]++;
                if (mc_pid->at(i)!=211) mc_Pi_Reject_count["Wrong mc_pid"]++;
                if (mc_Zh->at(i)<DISLimits[0][2] || DISLimits[1][2]<mc_Zh->at(i) || mc_Pt2->at(i)<DISLimits[0][3] || DISLimits[1][3]<mc_Pt2->at(i) ||
                    mc_PhiPQ->at(i)<DISLimits[0][4] || DISLimits[1][4]<mc_PhiPQ->at(i)) mc_Pi_Reject_count["Out of DIS range"]++;
            }
            
            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                good_pion = true;
                general_Pi_count["Total rec_Pi"]++;
                if (good_pion_mc)
                {
                    mc_Pi_Accept_count["Well reconstructed"]++;
                    rec_Pi_Accept_count["Good match with mc"]++;
                }
                else rec_Pi_Accept_count["Bad match with mc"]++;
            }
            else
            {
                rec_Pi_Reject_count["Not accepted"]++;
                if (pid->at(i)!=211) rec_Pi_Reject_count["Wrong pid"]++;
                if (Zh->at(i)<DISLimits[0][2] || DISLimits[1][2]<Zh->at(i) || Pt2->at(i)<DISLimits[0][3] || DISLimits[1][3]<Pt2->at(i) ||
                    PhiPQ->at(i)<DISLimits[0][4] || DISLimits[1][4]<PhiPQ->at(i)) rec_Pi_Reject_count["Out of DIS range"]++;
            }

            if (!good_pion_mc && !good_pion) continue;

            double mc_bin[] = {mc_Q2, mc_Nu, mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i)};
            double rec_bin[] = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};

            if (good_pion_mc)
            {
                histTrue->Fill(mc_bin);
            }
            
            if (good_pion)
            {
                histReco_rec->Fill(rec_bin);
            }

            if (good_pion_mc && good_pion)
            {
                pion_passed = true;
                histMigrationMatrixZh->Fill(mc_Zh->at(i), Zh->at(i));
                histMigrationMatrixPt2->Fill(mc_Pt2->at(i), Pt2->at(i));
                histMigrationMatrixPhiPQ->Fill(mc_PhiPQ->at(i), PhiPQ->at(i));

                histReco_mc->Fill(mc_bin);
                histTrue_rec->Fill(rec_bin);
            }

            effZh->Fill(pion_passed ,mc_Zh->at(i));
            effPt2->Fill(pion_passed ,mc_Pt2->at(i));
            effPhiPQ->Fill(pion_passed ,mc_PhiPQ->at(i));
        }   // loop over tracks
    }       // loop over entries

    // Acceptance
    THnSparse *histAcc_Reconstructed = (THnSparse*)histReco_rec->Clone("histAcc_Reconstructed");
    histAcc_Reconstructed->Divide(histTrue);
    THnSparse *histAcc_RecGoodGen_mc = (THnSparse*)histReco_mc->Clone( "histAcc_RecGoodGen_mc");
    histAcc_RecGoodGen_mc->Divide(histTrue);
    THnSparse *histAcc_RecGoodGen_rec = (THnSparse*)histTrue_rec->Clone("histAcc_RecGoodGen_rec");
    histAcc_RecGoodGen_rec->Divide(histTrue);

    // Summary tables
    std::cout << std::endl;
    PrintSummaryTable(general_El_count,     "General Electron Summary", entries_to_process);
    PrintSummaryTable(mc_El_Reject_count,   "Rejected MC Electron", entries_to_process);
    PrintSummaryTable(mc_El_Accept_count,   "Correctly reconstructed MC Electrons", general_El_count["Total mc_El"]);
    PrintSummaryTable(rec_El_Reject_count,  "Rejected reco Electrons", entries_to_process);
    PrintSummaryTable(rec_El_Accept_count,  "Matching of reconstructed Electrons", general_El_count["Total rec_El"]);
    PrintSummaryTable(general_Pi_count,     "General Pion Summary", inclusive_count);
    PrintSummaryTable(mc_Pi_Reject_count,   "Rejected MC Pion", inclusive_count);
    PrintSummaryTable(mc_Pi_Accept_count,   "Correctly reconstructed MC Pions", general_Pi_count["Total mc_Pi"]);
    PrintSummaryTable(rec_Pi_Reject_count,  "Rejected reco Pions", inclusive_count);
    PrintSummaryTable(rec_Pi_Accept_count,  "Matching of reconstructed Pions", general_Pi_count["Total rec_Pi"]);

    histTrue->Write();
    histReco_rec->Write();
    histReco_mc->Write();
    histTrue_rec->Write();

    histAcc_Reconstructed->Write();
    histAcc_RecGoodGen_mc->Write();
    histAcc_RecGoodGen_rec->Write();

    fout->Write();
    fout->Close();
}

void Acceptance::Get2DProj()
{
    using namespace DIS_original;
    ActivateBranches();

    TFile *fout;
    if (_isData) fout = TFile::Open(Form("../output/Get2DProj_%s_data.root", getNameTarget().c_str()), "RECREATE");
    else         fout = TFile::Open(Form("../output/Get2DProj_%s_hsim.root", getNameTarget().c_str()), "RECREATE");

    //// Define Histograms
    // Reconstructed or data
    TH2D* hist2D_Q2_Nu_reco = new TH2D("hist2D_Q2_Nu_reco", "Two dimensional Map;Q^{2} [GeV^{2}];#nu [GeV]",          50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][1], DISLimits[1][1]);
    TH2D* hist2D_Q2_Zh_reco = new TH2D("hist2D_Q2_Zh_reco", "Two dimensional Map;Q^{2} [GeV^{2}];Z_{h}",              50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Q2_Pt_reco = new TH2D("hist2D_Q2_Pt_reco", "Two dimensional Map;Q^{2} [GeV^{2}];P_{t}^{2} [GeV^{2}]",50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Q2_PQ_reco = new TH2D("hist2D_Q2_PQ_reco", "Two dimensional Map;Q^{2} [GeV^{2}];#phi_{PQ} [deg]",    50, DISLimits[0][0], DISLimits[1][0], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Nu_Zh_reco = new TH2D("hist2D_Nu_Zh_reco", "Two dimensional Map;#nu [GeV];Z_{h}",                    50, DISLimits[0][1], DISLimits[1][1],  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Nu_Pt_reco = new TH2D("hist2D_Nu_Pt_reco", "Two dimensional Map;#nu [GeV];P_{t}^{2} [GeV^{2}]",      50, DISLimits[0][1], DISLimits[1][1],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Nu_PQ_reco = new TH2D("hist2D_Nu_PQ_reco", "Two dimensional Map;#nu [GeV];#phi_{PQ} [deg]",          50, DISLimits[0][1], DISLimits[1][1], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Zh_Pt_reco = new TH2D("hist2D_Zh_Pt_reco", "Two dimensional Map;Z_{h};P_{t}^{2} [GeV^{2}]",          50, DISLimits[0][2], DISLimits[1][2],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Zh_PQ_reco = new TH2D("hist2D_Zh_PQ_reco", "Two dimensional Map;Z_{h};#phi_{PQ} [deg]",              50, DISLimits[0][2], DISLimits[1][2], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Pt_PQ_reco = new TH2D("hist2D_Pt_PQ_reco", "Two dimensional Map;P_{t}^{2} [GeV^{2}];#phi_{PQ} [deg]",50, DISLimits[0][3], DISLimits[1][3], 180, DISLimits[0][4], DISLimits[1][4]);

    // Reconstructed match
    TH2D* hist2D_Q2_Nu_mtch = new TH2D("hist2D_Q2_Nu_mtch", "Two dimensional Map (Reco match);Q^{2} [GeV^{2}];#nu [GeV]",          50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][1], DISLimits[1][1]);
    TH2D* hist2D_Q2_Zh_mtch = new TH2D("hist2D_Q2_Zh_mtch", "Two dimensional Map (Reco match);Q^{2} [GeV^{2}];Z_{h}",              50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Q2_Pt_mtch = new TH2D("hist2D_Q2_Pt_mtch", "Two dimensional Map (Reco match);Q^{2} [GeV^{2}];P_{t}^{2} [GeV^{2}]",50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Q2_PQ_mtch = new TH2D("hist2D_Q2_PQ_mtch", "Two dimensional Map (Reco match);Q^{2} [GeV^{2}];#phi_{PQ} [deg]",    50, DISLimits[0][0], DISLimits[1][0], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Nu_Zh_mtch = new TH2D("hist2D_Nu_Zh_mtch", "Two dimensional Map (Reco match);#nu [GeV];Z_{h}",                    50, DISLimits[0][1], DISLimits[1][1],  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Nu_Pt_mtch = new TH2D("hist2D_Nu_Pt_mtch", "Two dimensional Map (Reco match);#nu [GeV];P_{t}^{2} [GeV^{2}]",      50, DISLimits[0][1], DISLimits[1][1],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Nu_PQ_mtch = new TH2D("hist2D_Nu_PQ_mtch", "Two dimensional Map (Reco match);#nu [GeV];#phi_{PQ} [deg]",          50, DISLimits[0][1], DISLimits[1][1], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Zh_Pt_mtch = new TH2D("hist2D_Zh_Pt_mtch", "Two dimensional Map (Reco match);Z_{h};P_{t}^{2} [GeV^{2}]",          50, DISLimits[0][2], DISLimits[1][2],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Zh_PQ_mtch = new TH2D("hist2D_Zh_PQ_mtch", "Two dimensional Map (Reco match);Z_{h};#phi_{PQ} [deg]",              50, DISLimits[0][2], DISLimits[1][2], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Pt_PQ_mtch = new TH2D("hist2D_Pt_PQ_mtch", "Two dimensional Map (Reco match);P_{t}^{2} [GeV^{2}];#phi_{PQ} [deg]",50, DISLimits[0][3], DISLimits[1][3], 180, DISLimits[0][4], DISLimits[1][4]);

    // Generated (MC)
    TH2D* hist2D_Q2_Nu_gene = new TH2D("hist2D_Q2_Nu_gene", "Two dimensional Map (Generated);Q^{2} [GeV^{2}];#nu [GeV]",          50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][1], DISLimits[1][1]);
    TH2D* hist2D_Q2_Zh_gene = new TH2D("hist2D_Q2_Zh_gene", "Two dimensional Map (Generated);Q^{2} [GeV^{2}];Z_{h}",              50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Q2_Pt_gene = new TH2D("hist2D_Q2_Pt_gene", "Two dimensional Map (Generated);Q^{2} [GeV^{2}];P_{t}^{2} [GeV^{2}]",50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Q2_PQ_gene = new TH2D("hist2D_Q2_PQ_gene", "Two dimensional Map (Generated);Q^{2} [GeV^{2}];#phi_{PQ} [deg]",    50, DISLimits[0][0], DISLimits[1][0], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Nu_Zh_gene = new TH2D("hist2D_Nu_Zh_gene", "Two dimensional Map (Generated);#nu [GeV];Z_{h}",                    50, DISLimits[0][1], DISLimits[1][1],  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Nu_Pt_gene = new TH2D("hist2D_Nu_Pt_gene", "Two dimensional Map (Generated);#nu [GeV];P_{t}^{2} [GeV^{2}]",      50, DISLimits[0][1], DISLimits[1][1],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Nu_PQ_gene = new TH2D("hist2D_Nu_PQ_gene", "Two dimensional Map (Generated);#nu [GeV];#phi_{PQ} [deg]",          50, DISLimits[0][1], DISLimits[1][1], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Zh_Pt_gene = new TH2D("hist2D_Zh_Pt_gene", "Two dimensional Map (Generated);Z_{h};P_{t}^{2} [GeV^{2}]",          50, DISLimits[0][2], DISLimits[1][2],  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Zh_PQ_gene = new TH2D("hist2D_Zh_PQ_gene", "Two dimensional Map (Generated);Z_{h};#phi_{PQ} [deg]",              50, DISLimits[0][2], DISLimits[1][2], 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Pt_PQ_gene = new TH2D("hist2D_Pt_PQ_gene", "Two dimensional Map (Generated);P_{t}^{2} [GeV^{2}];#phi_{PQ} [deg]",50, DISLimits[0][3], DISLimits[1][3], 180, DISLimits[0][4], DISLimits[1][4]);

    // Bin migration
    TH2D* histMigrationMatrixQ2 = new TH2D("histMigrationMatrixQ2", "Migration Q^{2};True Q^{2} [GeV^{2}]; Reco Q^{2} [GeV^{2}]"           , 50,DISLimits[0][0],DISLimits[1][0], 50,DISLimits[0][0],DISLimits[1][0]);
    TH2D* histMigrationMatrixNu = new TH2D("histMigrationMatrixNu", "Migration #nu;True Nu [GeV]; Reco Nu [GeV]"                           , 50,DISLimits[0][1],DISLimits[1][1], 50,DISLimits[0][1],DISLimits[1][1]);
    TH2D* histMigrationMatrixZh = new TH2D("histMigrationMatrixZh", "Migration Z_{h};True Z_{h}; Reco Z_{h}"                               , 50,DISLimits[0][2],DISLimits[1][2], 50,DISLimits[0][2],DISLimits[1][2]);
    TH2D* histMigrationMatrixPt = new TH2D("histMigrationMatrixPt", "Migration P_{T}^{2};True P_{T}^{2} [GeV^{2}];Reco P_{T}^{2} [GeV^{2}]", 50,DISLimits[0][3],DISLimits[1][3], 50,DISLimits[0][3],DISLimits[1][3]);
    TH2D* histMigrationMatrixPQ = new TH2D("histMigrationMatrixPQ", "Migration #phi_{PQ};True #phi_{PQ} [deg];Reco #phi_{PQ} [deg]"        ,180,DISLimits[0][4],DISLimits[1][4],180,DISLimits[0][4],DISLimits[1][4]);

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    unsigned int entries_to_process = nentries;
    int n_pions = 0, n_pions_match = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;

    for (unsigned int jentry = 0; jentry < entries_to_process; jentry++)
    {
        if (jentry % 1000000 == 0)
            printf("Processing entry %9u, progress at %6.2f%%\n",jentry,100.*(double)jentry/(entries_to_process));

        // std::cout << "Processing entry " << jentry << ", progress at " << 100.*(double) jentry / (entries_to_process) << "%" << std::endl;
        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        // if (Cut(ientry) < 0) continue;
        good_electron_mc = false, good_electron = false;

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
            hist2D_Q2_Nu_reco->Fill(Q2,Nu);
        }

        if (!_isData && GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
            hist2D_Q2_Nu_gene->Fill(mc_Q2,mc_Nu);
        }

        if (good_electron && good_electron_mc)
        {
            hist2D_Q2_Nu_mtch->Fill(Q2,Nu);

            histMigrationMatrixQ2->Fill(mc_Q2,Q2);
            histMigrationMatrixNu->Fill(mc_Nu,Nu);
        }

        int vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;
            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                n_pions++;
                good_pion = true;
                hist2D_Q2_Zh_reco->Fill(Q2, Zh->at(i));
                hist2D_Q2_Pt_reco->Fill(Q2, Pt2->at(i));
                hist2D_Q2_PQ_reco->Fill(Q2, PhiPQ->at(i));
                hist2D_Nu_Zh_reco->Fill(Nu, Zh->at(i));
                hist2D_Nu_Pt_reco->Fill(Nu, Pt2->at(i));
                hist2D_Nu_PQ_reco->Fill(Nu, PhiPQ->at(i));
                hist2D_Zh_Pt_reco->Fill(Zh->at(i), Pt2->at(i));
                hist2D_Zh_PQ_reco->Fill(Zh->at(i), PhiPQ->at(i));
                hist2D_Pt_PQ_reco->Fill(Pt2->at(i), PhiPQ->at(i));
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
                hist2D_Q2_Zh_gene->Fill(mc_Q2, mc_Zh->at(i));
                hist2D_Q2_Pt_gene->Fill(mc_Q2, mc_Pt2->at(i));
                hist2D_Q2_PQ_gene->Fill(mc_Q2, mc_PhiPQ->at(i));
                hist2D_Nu_Zh_gene->Fill(mc_Nu, mc_Zh->at(i));
                hist2D_Nu_Pt_gene->Fill(mc_Nu, mc_Pt2->at(i));
                hist2D_Nu_PQ_gene->Fill(mc_Nu, mc_PhiPQ->at(i));
                hist2D_Zh_Pt_gene->Fill(mc_Zh->at(i), mc_Pt2->at(i));
                hist2D_Zh_PQ_gene->Fill(mc_Zh->at(i), mc_PhiPQ->at(i));
                hist2D_Pt_PQ_gene->Fill(mc_Pt2->at(i), mc_PhiPQ->at(i));
            }

            if (good_pion && good_pion_mc)
            {
                n_pions_match++;
                hist2D_Q2_Zh_mtch->Fill(Q2, Zh->at(i));
                hist2D_Q2_Pt_mtch->Fill(Q2, Pt2->at(i));
                hist2D_Q2_PQ_mtch->Fill(Q2, PhiPQ->at(i));
                hist2D_Nu_Zh_mtch->Fill(Nu, Zh->at(i));
                hist2D_Nu_Pt_mtch->Fill(Nu, Pt2->at(i));
                hist2D_Nu_PQ_mtch->Fill(Nu, PhiPQ->at(i));
                hist2D_Zh_Pt_mtch->Fill(Zh->at(i), Pt2->at(i));
                hist2D_Zh_PQ_mtch->Fill(Zh->at(i), PhiPQ->at(i));
                hist2D_Pt_PQ_mtch->Fill(Pt2->at(i), PhiPQ->at(i));

                histMigrationMatrixZh->Fill(mc_Zh->at(i), Zh->at(i));
                histMigrationMatrixPt->Fill(mc_Pt2->at(i), Pt2->at(i));
                histMigrationMatrixPQ->Fill(mc_PhiPQ->at(i), PhiPQ->at(i));
            }
        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " final state Pions matching generated." << std::endl;

    if (_isData)
    {
        hist2D_Q2_Nu_gene->Delete();
        hist2D_Q2_Zh_gene->Delete();
        hist2D_Q2_Pt_gene->Delete();
        hist2D_Q2_PQ_gene->Delete();
        hist2D_Nu_Zh_gene->Delete();
        hist2D_Nu_Pt_gene->Delete();
        hist2D_Nu_PQ_gene->Delete();
        hist2D_Zh_Pt_gene->Delete();
        hist2D_Zh_PQ_gene->Delete();
        hist2D_Pt_PQ_gene->Delete();

        hist2D_Q2_Nu_mtch->Delete();
        hist2D_Q2_Zh_mtch->Delete();
        hist2D_Q2_Pt_mtch->Delete();
        hist2D_Q2_PQ_mtch->Delete();
        hist2D_Nu_Zh_mtch->Delete();
        hist2D_Nu_Pt_mtch->Delete();
        hist2D_Nu_PQ_mtch->Delete();
        hist2D_Zh_Pt_mtch->Delete();
        hist2D_Zh_PQ_mtch->Delete();
        hist2D_Pt_PQ_mtch->Delete();

        histMigrationMatrixQ2->Delete();
        histMigrationMatrixNu->Delete();
        histMigrationMatrixZh->Delete();
        histMigrationMatrixPt->Delete();
        histMigrationMatrixPQ->Delete();
    }

    fout->Write();
    fout->Close();
}

/*
void Acceptance::Correction()
{
    fChain->SetBranchStatus("*",0);
    std::vector<string> activeBranches = {"TargType", "mc_TargType", "Q2", "mc_Q2", "Nu", "mc_Nu", "Xb", "mc_Xb",
                                          "Yb", "mc_Yb", "W", "mc_W", "vyec", "Zh", "mc_Zh", "Pt2", "mc_Pt2",
                                          "PhiPQ", "mc_PhiPQ", "pid", "mc_pid", "Nphe"}; //, "Xf"};
    for (const auto &activeBranch : activeBranches)
    {
        fChain->SetBranchStatus(activeBranch.c_str(), 1);
    }

    TFile *fout;
    if (SaveAcceptance) fout = TFile::Open(Form("../output/Acceptance_%s.root", getNameTarget().c_str()), "RECREATE");
    else                fout = TFile::Open("../output/Acceptance_ClosureTest_tmp.root", "RECREATE");

    // Define binning
    // OR : Original: {3, 3, 5, 5, 12} = 2700
	// CP : PhiPQ central peak: {3, 3, 5, 5, 40} = 9000 // PhiPQ binning is really important due to the features seen!
	// Int_t nbins[5] = {3, 3, 5, 5, 40};
    double* minbins = &DISLimits[0][0];
    double* maxbins = &DISLimits[1][0];

    for (int i=0; i<nbins[4]+1; i++)
    {
        PhiPQ_binng.push_back(-180. + i*360./nbins[4]);
    }

    // Set variable width bins
	Double_t *Q2_Lmts  = &Q2_binng[0]; // {1.0, 1.3, 1.8, 4.1};
	Double_t *Nu_Lmts  = &Nu_binng[0]; // {2.2, 3.2, 3.7, 4.2};
	Double_t *Zh_Lmts  = &Zh_binng[0]; // {0.0, 0.15, 0.25, 0.4, 0.7, 1.0};
	Double_t *Pt2_Lmts = &Pt2_binng[0];// {0.0, 0.03, 0.06, 0.1, 0.18, 1.0};
    Double_t *PhiPQ_Lmts = &PhiPQ_binng[0];;

    // TH1::SetDefaultSumw2();

    //// Define Histograms
    // one-dimensional efficiency histogramss
    TEfficiency* effZh = new TEfficiency("effZh", "effZh;z_{h};Reconstruction Efficiency", 20, DISLimits[0][2], DISLimits[1][2]);
    TEfficiency* effPt2 = new TEfficiency("effPt2", "effPt2;p_{T}^{2} (GeV^{2});Reconstruction Efficiency", 20, DISLimits[0][3], DISLimits[1][3]);
    TEfficiency* effPhiPQ = new TEfficiency("effPhiPQ", "effPhiPQ;#phi_{PQ} (deg);Reconstruction Efficiency", 60, DISLimits[0][4], DISLimits[1][4]);

    // bin Migration
    TH2F* histMigrationMatrixZh = new TH2F("histMigrationMatrixZh", "MigrationZh;True z_{h}; Reco z_{h}", 50, DISLimits[0][2], DISLimits[1][2], 50, DISLimits[0][2], DISLimits[1][2]);
    TH2F* histMigrationMatrixPt2 = new TH2F("histMigrationMatrixPt2", "MigrationPt2;True p_{T}^{2} (GeV^{2});Reco p_{T}^{2} (GeV^{2})", 50, DISLimits[0][3], DISLimits[1][3], 50, DISLimits[0][3], DISLimits[1][3]);
    TH2F* histMigrationMatrixPhiPQ = new TH2F("histMigrationMatrixPhiPQ", "MigrationPhiPQ;True #phi_{PQ} (deg);Reco #phi_{PQ} (deg)", 120, DISLimits[0][4], DISLimits[1][4], 120, DISLimits[0][4], DISLimits[1][4]);

    // THnSparse
    THnSparse *histReco_mc = new THnSparseD("histReco_mc","Reconstructed with mc_vars", 5,nbins,minbins,maxbins);
    THnSparse *histReco_rec = new THnSparseD("histReco_rec","Reconstructed with reco_vars", 5,nbins,minbins,maxbins);
    THnSparse *histTrue = new THnSparseD("histTrue","True", 5,nbins,minbins,maxbins);
	// THnSparse *histAcce_mc  = new THnSparseD("histAcce_mc","Acceptance with mc_vars", 5,nbins,minbins,maxbins);
	// THnSparse *histAcce_rec  = new THnSparseD("histAcce_rec","Acceptance with reco_vars", 5,nbins,minbins,maxbins);

    SetVariableSize(histReco_mc, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    SetVariableSize(histReco_rec, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    SetVariableSize(histTrue, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    // SetVariableSize(histAcce_mc,  nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    // SetVariableSize(histAcce_rec,  nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);

	histReco_mc->Sumw2();
	histReco_rec->Sumw2();
	histTrue->Sumw2();
	// histAcce_mc->Sumw2();
	// histAcce_rec->Sumw2();

    // std::cout << "Setting up unfolding objects done" << std::endl;

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    // for (Long64_t jentry = 0; jentry < nentries; jentry++) {
    unsigned int entries_to_process;
    if (SaveAcceptance) entries_to_process = nentries;
    else                entries_to_process = nentries/2;
    int global_bin;
    int vec_entries=0, vec_entries_MC=0;

    std::map<std::string, unsigned int> general_counter = {{"Total mc_El entries",0}, {"Total mc_Pi entries",0}};
    // std::map<std::string, unsigned int> general_counter = {{"Good MC_El",0}, {"Good MC_Pi",0}, {"Good Reco El",0}, {"Good Reco Pi",0}};
    // std::map<std::string, unsigned int> general_reco_counter = {{"Good Reco El",0}, {"Good Reco Pi",0}};
    std::map<std::string, unsigned int> mc_El_Bad_counter = {{"Wrong mc_TargType",0}, {"Out of DIS range",0}};
    std::map<std::string, unsigned int> mc_Pi_Bad_counter = {{"Wrong mc_pid",0}, {"Out of DIS range",0}};
    // std::map<std::string, unsigned int> mc_El_Good_counter = {{"Good mc_Electron",0}};
    // std::map<std::string, unsigned int> mc_Pi_Good_counter = {{"Leading mc_Pion",0}, {"No Leading mc_Pion",0}};
    std::map<std::string, unsigned int> rec_El_Bad_counter = {{"Wrong TargType",0}, {"Out of DIS range",0}, {"Out of VertexY Correction",0},
                                                              {"Different vector size",0}};
    std::map<std::string, unsigned int> rec_Pi_Bad_counter = {{"Bad Reconstructed Pion",0}};
    std::map<std::string, unsigned int> rec_El_Good_counter = {{"Good Reco Electron",0}};
    std::map<std::string, unsigned int> rec_Pi_Good_counter = {{"Good Reco Pi",0}}; // ,{"Leading Pion",0}, {"No Leading Pion",0}};
    std::vector<double> kinematical_vars, mc_kinematical_vars;
    for (unsigned int jentry = 0; jentry < entries_to_process; jentry++)
    {
        if (jentry % 1000000 == 0)
            printf("Processing entry %9u, progress at %6.2f%%\n",jentry,100.*(double)jentry/(entries_to_process));

        // std::cout << "Processing entry " << jentry << ", progress at " << 100.*(double) jentry / (entries_to_process) << "%" << std::endl;
        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        // if (Cut(ientry) < 0) continue;
        if (!GoodElectron_MC(ientry, DISLimits))
        {
            if (mc_TargType!=_targTypeCut) mc_El_Bad_counter["Wrong mc_TargType"]++;
            if (mc_Q2<DISLimits[0][0] || DISLimits[1][0]<mc_Q2 || 0.85<mc_Yb || mc_W<2 || mc_Nu<DISLimits[0][1] || DISLimits[1][1]<mc_Nu) mc_El_Bad_counter["Out of DIS range"]++;
            continue;
        }
        else general_counter["Total mc_El entries"]++;

        if (!GoodElectron(ientry, DISLimits))
        {
            if (TargType!=_targTypeCut) rec_El_Bad_counter["Wrong TargType"]++;
            if (Q2<DISLimits[0][0] || DISLimits[1][0]<Q2 || 0.85<Yb || W<2 || Nu<DISLimits[0][1] || DISLimits[1][1]<Nu) rec_El_Bad_counter["Out of DIS range"]++;
            if (vyec<-1.4 || 1.4<vyec) rec_El_Bad_counter["Out of VertexY Correction"]++;
        }
        else rec_El_Good_counter["Good Reco Electron"]++;

        kinematical_vars = {Q2, Nu};
        global_bin = GlobalVarPosition(&kinematical_vars, &leptonic_limits);

        vec_entries = PhiPQ->size();
        vec_entries_MC = mc_PhiPQ->size();
        if (vec_entries!=vec_entries_MC) rec_El_Bad_counter["Different vector size"]++;

		for (int i=0; i<vec_entries; i++)
        {
            if (!GoodPiPlus_MC(ientry, i, DISLimits))
            {
                if (mc_pid->at(i)!=211) mc_Pi_Bad_counter["Wrong mc_pid"]++;
                if (mc_Zh->at(i)<DISLimits[0][2] || DISLimits[1][2]<mc_Zh->at(i) || mc_Pt2->at(i)<DISLimits[0][3] || DISLimits[1][3]<mc_Pt2->at(i) ||
                    mc_PhiPQ->at(i)<DISLimits[0][4] || DISLimits[1][4]<mc_PhiPQ->at(i)) mc_Pi_Bad_counter["Out of DIS range"]++;
                continue;
            }
            else general_counter["Total mc_Pi entries"]++;

            double mc_bin[] = {mc_Q2, mc_Nu, mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i)};
            histTrue->Fill(mc_bin);
            bool passed(false);
            if (GoodPiPlus(ientry, i, DISLimits))
            {
                passed = true;
                histMigrationMatrixZh->Fill(mc_Zh->at(i), Zh->at(i));
                histMigrationMatrixPt2->Fill(mc_Pt2->at(i), Pt2->at(i));
                histMigrationMatrixPhiPQ->Fill(mc_PhiPQ->at(i), PhiPQ->at(i));

                histReco_mc->Fill(mc_bin);

                double rec_bin[] = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};
                histReco_rec->Fill(rec_bin);

                rec_Pi_Good_counter["Good Reco Pi"]++;
            }
            else
            {
                rec_Pi_Bad_counter["Bad Reconstructed Pion"]++;
            }

            effZh->Fill(passed ,mc_Zh->at(i));
            effPt2->Fill(passed ,mc_Pt2->at(i));
            effPhiPQ->Fill(passed ,mc_PhiPQ->at(i));
        }   // loop over tracks
    }       // loop over entries

    // Acceptance
    THnSparse *histAcce_mc = (THnSparse*)histReco_mc->Clone("histAcce_mc");
    histAcce_mc->Divide(histTrue);
    THnSparse *histAcce_rec = (THnSparse*)histReco_rec->Clone("histAcce_rec");
    histAcce_rec->Divide(histTrue);

    // Summary tables
    PrintSummaryTable(general_counter, "Good Particles Summary");
    // PrintSummaryTable(general_reco_counter, "Pass GoodParticle cut");
    PrintSummaryTable(mc_El_Bad_counter, "Doesn't pass MC Electron cuts", entries_to_process);
    PrintSummaryTable(mc_Pi_Bad_counter, "Doesn't pass MC Pion cuts");
    PrintSummaryTable(rec_El_Bad_counter, "Doesn't pass GoodElectron cut", general_counter["Total mc_El entries"]);
    PrintSummaryTable(rec_Pi_Bad_counter, "Doesn't pass GoodPion cut");
    PrintSummaryTable(rec_El_Good_counter, "Pass GoodElectron cut", general_counter["Total mc_El entries"]);
    PrintSummaryTable(rec_Pi_Good_counter, "Pass GoodPion cut", general_counter["Total mc_Pi entries"]);

    histReco_mc->Write();
    histReco_rec->Write();
    histTrue->Write();
    histAcce_mc->Write();
    histAcce_rec->Write();

    fout->Write();
    fout->Close();
}
*/

/*
void Acceptance::ClosureTest() // From Jorge
{
    TFile *facc = TFile::Open("test_acceptance.root", "READ");

    TEfficiency *effZh = (TEfficiency *)facc->Get("effZh");
    TEfficiency *effPt2 = (TEfficiency *)facc->Get("effPt2");
    TEfficiency *effPhiPQ = (TEfficiency *)facc->Get("effPhiPQ");
    TH2F *accZhPt2 = (TH2F *)facc->Get("accZhPt2");
    TH3F *accZhPt2PhiPQ = (TH3F *)facc->Get("accZhPt2PhiPQ");

    std::vector<string> activeBranches = {"TargType", "mc_TargType", "Q2", "mc_Q2", "Nu", "mc_Nu", "Xb", "mc_Xb",
                                          "Yb", "mc_Yb", "W", "mc_W", "vyec", "Zh", "mc_Zh", "Pt2", "mc_Pt2",
                                          "PhiPQ", "mc_PhiPQ", "pid", "mc_pid", "Nphe"};
    for (const auto &activeBranch : activeBranches)
    {
        fChain->SetBranchStatus(activeBranch.c_str(), 1);
    }

    TFile *fout = TFile::Open("test_acceptance_closure.root", "RECREATE");

    TH1F *histWeightsZh = new TH1F("histWeightsZh", "histWeightsZh;Weight;Counts", 100, 0, 1);
    TH1F *histWeightsPhiPQ = new TH1F("histWeightsPhiPQ", "histWeightsPhiPQ;Weight;Counts", 100, 0, 1);

    TH1F *histZh[3];
    histZh[0] = new TH1F("histZh_1d_eff_map", "histZh_1d_eff_map;z_{h};Events", 10, 0, 1);
    histZh[1] = new TH1F("histZh_2d_map", "histZh_2d_map;z_{h};Events", 10, 0, 1);
    histZh[2] = new TH1F("histZh_3d_map", "histZh_3d_map;z_{h};Events", 10, 0, 1);
    TH1F *histRecoZh = new TH1F("histRecoZh", "histRecoZh;Reco z_{h};Events", 10, 0, 1);
    TH1F *histTrueZh = new TH1F("histTrueZh", "histTrueZh;True z_{h};Events", 10, 0, 1);

    TH1F *histPt2[3];
    histPt2[0] = new TH1F("histPt2_1d_eff_map", "histZh_1d_eff_map;p_{T}^{2} (GeV^{2});Events", 10, 0, 1.2);
    histPt2[1] = new TH1F("histPt2_2d_map", "histZh_2d_map;p_{T}^{2} (GeV^{2});Events", 10, 0, 1.2);
    histPt2[2] = new TH1F("histPt2_3d_map", "histZh_3d_map;p_{T}^{2} (GeV^{2});Events", 10, 0, 1.2);
    TH1F *histRecoPt2 = new TH1F("histRecoPt2", "histRecoPt2;Reco p_{T}^{2} (GeV^{2});Events", 10, 0, 1.2);
    TH1F *histTruePt2 = new TH1F("histTruePt2", "histRecoPt2;True p_{T}^{2} (GeV^{2});Events", 10, 0, 1.2);

    TH1F *histPhiPQ[2];
    histPhiPQ[0] = new TH1F("histPhiPQ_1d_eff_map", "histZh;#phi_{PQ} (deg);Events", 11, -180, 180);
    histPhiPQ[1] = new TH1F("histPhiPQ_3d_map", "histZh;#phi_{PQ} (deg);Events", 11, -180, 180);
    TH1F *histRecoPhiPQ = new TH1F("histRecoPhiPQ", "histRecoZh;Reco #phi_{PQ} (deg);Events", 11, -180, 180);
    TH1F *histTruePhiPQ = new TH1F("histTruePhiPQ", "histTrueZh;True #phi_{PQ} (deg);Events", 11, -180, 180);

    TH2F *histRecoZhPhiPQ = new TH2F("histRecoZhPhiPQ", "histRecoZhPhiPQ;Reco z_{h};Reco #phi_{PQ} (deg)", 10, 0, 1, 11, -180, 180);
    TH2F *histTrueZhPhiPQ = new TH2F("histTrueZhPhiPQ", "histTrueZhPhiPQ;True z_{h};True #phi_{PQ} (deg)", 10, 0, 1, 11, -180, 180);

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    for (Long64_t jentry = nentries / 2 + 1; jentry < nentries; jentry++)
    {
        // for (Long64_t jentry = 0; jentry < nentries / 2; jentry++) {
        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        // if (Cut(ientry) < 0) continue;
        if (TargType != _targTypeCut)
            continue;

        size_t bin;
        float acc_value, weight;

        if (Q2 > 1.0)
        {
            for (size_t i = 0; i < Zh->size(); i++)
            {
                if (pid->at(i) != 211)
                    continue;

                histRecoZh->Fill(Zh->at(i));
                histRecoPt2->Fill(Pt2->at(i));
                histRecoPhiPQ->Fill(PhiPQ->at(i));

                histRecoZhPhiPQ->Fill(Zh->at(i), PhiPQ->at(i));
                histTrueZhPhiPQ->Fill(Zh->at(i), PhiPQ->at(i));

                // effs maps
                bin = effZh->FindFixBin(Zh->at(i));
                acc_value = effZh->GetEfficiency(bin);
                if (acc_value > 0)
                {
                    weight = 1.0 / acc_value;
                    histZh[0]->Fill(Zh->at(i), weight);
                }

                bin = effPt2->FindFixBin(Pt2->at(i));
                acc_value = effPt2->GetEfficiency(bin);
                if (acc_value > 0)
                {
                    weight = 1.0 / acc_value;
                    histPt2[0]->Fill(Pt2->at(i), weight);
                }

                bin = effPhiPQ->FindFixBin(PhiPQ->at(i));
                acc_value = effPhiPQ->GetEfficiency(bin);
                if (acc_value > 0)
                {
                    weight = 1.0 / acc_value;
                    histPhiPQ[0]->Fill(PhiPQ->at(i), weight);
                }

                // ZhPt2 map
                bin = accZhPt2->FindBin(Zh->at(i), Pt2->at(i));
                acc_value = accZhPt2->GetBinContent(bin);
                if (acc_value > 0)
                {
                    weight = 1.0 / acc_value;
                    histZh[1]->Fill(Zh->at(i), weight);
                    histPt2[1]->Fill(Pt2->at(i), weight);
                }

                // 3d map
                bin = accZhPt2PhiPQ->FindBin(Zh->at(i), Pt2->at(i), PhiPQ->at(i));
                acc_value = accZhPt2PhiPQ->GetBinContent(bin);
                if (acc_value > 0)
                {
                    weight = 1.0 / acc_value;
                    histZh[2]->Fill(Zh->at(i), weight);
                    histPt2[2]->Fill(Pt2->at(i), weight);
                    histPhiPQ[1]->Fill(PhiPQ->at(i), weight);
                }

            } // end of loop over tracks
        }

        if (mc_Q2 > 1.0)
        {
            for (size_t i = 0; i < mc_Zh->size(); i++)
            {
                if (mc_pid->at(i) != 211)
                    continue;
                histTrueZh->Fill(mc_Zh->at(i));
                histTruePt2->Fill(mc_Pt2->at(i));
                histTruePhiPQ->Fill(mc_PhiPQ->at(i));
            } // end of loop over tracks
        }
    }

    TH1F *histClosureZh[3];
    TH1F *histClosurePt2[3];
    TH1F *histClosurePhiPQ[2];
    histClosureZh[0] = (TH1F *)histZh[0]->Clone("histClosureZh_1d_eff_map");
    histClosureZh[1] = (TH1F *)histZh[1]->Clone("histClosureZh_2d_map");
    histClosureZh[2] = (TH1F *)histZh[2]->Clone("histClosureZh_3d_map");
    histClosurePt2[0] = (TH1F *)histPt2[0]->Clone("histClosurePt2_1d_eff_map");
    histClosurePt2[1] = (TH1F *)histPt2[1]->Clone("histClosurePt2_2d_map");
    histClosurePt2[2] = (TH1F *)histPt2[2]->Clone("histClosurePt2_3d_map");
    histClosurePhiPQ[0] = (TH1F *)histPhiPQ[0]->Clone("histClosurePhiPQ_1d_eff_map");
    histClosurePhiPQ[1] = (TH1F *)histPhiPQ[1]->Clone("histClosurePhiPQ_3d_map");

    histClosureZh[0]->Divide(histTrueZh);
    histClosureZh[1]->Divide(histTrueZh);
    histClosureZh[2]->Divide(histTrueZh);
    histClosurePt2[0]->Divide(histTruePt2);
    histClosurePt2[1]->Divide(histTruePt2);
    histClosurePt2[2]->Divide(histTruePt2);
    histClosurePhiPQ[0]->Divide(histTruePhiPQ);
    histClosurePhiPQ[1]->Divide(histTruePhiPQ);

    histClosureZh[0]->SetTitle("histClosureZh_1d_eff_map;z_{h};Closure");
    histClosureZh[1]->SetTitle("histClosureZh_2d_map;z_{h};Closure");
    histClosureZh[2]->SetTitle("histClosureZh_3d_map;z_{h};Closure");
    histClosurePt2[0]->SetTitle("histClosurePt2_1d_eff_map;p_{T}^{2} (GeV^{2});Closure");
    histClosurePt2[1]->SetTitle("histClosurePt2_2d_map;p_{T}^{2} (GeV^{2});Closure");
    histClosurePt2[2]->SetTitle("histClosurePt2_3d_map;p_{T}^{2} (GeV^{2});Closure");
    histClosurePhiPQ[0]->SetTitle("histClosurePhiPQ_1d_eff_map;#phi_{PQ} (deg);Closure");
    histClosurePhiPQ[1]->SetTitle("histClosurePhiPQ_3d_map;#phi_{PQ} (deg);Closure");

    histClosureZh[0]->SetMinimum(0.81);
    histClosureZh[0]->SetMaximum(1.19);
    histClosureZh[1]->SetMinimum(0.81);
    histClosureZh[1]->SetMaximum(1.19);
    histClosureZh[2]->SetMinimum(0.81);
    histClosureZh[2]->SetMaximum(1.19);
    histClosurePt2[0]->SetMinimum(0.81);
    histClosurePt2[0]->SetMaximum(1.19);
    histClosurePt2[1]->SetMinimum(0.81);
    histClosurePt2[1]->SetMaximum(1.19);
    histClosurePt2[2]->SetMinimum(0.81);
    histClosurePt2[2]->SetMaximum(1.19);
    histClosurePhiPQ[0]->SetMinimum(0.81);
    histClosurePhiPQ[0]->SetMaximum(1.19);
    histClosurePhiPQ[1]->SetMinimum(0.81);
    histClosurePhiPQ[1]->SetMaximum(1.19);

    TCanvas *c1 = new TCanvas("c1", "closure test", 1400, 1400);
    c1->Divide(3, 3);
    for (size_t i = 0; i < 3; i++)
    {
        c1->cd(i + 1);
        histClosureZh[i]->Draw();
    }
    for (size_t i = 0; i < 3; i++)
    {
        c1->cd(i + 4);
        histClosurePt2[i]->Draw();
    }
    c1->cd(7);
    histClosurePhiPQ[0]->Draw();
    c1->cd(8);
    histClosurePhiPQ[1]->Draw();

    c1->Write();

    auto responseZh = (RooUnfoldResponse *)facc->Get("responseZh");
    RooUnfoldBayes unfoldBayesZh(responseZh, histRecoZh, 4);
    TH1F *histUnfoldedZh = (TH1F *)unfoldBayesZh.Hreco();
    histUnfoldedZh->SetName("histUnfoldedZh");
    TH1F *histClosureUnfoldedZh = (TH1F *)histUnfoldedZh->Clone("histClosureUnfoldedZh");
    histClosureUnfoldedZh->Divide(histTrueZh);

    auto responsePt2 = (RooUnfoldResponse *)facc->Get("responsePt2");
    RooUnfoldBayes unfoldBayesPt2(responsePt2, histRecoPt2, 4);
    TH1F *histUnfoldedPt2 = (TH1F *)unfoldBayesPt2.Hreco();
    histUnfoldedPt2->SetName("histUnfoldedPt2");
    TH1F *histClosureUnfoldedPt2 = (TH1F *)histUnfoldedZh->Clone("histClosureUnfoldedPt2");
    histClosureUnfoldedZh->Divide(histTruePt2);

    auto responsePhiPQ = (RooUnfoldResponse *)facc->Get("responsePhiPQ");
    RooUnfoldBayes unfoldBayesPhiPQ(responsePhiPQ, histRecoPhiPQ, 4);
    TH1F *histUnfoldedPhiPQ = (TH1F *)unfoldBayesPhiPQ.Hreco();
    histUnfoldedPhiPQ->SetName("histUnfoldedPhiPQ");
    TH1F *histClosureUnfoldedPhiPQ = (TH1F *)histUnfoldedPhiPQ->Clone("histClosureUnfoldedPhiPQ");
    histClosureUnfoldedZh->Divide(histTruePhiPQ);

    // auto response2D = (RooUnfoldResponse*)facc->Get("response2D");
    // RooUnfoldBayes unfoldBayesZhPhiPQ(responsePhiPQ, histRecoZhPhiPQ, 4);
    // TH2F* histUnfoldedZhPhiPQ = (TH2F*)unfoldBayesZhPhiPQ.Hreco();
    // histUnfoldedZhPhiPQ->SetName("histUnfoldedZhPhiPQ");
    // TH2F* histClosureUnfoldedZhPhiPQ = (TH2F*)histUnfoldedZhPhiPQ->Clone("histClosureUnfoldedZhPhiPQ");
    // histClosureUnfoldedZhPhiPQ->Divide(histTrueZhPhiPQ);

    fout->Write();
    fout->Close();
}
*/


void Acceptance::ClosureTest()
{
    // Run over half of the sim and save in "../output/Acceptance_ClosureTest.root"
    Loop(false);
    using namespace DIS_original;


    // Begin Closure Test
    std::cout << "\n\nBeginning Closure Test calculations\n" << std::endl;

    TFile *facc = TFile::Open("../output/Acc_ClosureTest.root", "READ");
    TFile *fout = TFile::Open(Form("../output/ClosureTest_%s.root", getNameTarget().c_str()), "RECREATE");

    THnSparse *histAcc_Reconstructed  = (THnSparse*)facc->Get("histAcc_Reconstructed");
    THnSparse *histAcc_RecGoodGen_mc  = (THnSparse*)facc->Get("histAcc_RecGoodGen_mc");
    THnSparse *histAcc_RecGoodGen_rec = (THnSparse*)facc->Get("histAcc_RecGoodGen_rec");

    std::vector<TH3D*> histCorr_Reconstructed  = CreateQ2NuHistList<TH3D>(Q2_binng.size()-1, Nu_binng.size()-1, "Corr_Reconstructed", 10, DISLimits[0][2], DISLimits[1][2],
                                                        10, DISLimits[0][3], DISLimits[1][3], 40, DISLimits[0][4], DISLimits[1][4]);
    std::vector<TH3D*> histCorr_RecGoodGen_mc  = CreateQ2NuHistList<TH3D>(Q2_binng.size()-1, Nu_binng.size()-1, "Corr_RecGoodGen_mc", 10, DISLimits[0][2], DISLimits[1][2],
                                                        10, DISLimits[0][3], DISLimits[1][3], 40, DISLimits[0][4], DISLimits[1][4]);
    std::vector<TH3D*> histCorr_RecGoodGen_rec = CreateQ2NuHistList<TH3D>(Q2_binng.size()-1, Nu_binng.size()-1, "Corr_RecGoodGen_rec", 10, DISLimits[0][2], DISLimits[1][2],
                                                        10, DISLimits[0][3], DISLimits[1][3], 40, DISLimits[0][4], DISLimits[1][4]);
    // True has always good thrown pions. True_GivenReco is filled only when the Reco particle associated is well detected.
    std::vector<TH3D*> histTrue = CreateQ2NuHistList<TH3D>(Q2_binng.size()-1, Nu_binng.size()-1, "True", 10, DISLimits[0][2], DISLimits[1][2],
                                                        10, DISLimits[0][3], DISLimits[1][3], 40, DISLimits[0][4], DISLimits[1][4]);
    std::vector<TH3D*> histTrue_PionReco = CreateQ2NuHistList<TH3D>(Q2_binng.size()-1, Nu_binng.size()-1, "True_PionReco", 10, DISLimits[0][2], DISLimits[1][2],
                                                        10, DISLimits[0][3], DISLimits[1][3], 40, DISLimits[0][4], DISLimits[1][4]);

    Long64_t nentries = fChain->GetEntries();
    unsigned int entries_to_process = nentries/2;

    Long64_t nbytes = 0, nb = 0;
    
    int global_bin=-1, global_bin_True=-1;
    int vec_entries=0, count = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;
    std::vector<double> leptonic_vars, leptonic_vars_True;
    for (unsigned int jentry = entries_to_process; jentry < nentries; jentry++)
    {
        count++;
        if ((jentry-entries_to_process) % 1000000 == 0)
            printf("Processing entry %9u, progress at %6.2f%%\n",jentry-entries_to_process,100.*(double)(jentry-entries_to_process)/(nentries-entries_to_process));

        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        good_electron_mc = false, good_electron = false;

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
            leptonic_vars = {Q2, Nu};
            global_bin = GlobalVarPosition(&leptonic_vars, &leptonic_limits);
        }

        if (GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
            leptonic_vars_True = {mc_Q2, mc_Nu};
            global_bin_True = GlobalVarPosition(&leptonic_vars_True, &leptonic_limits);
        }

        if (!good_electron && !good_electron_mc) continue;
        
        vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;

            if (good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
            }

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                good_pion = true;
            }

            if (!good_pion_mc && !good_pion) continue;

            if (good_pion_mc)
            {
                histTrue[global_bin_True]->Fill(mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i));
            }

            if (good_pion)
            {
                double find_this_bin[] = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};

                int bin_Reconstructed  = histAcc_Reconstructed->GetBin(find_this_bin);
                int bin_RecGoodGen_mc  = histAcc_RecGoodGen_mc->GetBin(find_this_bin);
                int bin_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBin(find_this_bin);

                double value_Reconstructed  = histAcc_Reconstructed->GetBinContent(bin_Reconstructed);
                double value_RecGoodGen_mc  = histAcc_RecGoodGen_mc->GetBinContent(bin_RecGoodGen_mc);
                double value_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBinContent(bin_RecGoodGen_rec);

                if (value_Reconstructed  != 0) histCorr_Reconstructed[global_bin]->Fill(Zh->at(i), Pt2->at(i), PhiPQ->at(i), 1./value_Reconstructed);
                if (value_RecGoodGen_mc  != 0) histCorr_RecGoodGen_mc[global_bin]->Fill(Zh->at(i), Pt2->at(i), PhiPQ->at(i), 1./value_RecGoodGen_mc);
                if (value_RecGoodGen_rec != 0) histCorr_RecGoodGen_rec[global_bin]->Fill(Zh->at(i),Pt2->at(i), PhiPQ->at(i), 1./value_RecGoodGen_rec);
            }

            if (good_pion_mc && good_pion)
            {
                histTrue_PionReco[global_bin_True]->Fill(mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i));
            }

        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << count << " entries!" << std::endl;

    TH1D *histCT_tmp;
    std::string var_name[] = {"Zh", "Pt2", "PhiPQ"}; 
    std::string axis_title[] = {"Zh", "P_{t}^{2} [GeV]", "#phi_{PQ} [deg]"};
    std::string axis_proj[] = {"x","y","z"};
    for (unsigned int iQ2=0; iQ2<(Q2_binng.size()-1); iQ2++)
    {
		for (unsigned int iNu=0; iNu<(Nu_binng.size()-1); iNu++)
        {
			std::string bin_title = Form("%.1f<Q2<%.1f, %.1f<Nu<%.1f",Q2_binng[iQ2],Q2_binng[iQ2+1],Nu_binng[iNu],Nu_binng[iNu+1]);
			int ibin = iNu+iQ2*(Nu_binng.size()-1);

			for (int ivar=0; ivar<3; ivar++)
            {
                // histCorr_Reconstructed[global_bin]
                // histCorr_RecGoodGen_mc[global_bin]
                // histCorr_RecGoodGen_rec[global_bin]
                // histTrue[global_bin_True]
                // histTrue_PionReco[global_bin_True]

                // Corrected with Only Reco Acc / True (RO-T)
                histCT_tmp = (TH1D*) histCorr_Reconstructed[ibin]->Project3D(axis_proj[ivar].c_str());
                histCT_tmp->SetName(Form("histCT_RO-T_Q%iN%i",iQ2,iNu));
                histCT_tmp->Divide(histTrue[ibin]->Project3D(axis_proj[ivar].c_str()));
                histCT_tmp->SetTitle(Form("Closure Test: Corrected with Only Reco Acc / True, %s;%s;Corr_AccReco/True",bin_title.c_str(),axis_title[ivar].c_str()));

                // Corrected with MC vars when Reco matches Gen Acc / True (MC-T)
                histCT_tmp = (TH1D*) histCorr_RecGoodGen_mc[ibin]->Project3D(axis_proj[ivar].c_str());
                histCT_tmp->SetName(Form("histCT_MC-T_Q%iN%i",iQ2,iNu));
                histCT_tmp->Divide(histTrue[ibin]->Project3D(axis_proj[ivar].c_str()));
                histCT_tmp->SetTitle(Form("Closure Test: Corrected with MC_vars Reco when GoodGen Acc / True, %s;%s;Corr_AccMCGoodG/True",bin_title.c_str(),axis_title[ivar].c_str()));

                // Corrected with Reco vars when Reco matches Gen Acc / True (RR-T)
                histCT_tmp = (TH1D*) histCorr_RecGoodGen_rec[ibin]->Project3D(axis_proj[ivar].c_str());
                histCT_tmp->SetName(Form("histCT_RR-T_Q%iN%i",iQ2,iNu));
                histCT_tmp->Divide(histTrue[ibin]->Project3D(axis_proj[ivar].c_str()));
                histCT_tmp->SetTitle(Form("Closure Test: Corrected with Rec_vars Reco when GoodGen Acc / True, %s;%s;Corr_AccRRGoodG/True",bin_title.c_str(),axis_title[ivar].c_str()));
			}
		}
	}

    fout->Write();
    fout->Close();
    facc->Close();
}

/*
void Acceptance::ClosureTestMultiDimensional()
{
    // Run over half of the sim and save in "../output/Acceptance_ClosureTest.root"
    Loop(false);

    // Begin Closure Test
    std::cout << "\n\nBeginning Closure Test calculations\n" << std::endl;

    TFile *facc = TFile::Open("../output/Acc_ClosureTest.root", "READ");
    TFile *fout = TFile::Open(Form("../output/ClosureTestMD_%s.root", getNameTarget().c_str()), "RECREATE");

    double* minbins = &DISLimits[0][0];
    double* maxbins = &DISLimits[1][0];

    // Set variable width bins
	Double_t *Q2_Lmts  = &Q2_binng[0]; // {1.0, 1.3, 1.8, 4.1};
	Double_t *Nu_Lmts  = &Nu_binng[0]; // {2.2, 3.2, 3.7, 4.2};
	Double_t *Zh_Lmts  = &Zh_binng[0]; // {0.0, 0.15, 0.25, 0.4, 0.7, 0.9, 1.0};
	Double_t *Pt2_Lmts = &Pt2_binng[0];// {0.0, 0.03, 0.06, 0.1, 0.18, 1.0};
    Double_t *PhiPQ_Lmts = &PhiPQ_binng[0];

    THnSparse *histAcc_Reconstructed  = (THnSparse*)facc->Get("histAcc_Reconstructed");
    THnSparse *histAcc_RecGoodGen_mc  = (THnSparse*)facc->Get("histAcc_RecGoodGen_mc");
    THnSparse *histAcc_RecGoodGen_rec = (THnSparse*)facc->Get("histAcc_RecGoodGen_rec");

    THnSparse *histCorr_Reconstructed  = new THnSparseD("histCorr_Reconstructed","Corr_Reconstructed"  , 5,nbins,minbins,maxbins);
    THnSparse *histCorr_RecGoodGen_mc  = new THnSparseD("histCorr_RecGoodGen_mc","Corr_RecGoodGen_mc"  , 5,nbins,minbins,maxbins);
    THnSparse *histCorr_RecGoodGen_rec = new THnSparseD("histCorr_RecGoodGen_rec","Corr_RecGoodGen_rec", 5,nbins,minbins,maxbins);
    // True has always good thrown pions. True_GivenReco is filled only when the Reco particle associated is well detected.
    THnSparse *histTrue                = new THnSparseD("histTrue","True"                              , 5,nbins,minbins,maxbins);
    THnSparse *histTrue_PionReco       = new THnSparseD("histTrue_PionReco","True_PionReco"            , 5,nbins,minbins,maxbins);
    
    SetVariableSize(histCorr_Reconstructed , nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    SetVariableSize(histCorr_RecGoodGen_mc , nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    SetVariableSize(histCorr_RecGoodGen_rec, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    SetVariableSize(histTrue               , nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);
    SetVariableSize(histTrue_PionReco      , nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);

    histCorr_Reconstructed->Sumw2();
    histCorr_RecGoodGen_mc->Sumw2();
    histCorr_RecGoodGen_rec->Sumw2();
    histTrue->Sumw2();
    histTrue_PionReco->Sumw2();

    // histCorr_Reconstructed
    // histCorr_RecGoodGen_mc
    // histCorr_RecGoodGen_rec
    // histTrue
    // histTrue_PionReco

    Long64_t nentries = fChain->GetEntries();
    unsigned int entries_to_process = nentries/2;

    Long64_t nbytes = 0, nb = 0;
    
    int global_bin=-1, global_bin_True=-1;
    int vec_entries=0, count = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;
    std::vector<double> leptonic_vars, leptonic_vars_True;
    for (unsigned int jentry = entries_to_process; jentry < nentries; jentry++)
    {
        count++;
        if ((jentry-entries_to_process) % 1000000 == 0)
            printf("Processing entry %9u, progress at %6.2f%%\n",jentry-entries_to_process,100.*(double)(jentry-entries_to_process)/(nentries-entries_to_process));

        Long64_t ientry = LoadTree(jentry); // FINISH THE IMPLEMENTATION OF THIS MULTI DIMENSIONAL CLOSURE TEST!!!
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        good_electron_mc = false, good_electron = false;

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
            leptonic_vars = {Q2, Nu};
            global_bin = GlobalVarPosition(&leptonic_vars, &leptonic_limits);
        }

        if (GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
            leptonic_vars_True = {mc_Q2, mc_Nu};
            global_bin_True = GlobalVarPosition(&leptonic_vars_True, &leptonic_limits);
        }

        if (!good_electron && !good_electron_mc) continue;
        
        vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;

            if (good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
            }

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                good_pion = true;
            }

            if (!good_pion_mc && !good_pion) continue;

            if (good_pion_mc)
            {
                histTrue[global_bin_True]->Fill(mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i));
            }

            if (good_pion)
            {
                double find_this_bin[] = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};

                int bin_Reconstructed  = histAcc_Reconstructed->GetBin(find_this_bin);
                int bin_RecGoodGen_mc  = histAcc_RecGoodGen_mc->GetBin(find_this_bin);
                int bin_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBin(find_this_bin);

                double value_Reconstructed  = histAcc_Reconstructed->GetBinContent(bin_Reconstructed);
                double value_RecGoodGen_mc  = histAcc_RecGoodGen_mc->GetBinContent(bin_RecGoodGen_mc);
                double value_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBinContent(bin_RecGoodGen_rec);

                if (value_Reconstructed  != 0) histCorr_Reconstructed[global_bin]->Fill(Zh->at(i), Pt2->at(i), PhiPQ->at(i), 1./value_Reconstructed);
                if (value_RecGoodGen_mc  != 0) histCorr_RecGoodGen_mc[global_bin]->Fill(Zh->at(i), Pt2->at(i), PhiPQ->at(i), 1./value_RecGoodGen_mc);
                if (value_RecGoodGen_rec != 0) histCorr_RecGoodGen_rec[global_bin]->Fill(Zh->at(i),Pt2->at(i), PhiPQ->at(i), 1./value_RecGoodGen_rec);
            }

            if (good_pion_mc && good_pion)
            {
                histTrue_PionReco[global_bin_True]->Fill(mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i));
            }

        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << count << " entries!" << std::endl;

    TH1D *histCT_tmp;
    std::string var_name[] = {"Zh", "Pt2", "PhiPQ"}; 
    std::string axis_title[] = {"Zh", "P_{t}^{2} [GeV]", "#phi_{PQ} [deg]"};
    std::string axis_proj[] = {"x","y","z"};
    for (unsigned int iQ2=0; iQ2<(Q2_binng.size()-1); iQ2++)
    {
		for (unsigned int iNu=0; iNu<(Nu_binng.size()-1); iNu++)
        {
			std::string bin_title = Form("%.1f<Q2<%.1f, %.1f<Nu<%.1f",Q2_binng[iQ2],Q2_binng[iQ2+1],Nu_binng[iNu],Nu_binng[iNu+1]);
			int ibin = iNu+iQ2*(Nu_binng.size()-1);

			for (int ivar=0; ivar<3; ivar++)
            {
                // histCorr_Reconstructed[global_bin]
                // histCorr_RecGoodGen_mc[global_bin]
                // histCorr_RecGoodGen_rec[global_bin]
                // histTrue[global_bin_True]
                // histTrue_PionReco[global_bin_True]

                // Corrected with Only Reco Acc / True (RO-T)
                histCT_tmp = (TH1D*) histCorr_Reconstructed[ibin]->Project3D(axis_proj[ivar].c_str());
                histCT_tmp->SetName(Form("histCT_RO-T_Q%iN%i",iQ2,iNu));
                histCT_tmp->Divide(histTrue[ibin]->Project3D(axis_proj[ivar].c_str()));
                histCT_tmp->SetTitle(Form("Closure Test: Corrected with Only Reco Acc / True, %s;%s;Corr_AccReco/True",bin_title.c_str(),axis_title[ivar].c_str()));

                // Corrected with MC vars when Reco matches Gen Acc / True (MC-T)
                histCT_tmp = (TH1D*) histCorr_RecGoodGen_mc[ibin]->Project3D(axis_proj[ivar].c_str());
                histCT_tmp->SetName(Form("histCT_MC-T_Q%iN%i",iQ2,iNu));
                histCT_tmp->Divide(histTrue[ibin]->Project3D(axis_proj[ivar].c_str()));
                histCT_tmp->SetTitle(Form("Closure Test: Corrected with MC_vars Reco when GoodGen Acc / True, %s;%s;Corr_AccMCGoodG/True",bin_title.c_str(),axis_title[ivar].c_str()));

                // Corrected with Reco vars when Reco matches Gen Acc / True (RR-T)
                histCT_tmp = (TH1D*) histCorr_RecGoodGen_rec[ibin]->Project3D(axis_proj[ivar].c_str());
                histCT_tmp->SetName(Form("histCT_RR-T_Q%iN%i",iQ2,iNu));
                histCT_tmp->Divide(histTrue[ibin]->Project3D(axis_proj[ivar].c_str()));
                histCT_tmp->SetTitle(Form("Closure Test: Corrected with Rec_vars Reco when GoodGen Acc / True, %s;%s;Corr_AccRRGoodG/True",bin_title.c_str(),axis_title[ivar].c_str()));
			}
		}
	}

    fout->Write();
    fout->Close();
    facc->Close();
}
*/
