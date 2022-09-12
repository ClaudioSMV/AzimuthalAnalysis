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
#include <fstream>
#include <vector>
#include <string>

using namespace DIS;

inline float DEG2RAD(float x)
{
    return 0.017453293 * x;
}

void Acceptance::ActivateBranches()
{
    fChain->SetBranchStatus("*",0);
    std::vector<string> activeBranches = {"TargType", "Q2", "Nu", "Xb", "Yb", "W", "vyec", "Zh", "Pt2", "PhiPQ", "pid", "Xf"}; // , "Nphe"};
    std::vector<string> activeBranches_mc = {"mc_TargType", "mc_Q2", "mc_Nu", "mc_Xb", "mc_Yb", "mc_W", "mc_Zh", "mc_Pt2", "mc_PhiPQ", "mc_pid", "mc_Xf"};
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

    setNameFormat();
}

void Acceptance::Loop()
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

    ActivateBranches();

    TFile *fout;
    if (!_isClosureTest)
    {
        CreateDir("../output/Acceptance");
        fout = TFile::Open(Form("../output/Acceptance/Acceptance_%s.root", getNameAccFormat().c_str()), "RECREATE");
    }
    else
    {
        CreateDir("../output/ClosureTest");
        fout = TFile::Open(Form("../output/ClosureTest/AccCT_%s.root", getNameAccFormat().c_str()), "RECREATE");
    }

    std::cout << "\n\nBeginning Acceptance calculations for " << _nameTarget << " target\n" << std::endl;


    auto& ThisBins = Bin_List[_binIndex];
    // Define binning
    // OR : Original: {3, 3, 5, 5, 12} = 2700
	// CP : PhiPQ central peak: {3, 3, 5, 5, 40} = 9000 // PhiPQ binning is really important due to the features seen!
	// Int_t nbins[5] = {3, 3, 5, 5, 40};
    double* minbins = &DISLimits[0][0];
    double* maxbins = &DISLimits[1][0];
    int nbins[5] = {static_cast<int>(ThisBins[0].size()-1), static_cast<int>(ThisBins[1].size()-1),
                    static_cast<int>(ThisBins[2].size()-1), static_cast<int>(ThisBins[3].size()-1),
                    static_cast<int>(ThisBins[4].size()-1)};

    // Set variable width bins
	Double_t *Q2_Lmts    = &ThisBins[0][0]; // Q2_binng = {1.0, 1.3, 1.8, 4.1};
	Double_t *Nu_Lmts    = &ThisBins[1][0]; // Nu_binng = {2.2, 3.2, 3.7, 4.2};
	Double_t *Zh_Lmts    = &ThisBins[2][0]; // Zh_binng = {0.0, 0.15, 0.25, 0.4, 0.7, 1.0};
	Double_t *Pt2_Lmts   = &ThisBins[3][0]; // Pt2_binng = {0.0, 0.03, 0.06, 0.1, 0.18, 1.0};
    Double_t *PhiPQ_Lmts = &ThisBins[4][0]; // PhiPQ_binng 40 bins

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
    if (!_isClosureTest) entries_to_process = nentries;
    else                entries_to_process = nentries/2;
    int inclusive_count=0; // global_bin=-1,
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
    histAcc_Reconstructed->Divide(histReco_rec,histTrue,1,1,"B");
    THnSparse *histAcc_RecGoodGen_mc = (THnSparse*)histReco_mc->Clone( "histAcc_RecGoodGen_mc");
    histAcc_RecGoodGen_mc->Divide(histReco_mc,histTrue,1,1,"B");
    THnSparse *histAcc_RecGoodGen_rec = (THnSparse*)histTrue_rec->Clone("histAcc_RecGoodGen_rec");
    histAcc_RecGoodGen_rec->Divide(histTrue_rec,histTrue,1,1,"B");

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

    // Save Summary tables
    if (!_isClosureTest)
    {
        ofstream fileSummary;
        fileSummary.open(Form("../output/Acceptance/Summary_%s.txt", _nameFormatted.c_str()));
        fileSummary << Form(">> Summary table %s Target:\n\n",getNameTarget().c_str());
        SaveSummaryTable(general_El_count,     "General Electron Summary", fileSummary, entries_to_process);
        SaveSummaryTable(mc_El_Reject_count,   "Rejected MC Electron", fileSummary, entries_to_process);
        SaveSummaryTable(mc_El_Accept_count,   "Correctly reconstructed MC Electrons", fileSummary, general_El_count["Total mc_El"]);
        SaveSummaryTable(rec_El_Reject_count,  "Rejected reco Electrons", fileSummary, entries_to_process);
        SaveSummaryTable(rec_El_Accept_count,  "Matching of reconstructed Electrons", fileSummary, general_El_count["Total rec_El"]);
        SaveSummaryTable(general_Pi_count,     "General Pion Summary", fileSummary, inclusive_count);
        SaveSummaryTable(mc_Pi_Reject_count,   "Rejected MC Pion", fileSummary, inclusive_count);
        SaveSummaryTable(mc_Pi_Accept_count,   "Correctly reconstructed MC Pions", fileSummary, general_Pi_count["Total mc_Pi"]);
        SaveSummaryTable(rec_Pi_Reject_count,  "Rejected reco Pions", fileSummary, inclusive_count);
        SaveSummaryTable(rec_Pi_Accept_count,  "Matching of reconstructed Pions", fileSummary, general_Pi_count["Total rec_Pi"]);
        fileSummary.close();
    }

    histTrue->Write();
    histReco_rec->Write();
    histReco_mc->Write();
    histTrue_rec->Write();

    histAcc_Reconstructed->Write();
    histAcc_RecGoodGen_mc->Write();
    histAcc_RecGoodGen_rec->Write();

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

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

void Acceptance::Correction()
{
    // Remember to call Acceptance::setDataType() before, so "mc_" branches are not set (ERROR)
    ActivateBranches();

    auto& ThisBins = Bin_List[_binIndex];
    int nbins[5] = {static_cast<int>(ThisBins[0].size()-1), static_cast<int>(ThisBins[1].size()-1),
                    static_cast<int>(ThisBins[2].size()-1), static_cast<int>(ThisBins[3].size()-1),
                    static_cast<int>(ThisBins[4].size()-1)};

    // Begin Correction
    std::cout << "\n\nBeginning Correction "<< getNameTarget() <<" target:\n" << std::endl;

    CreateDir("../output/Correction");

    TFile *facc = TFile::Open(Form("../output/Acceptance/Acceptance_%s.root", getNameAccFormat().c_str()), "READ");
    TFile *fout = TFile::Open(Form("../output/Correction/Corrected_%s.root", _nameFormatted.c_str()), "RECREATE");

    // Get Acceptance THnSparse
    THnSparse *histAcc_Reconstructed  = (THnSparse*)facc->Get("histAcc_Reconstructed");
    THnSparse *histAcc_RecGoodGen_mc  = (THnSparse*)facc->Get("histAcc_RecGoodGen_mc");
    THnSparse *histAcc_RecGoodGen_rec = (THnSparse*)facc->Get("histAcc_RecGoodGen_rec");

    // Create Final THnSparse
    THnSparse *histCorr_Reconstructed  = CreateFinalHist("Corr_Reconstructed",  nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histCorr_RecGoodGen_mc  = CreateFinalHist("Corr_RecGoodGen_mc",  nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histCorr_RecGoodGen_rec = CreateFinalHist("Corr_RecGoodGen_rec", nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histRaw                 = CreateFinalHist("Raw_data",            nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);

    Long64_t nentries = fChain->GetEntries();
    // unsigned int entries_to_process = nentries/2;

    Long64_t nbytes = 0, nb = 0;
    
    int global_bin=-1;
    int vec_entries=0;
    bool good_electron = false;
    bool good_pion = false;
    std::vector<double> binKinVars;
    for (unsigned int jentry = 0; jentry < nentries; jentry++)
    {
        if (jentry % 1000000 == 0)
            printf("Processing entry %9u, progress at %6.2f%%\n",jentry,100.*(double)jentry/(nentries));

        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        good_electron = false;

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
        }

        if (!good_electron) continue;
        
        vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion = false;

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                good_pion = true;
                binKinVars = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};
            }

            if (!good_pion) continue;

            if (good_pion)
            {
                int bin_Reconstructed  = histAcc_Reconstructed->GetBin(&binKinVars[0]);
                int bin_RecGoodGen_mc  = histAcc_RecGoodGen_mc->GetBin(&binKinVars[0]);
                int bin_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBin(&binKinVars[0]);

                double value_Reconstructed  = histAcc_Reconstructed->GetBinContent(bin_Reconstructed);
                double value_RecGoodGen_mc  = histAcc_RecGoodGen_mc->GetBinContent(bin_RecGoodGen_mc);
                double value_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBinContent(bin_RecGoodGen_rec);

                if (value_Reconstructed  != 0) histCorr_Reconstructed->Fill(&binKinVars[0], 1./value_Reconstructed);
                if (value_RecGoodGen_mc  != 0) histCorr_RecGoodGen_mc->Fill(&binKinVars[0], 1./value_RecGoodGen_mc);
                if (value_RecGoodGen_rec != 0) histCorr_RecGoodGen_rec->Fill(&binKinVars[0], 1./value_RecGoodGen_rec);

                histRaw->Fill(&binKinVars[0]);
            }
        }   // loop over tracks
    }       // loop over entries

    histCorr_Reconstructed->Write();
    histCorr_RecGoodGen_mc->Write();
    histCorr_RecGoodGen_rec->Write();
    histRaw->Write();

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
    facc->Close();
}

void Acceptance::ClosureTest()
{
    // Run over half of the sim and save in "../output/ClosureTest/AccCT_%s_B%i_%iD.root"
    setClosureTest();
    if (!FileExists(Form("../output/ClosureTest/AccCT_%s.root", getNameAccFormat().c_str())))
    {
        std::cout << "Acceptance for ClosureTest doesn't exist. Creating file." << std::endl;
        Loop();
    }
    else
    {
        std::cout << "Acceptance for ClosureTest already exists! Using it." << std::endl;
        ActivateBranches();
    }

    auto& ThisBins = Bin_List[_binIndex];
    int nbins[5] = {static_cast<int>(ThisBins[0].size()-1), static_cast<int>(ThisBins[1].size()-1),
                    static_cast<int>(ThisBins[2].size()-1), static_cast<int>(ThisBins[3].size()-1),
                    static_cast<int>(ThisBins[4].size()-1)};

    // Begin Closure Test
    std::cout << "\n\nBeginning Closure Test for " << _nameTarget << " target\n" << std::endl;

    TFile *facc = TFile::Open(Form("../output/ClosureTest/AccCT_%s.root", getNameAccFormat().c_str()), "READ");
    TFile *fout = TFile::Open(Form("../output/ClosureTest/ClosureTest_%s.root", _nameFormatted.c_str()), "RECREATE");

    // Get Acceptance THnSparse
    THnSparse *histAcc_Reconstructed  = (THnSparse*)facc->Get("histAcc_Reconstructed");
    THnSparse *histAcc_RecGoodGen_mc  = (THnSparse*)facc->Get("histAcc_RecGoodGen_mc");
    THnSparse *histAcc_RecGoodGen_rec = (THnSparse*)facc->Get("histAcc_RecGoodGen_rec");

    // Create Final THnSparse
    THnSparse *histCorr_Reconstructed  = CreateFinalHist("Corr_Reconstructed",  nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histCorr_RecGoodGen_mc  = CreateFinalHist("Corr_RecGoodGen_mc",  nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histCorr_RecGoodGen_rec = CreateFinalHist("Corr_RecGoodGen_rec", nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histTrue                = CreateFinalHist("True",                nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histTrue_PionReco       = CreateFinalHist("True_PionReco",       nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);

    Long64_t nentries = fChain->GetEntries();
    unsigned int entries_to_process = nentries/2;

    Long64_t nbytes = 0, nb = 0;
    
    int global_bin=-1, global_bin_True=-1;
    int vec_entries=0, count = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;
    std::vector<double> binKinVars, binKinVars_mc;
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

        if (GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
        }

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
        }

        if (!good_electron && !good_electron_mc) continue;
        
        vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;

            if (good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
                binKinVars_mc = {mc_Q2, mc_Nu, mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i)};
            }

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                good_pion = true;
                binKinVars = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};
            }

            if (!good_pion_mc && !good_pion) continue;

            if (good_pion_mc)
            {
                histTrue->Fill(&binKinVars_mc[0]);
            }

            if (good_pion)
            {
                int bin_Reconstructed  = histAcc_Reconstructed->GetBin(&binKinVars[0]);
                int bin_RecGoodGen_mc  = histAcc_RecGoodGen_mc->GetBin(&binKinVars[0]);
                int bin_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBin(&binKinVars[0]);

                double value_Reconstructed  = histAcc_Reconstructed->GetBinContent(bin_Reconstructed);
                double value_RecGoodGen_mc  = histAcc_RecGoodGen_mc->GetBinContent(bin_RecGoodGen_mc);
                double value_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBinContent(bin_RecGoodGen_rec);

                if (value_Reconstructed  != 0) histCorr_Reconstructed->Fill(&binKinVars[0], 1./value_Reconstructed);
                if (value_RecGoodGen_mc  != 0) histCorr_RecGoodGen_mc->Fill(&binKinVars[0], 1./value_RecGoodGen_mc);
                if (value_RecGoodGen_rec != 0) histCorr_RecGoodGen_rec->Fill(&binKinVars[0], 1./value_RecGoodGen_rec);
            }

            if (good_pion_mc && good_pion)
            {
                histTrue_PionReco->Fill(&binKinVars_mc[0]);
            }

        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << count << " entries!" << std::endl;

    histCorr_Reconstructed->Write();
    histCorr_RecGoodGen_mc->Write();
    histCorr_RecGoodGen_rec->Write();
    histTrue->Write();
    histTrue_PionReco->Write();

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
    facc->Close();
}

void Acceptance::Get2DProj()
{
    ActivateBranches();

    TFile *fout;
    CreateDir("../output/Proj2D");
    if (_isData) fout = TFile::Open(Form("../output/Proj2D/Get2DProj_%s_data.root", _nameFormatted.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("../output/Proj2D/Get2DProj_%s_hsim.root", _nameFormatted.c_str()), "RECREATE");

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

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

/* WIP
void Acceptance::GetXfVSYh()
{
    ActivateBranches();
    fChain->SetBranchStatus("Eh", 1);
    fChain->SetBranchStatus("Pl2", 1);

    if (!_isData)
    {
        fChain->SetBranchStatus("mc_Eh", 1);
        fChain->SetBranchStatus("mc_Pl2", 1);
    }

    TFile *fout;
    CreateDir("../output/Hist2D_XfVsYh");
    if (_isData) fout = TFile::Open(Form("../output/Hist2D_XfVsYh/XfVsYh_%s_data.root", _nameFormatted.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("../output/Hist2D_XfVsYh/XfVsYh_%s_hsim.root", _nameFormatted.c_str()), "RECREATE");

    //// Define Histograms
    // Reconstructed or data
    TH2D* hist2D_Xf_Yh_reco = new TH2D("hist2D_Xf_Yh_reco", "Two dimensional Map;X_{f};Y_{h}"               , 50,-1.0,1.0, 50,-5.0,5.0);

    // Reconstructed match
    TH2D* hist2D_Xf_Yh_mtch = new TH2D("hist2D_Xf_Yh_mtch", "Two dimensional Map (Reco match);X_{f};Y_{h}"  , 50,-1.0,1.0, 50,-5.0,5.0);

    // Generated (MC)
    TH2D* hist2D_Xf_Yh_gene = new TH2D("hist2D_Xf_Yh_gene", "Two dimensional Map (Generated);X_{f};Y_{h}"   , 50,-1.0,1.0, 50,-5.0,5.0);

    // Bin migration
    TH2D* histMigrationMatrixXf = new TH2D("histMigrationMatrixXf", "Migration X_{f};True X_{f}; Reco X_{f}", 50,-1.0,1.0, 50,-1.0,1.0);
    TH2D* histMigrationMatrixYh = new TH2D("histMigrationMatrixYh", "Migration Y_{h};True Y_{h}; Reco Y_{h}", 50,-5.0,5.0, 50,-5.0,5.0);

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
        }

        if (!_isData && GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
        }

        if (good_electron && good_electron_mc)
        {
        }

        int vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;
            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                n_pions++;
                good_pion = true;
                hist2D_Xf_Yh_reco->Fill(Xf->at(i), Yh->at(i));
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
                hist2D_Xf_Yh_gene->Fill(mc_Xf->at(i), mc_Yh->at(i));
            }

            if (good_pion && good_pion_mc)
            {
                n_pions_match++;
                hist2D_Xf_Yh_mtch->Fill(Xf->at(i), Yh->at(i));

                histMigrationMatrixXf->Fill(mc_Xf->at(i), Xf->at(i));
                histMigrationMatrixYh->Fill(mc_Yh->at(i), Yh->at(i));
            }
        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " final state Pions matching generated." << std::endl;

    if (_isData)
    {
        hist2D_Xf_Yh_gene->Delete();

        hist2D_Xf_Yh_mtch->Delete();

        histMigrationMatrixXf->Delete();
        histMigrationMatrixYh->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}
*/
