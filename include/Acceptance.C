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

    if (_cutDeltaSector0)
    {
        activeBranches.push_back("SectorEl");
        activeBranches.push_back("Sector");
        activeBranches_mc.push_back("mc_SectorEl");
        activeBranches_mc.push_back("mc_Sector");
    }

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
        std::string acc_folder = "../output/Acceptance" + getAccFoldNameExt();
        CreateDir(acc_folder);
        fout = TFile::Open(Form("%s/Acceptance_%s.root", acc_folder.c_str(), getAccFileName().c_str()), "RECREATE");
    }
    else
    {
        std::string ct_folder = "../output/ClosureTest" + getFoldNameExt();
        CreateDir(ct_folder);
        fout = TFile::Open(Form("%s/AccCT_%s.root", ct_folder.c_str(), getAccFileName().c_str()), "RECREATE");
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
    // TEfficiency* effQ2 = new TEfficiency("effQ2", "effQ2;Q^{2} (GeV^{2});Reconstruction Efficiency", 20, DISLimits[0][0], DISLimits[1][0]);
    // TEfficiency* effNu = new TEfficiency("effNu", "effNu;#nu (GeV);Reconstruction Efficiency", 20, DISLimits[0][1], DISLimits[1][1]);
    TEfficiency* effZh = new TEfficiency("effZh", "effZh;z_{h};Reconstruction Efficiency", 20, DISLimits[0][2], DISLimits[1][2]);
    TEfficiency* effPt2 = new TEfficiency("effPt2", "effPt2;p_{T}^{2} (GeV^{2});Reconstruction Efficiency", 20, DISLimits[0][3], DISLimits[1][3]);
    TEfficiency* effPhiPQ = new TEfficiency("effPhiPQ", "effPhiPQ;#phi_{PQ} (deg);Reconstruction Efficiency", 60, DISLimits[0][4], DISLimits[1][4]);

    // one-dimensional resolution histograms
    TH1F* resQ2 = new TH1F("resQ2", "ResolutionQ2;Q^{2}-mc_Q^{2};Counts", 64, -0.3, 0.3);
    TH1F* resNu = new TH1F("resNu", "ResolutionNu;#nu-mc_#nu;Counts", 64, -0.3, 0.3);
    TH1F* resZh = new TH1F("resZh", "ResolutionZh;z_{h}-mc_z_{h};Counts", 64, -0.15, 0.15);
    TH1F* resPt2 = new TH1F("resPt2", "ResolutionPt2;p_{T}^{2}-mc_p_{T}^{2};Counts", 64, -0.15, 0.15);
    TH1F* resPhiPQ = new TH1F("resPhiPQ", "ResolutionPhiPQ;#phi_{PQ}-mc_#phi_{PQ};Counts", 80, -4.0, 4.0);

    // bin Migration
    TH2F* histMigrationMatrixQ2 = new TH2F("histMigrationMatrixQ2", "MigrationQ2;True Q^{2}; Reco Q^{2}", 50, DISLimits[0][0], DISLimits[1][0], 50, DISLimits[0][0], DISLimits[1][0]);
    TH2F* histMigrationMatrixNu = new TH2F("histMigrationMatrixNu", "MigrationNu;True #nu; Reco #nu", 50, DISLimits[0][1], DISLimits[1][1], 50, DISLimits[0][1], DISLimits[1][1]);
    TH2F* histMigrationMatrixZh = new TH2F("histMigrationMatrixZh", "MigrationZh;True z_{h}; Reco z_{h}", 50, DISLimits[0][2], DISLimits[1][2], 50, DISLimits[0][2], DISLimits[1][2]);
    TH2F* histMigrationMatrixPt2 = new TH2F("histMigrationMatrixPt2", "MigrationPt2;True p_{T}^{2} (GeV^{2});Reco p_{T}^{2} (GeV^{2})", 50, DISLimits[0][3], DISLimits[1][3], 50, DISLimits[0][3], DISLimits[1][3]);
    TH2F* histMigrationMatrixPhiPQ = new TH2F("histMigrationMatrixPhiPQ", "MigrationPhiPQ;True #phi_{PQ} (deg);Reco #phi_{PQ} (deg)", 120, DISLimits[0][4], DISLimits[1][4], 120, DISLimits[0][4], DISLimits[1][4]);

    // THnSparse
    THnSparse *histTrue = new THnSparseD("histTrue","True", 5,nbins,minbins,maxbins);
    THnSparse *histReco_rec = new THnSparseD("histReco_rec","Reconstructed only", 5,nbins,minbins,maxbins);
    THnSparse *histReco_mc = new THnSparseD("histReco_mc","Good reconstructed with mc_vars", 5,nbins,minbins,maxbins);
    THnSparse *histTrue_rec = new THnSparseD("histTrue_rec","Good reconstructed with reco_vars", 5,nbins,minbins,maxbins);

    SetVariableSize(histTrue, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);     // Good Generated (Doesn't care of Reco), filled with Generated kinematic vars
    SetVariableSize(histReco_rec, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts); // Good Reco (Doesn't care of Generated), filled with Reco kinematic vars
    SetVariableSize(histReco_mc, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts);  // Good Reco & Generated, filled with Generated kinematic vars
    SetVariableSize(histTrue_rec, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts); // Good Reco & Generated, filled with Reco kinematic vars

	histTrue->Sumw2();
	histReco_rec->Sumw2();
	histReco_mc->Sumw2();
	histTrue_rec->Sumw2();

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
    bool save_lepton_vars = true;

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
        
        // Save leptonic variables only when there is at least one pion
        save_lepton_vars=true;

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

                resZh->Fill(Zh->at(i) - mc_Zh->at(i));
                resPt2->Fill(Pt2->at(i) - mc_Pt2->at(i));

                // Save PhiPQ considering that it's a cyclic variable
                double delta_PhiPQ = PhiPQ->at(i) - mc_PhiPQ->at(i);
                if (abs(delta_PhiPQ) > 350.)
                {
                    if (delta_PhiPQ>0) resPhiPQ->Fill(delta_PhiPQ-360);
                    else               resPhiPQ->Fill(delta_PhiPQ+360);
                }
                else
                {
                    resPhiPQ->Fill(delta_PhiPQ);
                }

                histReco_mc->Fill(mc_bin);
                histTrue_rec->Fill(rec_bin);

                if (save_lepton_vars)
                {
                    histMigrationMatrixQ2->Fill(mc_Q2, Q2);
                    histMigrationMatrixNu->Fill(mc_Nu, Nu);

                    resQ2->Fill(Q2 - mc_Q2);
                    resNu->Fill(Nu - mc_Nu);

                    save_lepton_vars = false;
                }
            }

            effZh->Fill(pion_passed, mc_Zh->at(i));
            effPt2->Fill(pion_passed, mc_Pt2->at(i));
            effPhiPQ->Fill(pion_passed, mc_PhiPQ->at(i));
        }   // loop over tracks
    }       // loop over entries

    // Acceptance
    THnSparse *histAcc_Reconstru = (THnSparse*)histReco_rec->Clone("histAcc_Reconstru");
    histAcc_Reconstru->Divide(histReco_rec,histTrue,1,1,"B");
    THnSparse *histAcc_ReMtch_mc = (THnSparse*)histReco_mc->Clone( "histAcc_ReMtch_mc");
    histAcc_ReMtch_mc->Divide(histReco_mc,histTrue,1,1,"B");
    THnSparse *histAcc_ReMtch_re = (THnSparse*)histTrue_rec->Clone("histAcc_ReMtch_re");
    histAcc_ReMtch_re->Divide(histTrue_rec,histTrue,1,1,"B");

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
        std::string acc_folder = "../output/Acceptance" + getAccFoldNameExt();
        fileSummary.open(Form("%s/Summary_%s.txt", acc_folder.c_str(), _nameFormatted.c_str()));
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

    PrintFilledBins(histAcc_Reconstru);
    PrintFilledBins(histAcc_ReMtch_mc);
    PrintFilledBins(histAcc_ReMtch_re);

    histTrue->Write();
    histReco_rec->Write();
    histReco_mc->Write();
    histTrue_rec->Write();

    histAcc_Reconstru->Write();
    histAcc_ReMtch_mc->Write();
    histAcc_ReMtch_re->Write();

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

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

    std::string acc_folder = "../output/Acceptance" + getAccFoldNameExt();
    std::string cor_folder = "../output/Correction" + getFoldNameExt();
    CreateDir(cor_folder);

    TFile *facc = TFile::Open(Form("%s/Acceptance_%s.root", acc_folder.c_str(), getAccFileName().c_str()), "READ");
    TFile *fout = TFile::Open(Form("%s/Corrected_%s.root", cor_folder.c_str(), _nameFormatted.c_str()), "RECREATE");

    // Get Acceptance THnSparse
    THnSparse *histAcc_Reconstru = (THnSparse*)facc->Get("histAcc_Reconstru");
    THnSparse *histAcc_ReMtch_mc = (THnSparse*)facc->Get("histAcc_ReMtch_mc");
    THnSparse *histAcc_ReMtch_re = (THnSparse*)facc->Get("histAcc_ReMtch_re");

    // Create Final THnSparse
    THnSparse *histCorr_Reconstru = CreateFinalHist("Corr_Reconstru", nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histCorr_ReMtch_mc = CreateFinalHist("Corr_ReMtch_mc", nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histCorr_ReMtch_re = CreateFinalHist("Corr_ReMtch_re", nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histRaw            = CreateFinalHist("Raw_data",       nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);

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
                // Reconstru
                CorrectBin(binKinVars, histAcc_Reconstru, histCorr_Reconstru, _useFullError);

                // ReMtch_mc
                CorrectBin(binKinVars, histAcc_ReMtch_mc, histCorr_ReMtch_mc, _useFullError);

                // ReMtch_re
                CorrectBin(binKinVars, histAcc_ReMtch_re, histCorr_ReMtch_re, _useFullError);

                histRaw->Fill(&binKinVars[0]);
            }
        }   // loop over tracks
    }       // loop over entries

    histCorr_Reconstru->Write();
    histCorr_ReMtch_mc->Write();
    histCorr_ReMtch_re->Write();
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

    std::string ct_folder = "../output/ClosureTest" + getFoldNameExt();
    if (!FileExists(Form("%s/AccCT_%s.root", ct_folder.c_str(), getAccFileName().c_str())))
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

    TFile *facc = TFile::Open(Form("%s/AccCT_%s.root", ct_folder.c_str(), getAccFileName().c_str()), "READ");
    TFile *fout = TFile::Open(Form("%s/ClosureTest_%s.root", ct_folder.c_str(), _nameFormatted.c_str()), "RECREATE");

    // Get Acceptance THnSparse
    THnSparse *histAcc_Reconstru = (THnSparse*)facc->Get("histAcc_Reconstru");
    THnSparse *histAcc_ReMtch_mc = (THnSparse*)facc->Get("histAcc_ReMtch_mc");
    THnSparse *histAcc_ReMtch_re = (THnSparse*)facc->Get("histAcc_ReMtch_re");

    // Create Final THnSparse
    THnSparse *histCorr_Reconstru = CreateFinalHist("Corr_Reconstru", nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histCorr_ReMtch_mc = CreateFinalHist("Corr_ReMtch_mc", nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histCorr_ReMtch_re = CreateFinalHist("Corr_ReMtch_re", nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histTrue           = CreateFinalHist("True",           nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);
    THnSparse *histTrue_PionReco  = CreateFinalHist("True_PionReco",  nbins, &(Correction::NIrregBins[_binNdims]), ThisBins, DISLimits);

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
                // Reconstructed
                CorrectBin(binKinVars, histAcc_Reconstru, histCorr_Reconstru, _useFullError);

                // ReMtch_mc
                CorrectBin(binKinVars, histAcc_ReMtch_mc, histCorr_ReMtch_mc, _useFullError);

                // ReMtch_re
                CorrectBin(binKinVars, histAcc_ReMtch_re, histCorr_ReMtch_re, _useFullError);
            }

            if (good_pion_mc && good_pion)
            {
                histTrue_PionReco->Fill(&binKinVars_mc[0]);
            }

        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << count << " entries!" << std::endl;

    histCorr_Reconstru->Write();
    histCorr_ReMtch_mc->Write();
    histCorr_ReMtch_re->Write();
    histTrue->Write();
    histTrue_PionReco->Write();

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
    facc->Close();
}

void Acceptance::Hist2D_KinVars()
{
    ActivateBranches();

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    CreateDir(h2d_folder);

    if (_isData) fout = TFile::Open(Form("%s/KinematicVars_%s_data.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/KinematicVars_%s_hsim.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");

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
    TH2D* hist2D_Q2_Nu_goodPi_reco = new TH2D("hist2D_Q2_Nu_goodPi_reco", "Two dimensional Map;Q^{2} [GeV^{2}];#nu [GeV]", 50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][1], DISLimits[1][1]);

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
    TH2D* hist2D_Q2_Nu_goodPi_mtch = new TH2D("hist2D_Q2_Nu_goodPi_mtch", "Two dimensional Map (Reco match);Q^{2} [GeV^{2}];#nu [GeV]", 50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][1], DISLimits[1][1]);

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
    TH2D* hist2D_Q2_Nu_goodPi_gene = new TH2D("hist2D_Q2_Nu_goodPi_gene", "Two dimensional Map (Generated);Q^{2} [GeV^{2}];#nu [GeV]", 50, DISLimits[0][0], DISLimits[1][0],  50, DISLimits[0][1], DISLimits[1][1]);

    // Bin migration
    TH2D* histMigrationMatrixQ2 = new TH2D("histMigrationMatrixQ2", "Migration Q^{2};True Q^{2} [GeV^{2}]; Reco Q^{2} [GeV^{2}]"           , 50,DISLimits[0][0],DISLimits[1][0], 50,DISLimits[0][0],DISLimits[1][0]);
    TH2D* histMigrationMatrixNu = new TH2D("histMigrationMatrixNu", "Migration #nu;True Nu [GeV]; Reco Nu [GeV]"                           , 50,DISLimits[0][1],DISLimits[1][1], 50,DISLimits[0][1],DISLimits[1][1]);
    TH2D* histMigrationMatrixZh = new TH2D("histMigrationMatrixZh", "Migration Z_{h};True Z_{h}; Reco Z_{h}"                               , 50,DISLimits[0][2],DISLimits[1][2], 50,DISLimits[0][2],DISLimits[1][2]);
    TH2D* histMigrationMatrixPt = new TH2D("histMigrationMatrixPt", "Migration P_{T}^{2};True P_{T}^{2} [GeV^{2}];Reco P_{T}^{2} [GeV^{2}]", 50,DISLimits[0][3],DISLimits[1][3], 50,DISLimits[0][3],DISLimits[1][3]);
    TH2D* histMigrationMatrixPQ = new TH2D("histMigrationMatrixPQ", "Migration #phi_{PQ};True #phi_{PQ} [deg];Reco #phi_{PQ} [deg]"        ,180,DISLimits[0][4],DISLimits[1][4],180,DISLimits[0][4],DISLimits[1][4]);
    TH2D* histMigrationMatrixQ2_goodPi = new TH2D("histMigrationMatrixQ2_goodPi", "Migration Q^{2};True Q^{2} [GeV^{2}]; Reco Q^{2} [GeV^{2}]", 50,DISLimits[0][0],DISLimits[1][0], 50,DISLimits[0][0],DISLimits[1][0]);
    TH2D* histMigrationMatrixNu_goodPi = new TH2D("histMigrationMatrixNu_goodPi", "Migration #nu;True Nu [GeV]; Reco Nu [GeV]"                , 50,DISLimits[0][1],DISLimits[1][1], 50,DISLimits[0][1],DISLimits[1][1]);
    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    unsigned int entries_to_process = nentries;
    int n_pions = 0, n_pions_match = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;
    bool at_least_one_mcPion = false, at_least_one_Pion = false, at_least_one_Pion_mtch = false;

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
        at_least_one_mcPion = false, at_least_one_Pion = false, at_least_one_Pion_mtch = false;

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

                at_least_one_Pion = true;
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

                at_least_one_mcPion = true;
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

                at_least_one_Pion_mtch = true;
            }
        }   // loop over tracks

        if (at_least_one_Pion) hist2D_Q2_Nu_goodPi_reco->Fill(Q2,Nu);

        if (at_least_one_mcPion) hist2D_Q2_Nu_goodPi_gene->Fill(mc_Q2,mc_Nu);

        if (at_least_one_Pion_mtch)
        {
            hist2D_Q2_Nu_goodPi_mtch->Fill(Q2,Nu);

            histMigrationMatrixQ2_goodPi->Fill(mc_Q2,Q2);
            histMigrationMatrixNu_goodPi->Fill(mc_Nu,Nu);
        }
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
        hist2D_Q2_Nu_goodPi_gene->Delete();

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
        hist2D_Q2_Nu_goodPi_mtch->Delete();

        histMigrationMatrixQ2->Delete();
        histMigrationMatrixNu->Delete();
        histMigrationMatrixZh->Delete();
        histMigrationMatrixPt->Delete();
        histMigrationMatrixPQ->Delete();
        histMigrationMatrixQ2_goodPi->Delete();
        histMigrationMatrixNu_goodPi->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

void Acceptance::Hist2D_XfVsYh()
{
    ActivateBranches();
    fChain->SetBranchStatus("Pl2", 1);

    if (!_isData)
    {
        fChain->SetBranchStatus("mc_Pl2", 1);
    }

    double PlCM=0, mc_PlCM=0;
    double EhCM=0, mc_EhCM=0;
    double Yh=0, mc_Yh=0;
    double kMassProton = 0.938272;
    double kMassPiPlus = 0.139570;

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    CreateDir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/XfVsYh_%s_data.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/XfVsYh_%s_hsim.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");

    //// Define Histograms
    // Simple TH1
    TH1D* hist1D_Xf_reco = new TH1D("hist1D_Xf_reco", "Histogram 1D Reconstructed;X_{f};Counts", 120,-1.1,1.1);
    TH1D* hist1D_Xf_mtch = new TH1D("hist1D_Xf_mtch", "Histogram 1D Reconstructed match;X_{f};Counts", 120,-1.1,1.1);
    TH1D* hist1D_Xf_gene = new TH1D("hist1D_Xf_gene", "Histogram 1D Generated;X_{f};Counts", 120,-1.1,1.1);

    TH1D* hist1D_Yh_reco = new TH1D("hist1D_Yh_reco", "Histogram 1D Reconstructed;Y_{h};Counts", 100,-2.5,2.5);
    TH1D* hist1D_Yh_mtch = new TH1D("hist1D_Yh_mtch", "Histogram 1D Reconstructed match;Y_{h};Counts", 100,-2.5,2.5);
    TH1D* hist1D_Yh_gene = new TH1D("hist1D_Yh_gene", "Histogram 1D Generated;Y_{h};Counts", 100,-2.5,2.5);

    // Reconstructed or data
    TH2D* hist2D_Xf_Yh_reco = new TH2D("hist2D_Xf_Yh_reco", "Two dimensional Map;X_{f};Y_{h}"               , 60,-1.0,1.0, 100,-2.5,2.5);

    // Reconstructed match
    TH2D* hist2D_Xf_Yh_mtch = new TH2D("hist2D_Xf_Yh_mtch", "Two dimensional Map (Reco match);X_{f};Y_{h}"  , 60,-1.0,1.0, 100,-2.5,2.5);

    // Generated (MC)
    TH2D* hist2D_Xf_Yh_gene = new TH2D("hist2D_Xf_Yh_gene", "Two dimensional Map (Generated);X_{f};Y_{h}"   , 60,-1.0,1.0, 100,-2.5,2.5);

    // Bin migration
    TH2D* histMigrationMatrixXf = new TH2D("histMigrationMatrixXf", "Migration X_{f};True X_{f}; Reco X_{f}", 60,-1.0,1.0, 60,-1.0,1.0);
    TH2D* histMigrationMatrixYh = new TH2D("histMigrationMatrixYh", "Migration Y_{h};True Y_{h}; Reco Y_{h}", 100,-2.5,2.5, 100,-2.5,2.5);

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
            PlCM=0, EhCM=0, Yh=0;
            mc_PlCM=0, mc_EhCM=0, mc_Yh=0;

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                n_pions++;
                good_pion = true;

                PlCM = (TMath::Sqrt(Pl2->at(i)) - Zh->at(i) * Nu * TMath::Sqrt(Q2 + Nu * Nu) / (Nu + kMassProton)) * (Nu + kMassProton) / W;
                EhCM = (W * W + kMassPiPlus - kMassProton)/(2*W);

                Yh = TMath::Log((EhCM + PlCM)/(EhCM - PlCM))/2.;

                hist1D_Xf_reco->Fill(Xf->at(i));
                hist1D_Yh_reco->Fill(Yh);
                hist2D_Xf_Yh_reco->Fill(Xf->at(i), Yh);
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;

                mc_PlCM = (TMath::Sqrt(mc_Pl2->at(i)) - mc_Zh->at(i) * mc_Nu * TMath::Sqrt(mc_Q2 + mc_Nu * mc_Nu) / (mc_Nu + kMassProton)) * (mc_Nu + kMassProton) / mc_W;
                mc_EhCM = (mc_W * mc_W + kMassPiPlus - kMassProton)/(2*mc_W);

                mc_Yh = TMath::Log((mc_EhCM + mc_PlCM)/(mc_EhCM - mc_PlCM))/2.;

                hist1D_Xf_gene->Fill(mc_Xf->at(i));
                hist1D_Yh_gene->Fill(mc_Yh);
                hist2D_Xf_Yh_gene->Fill(mc_Xf->at(i), mc_Yh);
            }

            if (good_pion && good_pion_mc)
            {
                n_pions_match++;

                hist1D_Xf_mtch->Fill(Xf->at(i));
                hist1D_Yh_mtch->Fill(Yh);
                hist2D_Xf_Yh_mtch->Fill(Xf->at(i), Yh);

                histMigrationMatrixXf->Fill(mc_Xf->at(i), Xf->at(i));
                histMigrationMatrixYh->Fill(mc_Yh, Yh);
            }
        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " final state Pions matching generated." << std::endl;

    if (_isData)
    {
        hist1D_Xf_mtch->Delete();
        hist1D_Xf_gene->Delete();
        hist1D_Yh_mtch->Delete();
        hist1D_Yh_gene->Delete();

        hist2D_Xf_Yh_gene->Delete();
        hist2D_Xf_Yh_mtch->Delete();

        histMigrationMatrixXf->Delete();
        histMigrationMatrixYh->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

void Acceptance::Hist2D_ThetaPQ()
{
    ActivateBranches();
    fChain->SetBranchStatus("ThetaPQ", 1);
    fChain->SetBranchStatus("Pl2", 1);

    if (!_isData)
    {
        fChain->SetBranchStatus("mc_ThetaPQ", 1);
        fChain->SetBranchStatus("mc_Pl2", 1);
    }

    double PlCM=0, mc_PlCM=0;
    double EhCM=0, mc_EhCM=0;
    double Yh=0, mc_Yh=0;
    double kMassProton = 0.938272;
    double kMassPiPlus = 0.139570;

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    CreateDir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/ThetaPQ_%s_data.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/ThetaPQ_%s_hsim.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");

    //// Define Histograms
    // Simple TH1
    TH1D* hist1D_ThPQ_reco = new TH1D("hist1D_ThPQ_reco", "Histogram 1D Reconstructed;#theta_{PQ};Counts", 180,0.0,180.0);
    TH1D* hist1D_ThPQ_mtch = new TH1D("hist1D_ThPQ_mtch", "Histogram 1D Reconstructed match;#theta_{PQ};Counts", 180,0.0,180.0);
    TH1D* hist1D_ThPQ_gene = new TH1D("hist1D_ThPQ_gene", "Histogram 1D Generated;#theta_{PQ};Counts", 180,0.0,180.0);

    // TH1D* hist1D_Yh_reco = new TH1D("hist1D_Yh_reco", "Histogram 1D Reconstructed;Y_{h};Counts", 100,-2.5,2.5);
    // TH1D* hist1D_Yh_mtch = new TH1D("hist1D_Yh_mtch", "Histogram 1D Reconstructed match;Y_{h};Counts", 100,-2.5,2.5);
    // TH1D* hist1D_Yh_gene = new TH1D("hist1D_Yh_gene", "Histogram 1D Generated;Y_{h};Counts", 100,-2.5,2.5);

    // Reconstructed or data
    TH2D* hist2D_ThPQ_PhiPQ_reco = new TH2D("hist2D_ThPQ_PhiPQ_reco", "Two dimensional Map;#theta_{PQ};#phi_{PQ}" , 180,0.0,180.0, 180,-180.0,180.0);
    TH2D* hist2D_ThPQ_Yh_reco    = new TH2D("hist2D_ThPQ_Yh_reco", "Two dimensional Map;#theta_{PQ};Y_{h}"        , 180,0.0,180.0, 100,-2.5,2.5);
    TH2D* hist2D_PhiPQ_Yh_reco    = new TH2D("hist2D_PhiPQ_Yh_reco", "Two dimensional Map;#phi_{PQ};Y_{h}"        , 180,-180.0,180.0, 100,-2.5,2.5);

    // Reconstructed match
    TH2D* hist2D_ThPQ_PhiPQ_mtch = new TH2D("hist2D_ThPQ_PhiPQ_mtch", "Two dimensional Map (Reco match);#theta_{PQ};#phi_{PQ}"  , 180,0.0,180.0, 180,-180.0,180.0);
    TH2D* hist2D_ThPQ_Yh_mtch    = new TH2D("hist2D_ThPQ_Yh_mtch", "Two dimensional Map (Reco match);#theta_{PQ};Y_{h}"        , 180,0.0,180.0, 100,-2.5,2.5);
    TH2D* hist2D_PhiPQ_Yh_mtch    = new TH2D("hist2D_PhiPQ_Yh_mtch", "Two dimensional Map (Reco match);#phi_{PQ};Y_{h}"        , 180,-180.0,180.0, 100,-2.5,2.5);

    // Generated (MC)
    TH2D* hist2D_ThPQ_PhiPQ_gene = new TH2D("hist2D_ThPQ_PhiPQ_gene", "Two dimensional Map (Generated);#theta_{PQ};#phi_{PQ}"   , 180,0.0,180.0, 180,-180.0,180.0);
    TH2D* hist2D_ThPQ_Yh_gene    = new TH2D("hist2D_ThPQ_Yh_gene", "Two dimensional Map (Generated);#theta_{PQ};Y_{h}"        , 180,0.0,180.0, 100,-2.5,2.5);
    TH2D* hist2D_PhiPQ_Yh_gene    = new TH2D("hist2D_PhiPQ_Yh_gene", "Two dimensional Map (Generated);#phi_{PQ};Y_{h}"        , 180,-180.0,180.0, 100,-2.5,2.5);

    // Bin migration
    TH2D* histMigrationMatrixThPQ = new TH2D("histMigrationMatrixThPQ", "Migration #theta_{PQ};True #theta_{PQ}; Reco #theta_{PQ}", 180,0.0,180.0, 180,0.0,180.0);
    // TH2D* histMigrationMatrixYh = new TH2D("histMigrationMatrixYh", "Migration Y_{h};True Y_{h}; Reco Y_{h}", 100,-2.5,2.5, 100,-2.5,2.5);

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
            PlCM=0, EhCM=0, Yh=0;
            mc_PlCM=0, mc_EhCM=0, mc_Yh=0;

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                n_pions++;
                good_pion = true;

                PlCM = (TMath::Sqrt(Pl2->at(i)) - Zh->at(i) * Nu * TMath::Sqrt(Q2 + Nu * Nu) / (Nu + kMassProton)) * (Nu + kMassProton) / W;
                EhCM = (W * W + kMassPiPlus - kMassProton)/(2*W);

                Yh = TMath::Log((EhCM + PlCM)/(EhCM - PlCM))/2.;

                hist1D_ThPQ_reco->Fill(ThetaPQ->at(i));
                // hist1D_Yh_reco->Fill(Yh);
                hist2D_ThPQ_PhiPQ_reco->Fill(ThetaPQ->at(i), PhiPQ->at(i));
                hist2D_ThPQ_Yh_reco->Fill(ThetaPQ->at(i), Yh);
                hist2D_PhiPQ_Yh_reco->Fill(PhiPQ->at(i), Yh);
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;

                mc_PlCM = (TMath::Sqrt(mc_Pl2->at(i)) - mc_Zh->at(i) * mc_Nu * TMath::Sqrt(mc_Q2 + mc_Nu * mc_Nu) / (mc_Nu + kMassProton)) * (mc_Nu + kMassProton) / mc_W;
                mc_EhCM = (mc_W * mc_W + kMassPiPlus - kMassProton)/(2*mc_W);

                mc_Yh = TMath::Log((mc_EhCM + mc_PlCM)/(mc_EhCM - mc_PlCM))/2.;

                hist1D_ThPQ_gene->Fill(mc_ThetaPQ->at(i));
                // hist1D_Yh_gene->Fill(mc_Yh);
                hist2D_ThPQ_PhiPQ_gene->Fill(mc_ThetaPQ->at(i), mc_PhiPQ->at(i));
                hist2D_ThPQ_Yh_gene->Fill(mc_ThetaPQ->at(i), mc_Yh);
                hist2D_PhiPQ_Yh_gene->Fill(mc_PhiPQ->at(i), mc_Yh);
            }

            if (good_pion && good_pion_mc)
            {
                n_pions_match++;

                hist1D_ThPQ_mtch->Fill(ThetaPQ->at(i));
                // hist1D_Yh_mtch->Fill(Yh);
                hist2D_ThPQ_PhiPQ_mtch->Fill(ThetaPQ->at(i), PhiPQ->at(i));
                hist2D_ThPQ_Yh_mtch->Fill(ThetaPQ->at(i), Yh);
                hist2D_PhiPQ_Yh_mtch->Fill(PhiPQ->at(i), Yh);

                histMigrationMatrixThPQ->Fill(mc_ThetaPQ->at(i), ThetaPQ->at(i));
                // histMigrationMatrixYh->Fill(mc_Yh, Yh);
            }
        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " final state Pions matching generated." << std::endl;

    if (_isData)
    {
        hist1D_ThPQ_mtch->Delete();
        hist1D_ThPQ_gene->Delete();
        // hist1D_Yh_mtch->Delete();
        // hist1D_Yh_gene->Delete();

        hist2D_ThPQ_PhiPQ_mtch->Delete();
        hist2D_ThPQ_PhiPQ_gene->Delete();
        hist2D_ThPQ_Yh_mtch->Delete();
        hist2D_ThPQ_Yh_gene->Delete();
        hist2D_PhiPQ_Yh_mtch->Delete();
        hist2D_PhiPQ_Yh_gene->Delete();

        histMigrationMatrixThPQ->Delete();
        // histMigrationMatrixYh->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

void Acceptance::Hist2D_LabAngles()
{
    ActivateBranches();
    fChain->SetBranchStatus("PhiLabEl", 1);
    fChain->SetBranchStatus("ThetaLabEl", 1);
    fChain->SetBranchStatus("PhiLab", 1);
    fChain->SetBranchStatus("ThetaLab", 1);

    if (!_isData)
    {
        fChain->SetBranchStatus("mc_PhiLabEl", 1);
        fChain->SetBranchStatus("mc_ThetaLabEl", 1);
        fChain->SetBranchStatus("mc_PhiLab", 1);
        fChain->SetBranchStatus("mc_ThetaLab", 1);
    }

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    CreateDir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/LabAngles_%s_data.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/LabAngles_%s_hsim.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");

    //// Define Histograms
    // Simple TH1
    TH1D* hist1D_ThLabEl_reco = new TH1D("hist1D_ThLabEl_reco", "Histogram 1D Reconstructed;#theta_{Lab} El;Counts", 180,0.0,180.0);
    TH1D* hist1D_ThLabEl_mtch = new TH1D("hist1D_ThLabEl_mtch", "Histogram 1D Reconstructed match;#theta_{Lab} El;Counts", 180,0.0,180.0);
    TH1D* hist1D_ThLabEl_gene = new TH1D("hist1D_ThLabEl_gene", "Histogram 1D Generated;#theta_{Lab} El;Counts", 180,0.0,180.0);

    TH1D* hist1D_PhiLabEl_reco = new TH1D("hist1D_PhiLabEl_reco", "Histogram 1D Reconstructed;#phi_{Lab} El;Counts", 180,-30.0,330.0);
    TH1D* hist1D_PhiLabEl_mtch = new TH1D("hist1D_PhiLabEl_mtch", "Histogram 1D Reconstructed match;#phi_{Lab} El;Counts", 180,-30.0,330.0);
    TH1D* hist1D_PhiLabEl_gene = new TH1D("hist1D_PhiLabEl_gene", "Histogram 1D Generated;#phi_{Lab} El;Counts", 180,-30.0,330.0);

    TH1D* hist1D_ThLab_reco = new TH1D("hist1D_ThLab_reco", "Histogram 1D Reconstructed;#theta_{Lab};Counts", 180,0.0,180.0);
    TH1D* hist1D_ThLab_mtch = new TH1D("hist1D_ThLab_mtch", "Histogram 1D Reconstructed match;#theta_{Lab};Counts", 180,0.0,180.0);
    TH1D* hist1D_ThLab_gene = new TH1D("hist1D_ThLab_gene", "Histogram 1D Generated;#theta_{Lab};Counts", 180,0.0,180.0);

    TH1D* hist1D_PhiLab_reco = new TH1D("hist1D_PhiLab_reco", "Histogram 1D Reconstructed;#phi_{Lab};Counts", 180,-30.0,330.0);
    TH1D* hist1D_PhiLab_mtch = new TH1D("hist1D_PhiLab_mtch", "Histogram 1D Reconstructed match;#phi_{Lab};Counts", 180,-30.0,330.0);
    TH1D* hist1D_PhiLab_gene = new TH1D("hist1D_PhiLab_gene", "Histogram 1D Generated;#phi_{Lab};Counts", 180,-30.0,330.0);

    TH1D* hist1D_ThLabEl_mtch_Pi = new TH1D("hist1D_ThLabEl_mtch_Pi", "Histogram 1D Reconstructed match, good Pion;#theta_{Lab} El;Counts", 180,0.0,180.0);
    TH1D* hist1D_PhiLabEl_mtch_Pi = new TH1D("hist1D_PhiLabEl_mtch_Pi", "Histogram 1D Reconstructed match, good Pion;#phi_{Lab} El;Counts", 180,-30.0,330.0);

    // Reconstructed or data
    TH2D* hist2D_ThLabEl_PhiLabEl_reco = new TH2D("hist2D_ThLabEl_PhiLabEl_reco", "Two dimensional Map;#theta_{Lab} El;#phi_{Lab} El" , 180,0.0,180.0, 180,-30.0,330.0);
    TH2D* hist2D_ThLab_PhiLab_reco = new TH2D("hist2D_ThLab_PhiLab_reco", "Two dimensional Map;#theta_{Lab};#phi_{Lab}" , 180,0.0,180.0, 180,-30.0,330.0);

    // Reconstructed match
    TH2D* hist2D_ThLabEl_PhiLabEl_mtch = new TH2D("hist2D_ThLabEl_PhiLabEl_mtch", "Two dimensional Map;#theta_{Lab} El;#phi_{Lab} El" , 180,0.0,180.0, 180,-30.0,330.0);
    TH2D* hist2D_ThLab_PhiLab_mtch = new TH2D("hist2D_ThLab_PhiLab_mtch", "Two dimensional Map;#theta_{Lab};#phi_{Lab}" , 180,0.0,180.0, 180,-30.0,330.0);

    TH2D* hist2D_ThLabEl_PhiLabEl_mtch_Pi = new TH2D("hist2D_ThLabEl_PhiLabEl_mtch_Pi", "Two dimensional Map, good Pion;#theta_{Lab} El;#phi_{Lab} El" , 180,0.0,180.0, 180,-30.0,330.0);

    // Generated (MC)
    TH2D* hist2D_ThLabEl_PhiLabEl_gene = new TH2D("hist2D_ThLabEl_PhiLabEl_gene", "Two dimensional Map;#theta_{Lab} El;#phi_{Lab} El" , 180,0.0,180.0, 180,-30.0,330.0);
    TH2D* hist2D_ThLab_PhiLab_gene = new TH2D("hist2D_ThLab_PhiLab_gene", "Two dimensional Map;#theta_{Lab};#phi_{Lab}" , 180,0.0,180.0, 180,-30.0,330.0);

    // Bin migration
    TH2D* histMigrationMatrixThLabEl = new TH2D("histMigrationMatrixThLabEl", "Migration #theta_{Lab} El;True #theta_{Lab} El; Reco #theta_{Lab} El", 180,0.0,180.0, 180,0.0,180.0);
    TH2D* histMigrationMatrixPhiLabEl = new TH2D("histMigrationMatrixPhiLabEl", "Migration #phi_{Lab} El;True #phi_{Lab} El; Reco #phi_{Lab} El", 180,-30.0,330.0, 180,-30.0,330.0);
    TH2D* histMigrationMatrixThLab = new TH2D("histMigrationMatrixThLab", "Migration #theta_{Lab};True #theta_{Lab}; Reco #theta_{Lab}", 180,0.0,180.0, 180,0.0,180.0);
    TH2D* histMigrationMatrixPhiLab = new TH2D("histMigrationMatrixPhiLab", "Migration #phi_{Lab};True #phi_{Lab}; Reco #phi_{Lab}", 180,-30.0,330.0, 180,-30.0,330.0);

    TH2D* histMigrationMatrixThLabEl_Pi = new TH2D("histMigrationMatrixThLabEl_Pi", "Migration #theta_{Lab} El, good Pion;True #theta_{Lab} El; Reco #theta_{Lab} El", 180,0.0,180.0, 180,0.0,180.0);
    TH2D* histMigrationMatrixPhiLabEl_Pi = new TH2D("histMigrationMatrixPhiLabEl_Pi", "Migration #phi_{Lab} El, good Pion;True #phi_{Lab} El; Reco #phi_{Lab} El", 180,-30.0,330.0, 180,-30.0,330.0);

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    unsigned int entries_to_process = nentries;
    int n_pions = 0, n_pions_match = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;
    bool at_least_one_pion_mtch = false;

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
        at_least_one_pion_mtch = false;

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
            hist1D_ThLabEl_reco->Fill(ThetaLabEl);
            hist1D_PhiLabEl_reco->Fill(PhiLabEl);

            hist2D_ThLabEl_PhiLabEl_reco->Fill(ThetaLabEl, PhiLabEl);
        }

        if (!_isData && GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
            hist1D_ThLabEl_gene->Fill(mc_ThetaLabEl);
            hist1D_PhiLabEl_gene->Fill(mc_PhiLabEl);

            hist2D_ThLabEl_PhiLabEl_gene->Fill(mc_ThetaLabEl, mc_PhiLabEl);
        }

        if (good_electron && good_electron_mc)
        {
            hist1D_ThLabEl_mtch->Fill(ThetaLabEl);
            hist1D_PhiLabEl_mtch->Fill(PhiLabEl);

            hist2D_ThLabEl_PhiLabEl_mtch->Fill(ThetaLabEl, PhiLabEl);

            histMigrationMatrixThLabEl->Fill(mc_ThetaLabEl, ThetaLabEl);
            histMigrationMatrixPhiLabEl->Fill(mc_PhiLabEl, PhiLabEl);
        }

        int vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;
            // PlCM=0, EhCM=0, Yh=0;
            // mc_PlCM=0, mc_EhCM=0, mc_Yh=0;

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                n_pions++;
                good_pion = true;

                // PlCM = (TMath::Sqrt(Pl2->at(i)) - Zh->at(i) * Nu * TMath::Sqrt(Q2 + Nu * Nu) / (Nu + kMassProton)) * (Nu + kMassProton) / W;
                // EhCM = (W * W + kMassPiPlus - kMassProton)/(2*W);

                // Yh = TMath::Log((EhCM + PlCM)/(EhCM - PlCM))/2.;

                hist1D_ThLab_reco->Fill(ThetaLab->at(i));
                hist1D_PhiLab_reco->Fill(PhiLab->at(i));

                hist2D_ThLab_PhiLab_reco->Fill(ThetaLab->at(i), PhiLab->at(i));
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;

                // mc_PlCM = (TMath::Sqrt(mc_Pl2->at(i)) - mc_Zh->at(i) * mc_Nu * TMath::Sqrt(mc_Q2 + mc_Nu * mc_Nu) / (mc_Nu + kMassProton)) * (mc_Nu + kMassProton) / mc_W;
                // mc_EhCM = (mc_W * mc_W + kMassPiPlus - kMassProton)/(2*mc_W);

                // mc_Yh = TMath::Log((mc_EhCM + mc_PlCM)/(mc_EhCM - mc_PlCM))/2.;

                hist1D_ThLab_gene->Fill(mc_ThetaLab->at(i));
                hist1D_PhiLab_gene->Fill(mc_PhiLab->at(i));

                hist2D_ThLab_PhiLab_gene->Fill(mc_ThetaLab->at(i), mc_PhiLab->at(i));
            }

            if (good_pion && good_pion_mc)
            {
                n_pions_match++;
                at_least_one_pion_mtch = true;

                hist1D_ThLab_mtch->Fill(ThetaLab->at(i));
                hist1D_PhiLab_mtch->Fill(PhiLab->at(i));

                hist2D_ThLab_PhiLab_mtch->Fill(ThetaLab->at(i), PhiLab->at(i));

                histMigrationMatrixThLab->Fill(mc_ThetaLab->at(i), ThetaLab->at(i));
                histMigrationMatrixPhiLab->Fill(mc_PhiLab->at(i), PhiLab->at(i));
            }
        }   // loop over tracks

        if (at_least_one_pion_mtch && good_electron && good_electron_mc)
        {
            hist1D_ThLabEl_mtch_Pi->Fill(ThetaLabEl);
            hist1D_PhiLabEl_mtch_Pi->Fill(PhiLabEl);

            hist2D_ThLabEl_PhiLabEl_mtch_Pi->Fill(ThetaLabEl, PhiLabEl);

            histMigrationMatrixThLabEl_Pi->Fill(mc_ThetaLabEl, ThetaLabEl);
            histMigrationMatrixPhiLabEl_Pi->Fill(mc_PhiLabEl, PhiLabEl);
        }
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " final state Pions matching generated." << std::endl;

    if (_isData)
    {
        hist1D_ThLabEl_mtch->Delete();
        hist1D_ThLabEl_gene->Delete();
        hist1D_PhiLabEl_mtch->Delete();
        hist1D_PhiLabEl_gene->Delete();
        hist1D_ThLab_mtch->Delete();
        hist1D_ThLab_gene->Delete();
        hist1D_PhiLab_mtch->Delete();
        hist1D_PhiLab_gene->Delete();

        hist2D_ThLabEl_PhiLabEl_mtch->Delete();
        hist2D_ThLabEl_PhiLabEl_gene->Delete();
        hist2D_ThLab_PhiLab_mtch->Delete();
        hist2D_ThLab_PhiLab_gene->Delete();

        histMigrationMatrixThLabEl->Delete();
        histMigrationMatrixPhiLabEl->Delete();
        histMigrationMatrixThLab->Delete();
        histMigrationMatrixPhiLab->Delete();

        hist1D_ThLabEl_mtch_Pi->Delete();
        hist1D_PhiLabEl_mtch_Pi->Delete();

        hist2D_ThLabEl_PhiLabEl_mtch_Pi->Delete();

        histMigrationMatrixThLabEl_Pi->Delete();
        histMigrationMatrixPhiLabEl_Pi->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

void Acceptance::Hist2D_PQVsLab()
{
    ActivateBranches();
    fChain->SetBranchStatus("PhiLabEl", 1);
    fChain->SetBranchStatus("ThetaLabEl", 1);
    fChain->SetBranchStatus("PhiLab", 1);
    fChain->SetBranchStatus("ThetaLab", 1);
    fChain->SetBranchStatus("ThetaPQ", 1);

    if (!_isData)
    {
        fChain->SetBranchStatus("mc_PhiLabEl", 1);
        fChain->SetBranchStatus("mc_ThetaLabEl", 1);
        fChain->SetBranchStatus("mc_PhiLab", 1);
        fChain->SetBranchStatus("mc_ThetaLab", 1);
        fChain->SetBranchStatus("mc_ThetaPQ", 1);
    }

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    CreateDir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/PQVsLab_%s_data.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/PQVsLab_%s_hsim.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");

    //// Define Histograms
    // Simple TH1
    TH1D* hist1D_ThetaPQ_reco = new TH1D("hist1D_ThetaPQ_reco", "Histogram 1D Reconstructed;#theta_{PQ};Counts", 360,0.0,180.0);
    TH1D* hist1D_ThetaPQ_mtch = new TH1D("hist1D_ThetaPQ_mtch", "Histogram 1D Reconstructed match;#theta_{PQ};Counts", 360,0.0,180.0);
    TH1D* hist1D_ThetaPQ_gene = new TH1D("hist1D_ThetaPQ_gene", "Histogram 1D Generated;#theta_{PQ};Counts", 360,0.0,180.0);

    // Reconstructed or data
    TH2D* hist2D_ThLabEl_PhiPQ_reco = new TH2D("hist2D_ThLabEl_PhiPQ_reco", "Two dimensional map Reco;#theta_{Lab} El;#phi_{PQ}" , 180,0.0,180.0, 360,-180.0,180.0);
    TH2D* hist2D_PhiLabEl_PhiPQ_reco = new TH2D("hist2D_PhiLabEl_PhiPQ_reco", "Two dimensional map Reco;#phi_{Lab} El;#phi_{PQ}" , 360,-30.0,330.0, 360,-180.0,180.0);
    TH2D* hist2D_ThLab_PhiPQ_reco = new TH2D("hist2D_ThLab_PhiPQ_reco", "Two dimensional map Reco;#theta_{Lab};#phi_{PQ}" , 180,0.0,180.0, 360,-180.0,180.0);
    TH2D* hist2D_PhiLab_PhiPQ_reco = new TH2D("hist2D_PhiLab_PhiPQ_reco", "Two dimensional map Reco;#phi_{Lab};#phi_{PQ}" , 360,-30.0,330.0, 360,-180.0,180.0);

    TH2D* hist2D_ThLabEl_ThPQ_reco = new TH2D("hist2D_ThLabEl_ThPQ_reco", "Two dimensional map Reco;#theta_{Lab} El;#theta_{PQ}" , 180,0.0,180.0, 180,0.0,180.0);
    TH2D* hist2D_PhiLabEl_ThPQ_reco = new TH2D("hist2D_PhiLabEl_ThPQ_reco", "Two dimensional map Reco;#phi_{Lab} El;#theta_{PQ}" , 360,-30.0,330.0, 180,0.0,180.0);
    TH2D* hist2D_ThLab_ThPQ_reco = new TH2D("hist2D_ThLab_ThPQ_reco", "Two dimensional map Reco;#theta_{Lab};#theta_{PQ}" , 180,0.0,180.0, 180,0.0,180.0);
    TH2D* hist2D_PhiLab_ThPQ_reco = new TH2D("hist2D_PhiLab_ThPQ_reco", "Two dimensional map Reco;#phi_{Lab};#theta_{PQ}" , 360,-30.0,330.0, 180,0.0,180.0);

    // Reconstructed match
    TH2D* hist2D_ThLabEl_PhiPQ_mtch = new TH2D("hist2D_ThLabEl_PhiPQ_mtch", "Two dimensional map Match;#theta_{Lab} El;#phi_{PQ}" , 180,0.0,180.0, 360,-180.0,180.0);
    TH2D* hist2D_PhiLabEl_PhiPQ_mtch = new TH2D("hist2D_PhiLabEl_PhiPQ_mtch", "Two dimensional map Match;#phi_{Lab} El;#phi_{PQ}" , 360,-30.0,330.0, 360,-180.0,180.0);
    TH2D* hist2D_ThLab_PhiPQ_mtch = new TH2D("hist2D_ThLab_PhiPQ_mtch", "Two dimensional map Match;#theta_{Lab};#phi_{PQ}" , 180,0.0,180.0, 360,-180.0,180.0);
    TH2D* hist2D_PhiLab_PhiPQ_mtch = new TH2D("hist2D_PhiLab_PhiPQ_mtch", "Two dimensional map Match;#phi_{Lab};#phi_{PQ}" , 360,-30.0,330.0, 360,-180.0,180.0);

    TH2D* hist2D_ThLabEl_ThPQ_mtch = new TH2D("hist2D_ThLabEl_ThPQ_mtch", "Two dimensional map Match;#theta_{Lab} El;#theta_{PQ}" , 180,0.0,180.0, 180,0.0,180.0);
    TH2D* hist2D_PhiLabEl_ThPQ_mtch = new TH2D("hist2D_PhiLabEl_ThPQ_mtch", "Two dimensional map Match;#phi_{Lab} El;#theta_{PQ}" , 360,-30.0,330.0, 180,0.0,180.0);
    TH2D* hist2D_ThLab_ThPQ_mtch = new TH2D("hist2D_ThLab_ThPQ_mtch", "Two dimensional map Match;#theta_{Lab};#theta_{PQ}" , 180,0.0,180.0, 180,0.0,180.0);
    TH2D* hist2D_PhiLab_ThPQ_mtch = new TH2D("hist2D_PhiLab_ThPQ_mtch", "Two dimensional map Match;#phi_{Lab};#theta_{PQ}" , 360,-30.0,330.0, 180,0.0,180.0);

    // Generated (MC)
    TH2D* hist2D_ThLabEl_PhiPQ_gene = new TH2D("hist2D_ThLabEl_PhiPQ_gene", "Two dimensional map Generated;#theta_{Lab} El;#phi_{PQ}" , 180,0.0,180.0, 360,-180.0,180.0);
    TH2D* hist2D_PhiLabEl_PhiPQ_gene = new TH2D("hist2D_PhiLabEl_PhiPQ_gene", "Two dimensional map Generated;#phi_{Lab} El;#phi_{PQ}" , 360,-30.0,330.0, 360,-180.0,180.0);
    TH2D* hist2D_ThLab_PhiPQ_gene = new TH2D("hist2D_ThLab_PhiPQ_gene", "Two dimensional map Generated;#theta_{Lab};#phi_{PQ}" , 180,0.0,180.0, 360,-180.0,180.0);
    TH2D* hist2D_PhiLab_PhiPQ_gene = new TH2D("hist2D_PhiLab_PhiPQ_gene", "Two dimensional map Generated;#phi_{Lab};#phi_{PQ}" , 360,-30.0,330.0, 360,-180.0,180.0);

    TH2D* hist2D_ThLabEl_ThPQ_gene = new TH2D("hist2D_ThLabEl_ThPQ_gene", "Two dimensional map Generated;#theta_{Lab} El;#theta_{PQ}" , 180,0.0,180.0, 180,0.0,180.0);
    TH2D* hist2D_PhiLabEl_ThPQ_gene = new TH2D("hist2D_PhiLabEl_ThPQ_gene", "Two dimensional map Generated;#phi_{Lab} El;#theta_{PQ}" , 360,-30.0,330.0, 180,0.0,180.0);
    TH2D* hist2D_ThLab_ThPQ_gene = new TH2D("hist2D_ThLab_ThPQ_gene", "Two dimensional map Generated;#theta_{Lab};#theta_{PQ}" , 180,0.0,180.0, 180,0.0,180.0);
    TH2D* hist2D_PhiLab_ThPQ_gene = new TH2D("hist2D_PhiLab_ThPQ_gene", "Two dimensional map Generated;#phi_{Lab};#theta_{PQ}" , 360,-30.0,330.0, 180,0.0,180.0);

    // Bin migration
    TH2D* histMigrationMatrixThetaPQ = new TH2D("histMigrationMatrixThetaPQ", "Migration #theta_{PQ};True #theta_{PQ}; Reco #theta_{PQ}", 180,0.0,180.0, 180,0.0,180.0);

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    unsigned int entries_to_process = nentries;
    int n_pions = 0, n_pions_mc = 0, n_pions_match = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;
    // bool at_least_one_pion_mtch = false;

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
        // at_least_one_pion_mtch = false;

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
        }

        if (!_isData && GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
        }

        // if (good_electron && good_electron_mc)
        // {
        // }

        int vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                n_pions++;
                good_pion = true;

                hist1D_ThetaPQ_reco->Fill(ThetaPQ->at(i));

                hist2D_ThLabEl_PhiPQ_reco->Fill(ThetaLabEl, PhiPQ->at(i));
                hist2D_PhiLabEl_PhiPQ_reco->Fill(PhiLabEl, PhiPQ->at(i));
                hist2D_ThLab_PhiPQ_reco->Fill(ThetaLab->at(i), PhiPQ->at(i));
                hist2D_PhiLab_PhiPQ_reco->Fill(PhiLab->at(i), PhiPQ->at(i));

                hist2D_ThLabEl_ThPQ_reco->Fill(ThetaLabEl, ThetaPQ->at(i));
                hist2D_PhiLabEl_ThPQ_reco->Fill(PhiLabEl, ThetaPQ->at(i));
                hist2D_ThLab_ThPQ_reco->Fill(ThetaLab->at(i), ThetaPQ->at(i));
                hist2D_PhiLab_ThPQ_reco->Fill(PhiLab->at(i), ThetaPQ->at(i));
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
                n_pions_mc++;

                hist1D_ThetaPQ_gene->Fill(mc_ThetaPQ->at(i));

                hist2D_ThLabEl_PhiPQ_gene->Fill(mc_ThetaLabEl, mc_PhiPQ->at(i));
                hist2D_PhiLabEl_PhiPQ_gene->Fill(mc_PhiLabEl, mc_PhiPQ->at(i));
                hist2D_ThLab_PhiPQ_gene->Fill(mc_ThetaLab->at(i), mc_PhiPQ->at(i));
                hist2D_PhiLab_PhiPQ_gene->Fill(mc_PhiLab->at(i), mc_PhiPQ->at(i));

                hist2D_ThLabEl_ThPQ_gene->Fill(mc_ThetaLabEl, mc_ThetaPQ->at(i));
                hist2D_PhiLabEl_ThPQ_gene->Fill(mc_PhiLabEl, mc_ThetaPQ->at(i));
                hist2D_ThLab_ThPQ_gene->Fill(mc_ThetaLab->at(i), mc_ThetaPQ->at(i));
                hist2D_PhiLab_ThPQ_gene->Fill(mc_PhiLab->at(i), mc_ThetaPQ->at(i));
            }

            if (good_pion && good_pion_mc)
            {
                n_pions_match++;
                // at_least_one_pion_mtch = true;

                hist1D_ThetaPQ_mtch->Fill(ThetaPQ->at(i));

                hist2D_ThLabEl_PhiPQ_mtch->Fill(ThetaLabEl, PhiPQ->at(i));
                hist2D_PhiLabEl_PhiPQ_mtch->Fill(PhiLabEl, PhiPQ->at(i));
                hist2D_ThLab_PhiPQ_mtch->Fill(ThetaLab->at(i), PhiPQ->at(i));
                hist2D_PhiLab_PhiPQ_mtch->Fill(PhiLab->at(i), PhiPQ->at(i));

                hist2D_ThLabEl_ThPQ_mtch->Fill(ThetaLabEl, ThetaPQ->at(i));
                hist2D_PhiLabEl_ThPQ_mtch->Fill(PhiLabEl, ThetaPQ->at(i));
                hist2D_ThLab_ThPQ_mtch->Fill(ThetaLab->at(i), ThetaPQ->at(i));
                hist2D_PhiLab_ThPQ_mtch->Fill(PhiLab->at(i), ThetaPQ->at(i));


                histMigrationMatrixThetaPQ->Fill(mc_ThetaPQ->at(i), ThetaPQ->at(i));
            }
        }   // loop over tracks
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " matching pions out of " << n_pions_mc << " generated." << std::endl;

    if (_isData)
    {
        hist1D_ThetaPQ_gene->Delete();

        hist2D_ThLabEl_PhiPQ_gene->Delete();
        hist2D_PhiLabEl_PhiPQ_gene->Delete();
        hist2D_ThLab_PhiPQ_gene->Delete();
        hist2D_PhiLab_PhiPQ_gene->Delete();

        hist2D_ThLabEl_ThPQ_gene->Delete();
        hist2D_PhiLabEl_ThPQ_gene->Delete();
        hist2D_ThLab_ThPQ_gene->Delete();
        hist2D_PhiLab_ThPQ_gene->Delete();

        hist1D_ThetaPQ_mtch->Delete();

        hist2D_ThLabEl_PhiPQ_mtch->Delete();
        hist2D_PhiLabEl_PhiPQ_mtch->Delete();
        hist2D_ThLab_PhiPQ_mtch->Delete();
        hist2D_PhiLab_PhiPQ_mtch->Delete();

        hist2D_ThLabEl_ThPQ_mtch->Delete();
        hist2D_PhiLabEl_ThPQ_mtch->Delete();
        hist2D_ThLab_ThPQ_mtch->Delete();
        hist2D_PhiLab_ThPQ_mtch->Delete();

        histMigrationMatrixThetaPQ->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

void Acceptance::Hist2D_PhiPQVsSector()
{
    ActivateBranches();
    fChain->SetBranchStatus("SectorEl", 1);
    fChain->SetBranchStatus("Sector", 1);
    fChain->SetBranchStatus("ThetaPQ", 1);

    if (!_isData)
    {
        fChain->SetBranchStatus("mc_SectorEl", 1);
        fChain->SetBranchStatus("mc_Sector", 1);
        fChain->SetBranchStatus("mc_ThetaPQ", 1);
    }

    std::string acc_folder = "../output/JLab_cluster/Acceptance" + getAccFoldNameExt();
    if (!FileExists(Form("%s/Acceptance_%s.root", acc_folder.c_str(), getAccFileName().c_str())))
    {
        std::cout << "Acceptance file not found in JLab_cluster folder." << std::endl;
        exit(0);
    }
    TFile *facc = TFile::Open(Form("%s/Acceptance_%s.root", acc_folder.c_str(), getAccFileName().c_str()), "READ");
    THnSparse *histAcc = (THnSparse*)facc->Get("histAcc_Reconstru");

    setBinningType(-1);
    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    CreateDir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/PQVsSector_%s_data.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/PQVsSector_%s_hsim.root", h2d_folder.c_str(), _nameFormatted.c_str()), "RECREATE");

    //// Define Histograms
    // Simple TH1
    TH1D* hist1D_Sector_reco = new TH1D("hist1D_Sector_reco", "Histogram 1D Reconstructed;Sector;Counts", 6,0,6);
    TH1D* hist1D_Sector_mtch = new TH1D("hist1D_Sector_mtch", "Histogram 1D Reconstructed match;Sector;Counts", 6,0,6);
    TH1D* hist1D_Sector_gene = new TH1D("hist1D_Sector_gene", "Histogram 1D Generated;Sector;Counts", 6,0,6);

    TH1D* hist1D_SectorEl_reco = new TH1D("hist1D_SectorEl_reco", "Histogram 1D Reconstructed;SectorEl;Counts", 6,0,6);
    TH1D* hist1D_SectorEl_mtch = new TH1D("hist1D_SectorEl_mtch", "Histogram 1D Reconstructed match;SectorEl;Counts", 6,0,6);
    TH1D* hist1D_SectorEl_gene = new TH1D("hist1D_SectorEl_gene", "Histogram 1D Generated;SectorEl;Counts", 6,0,6);

    TH1D* hist1D_SectorEl_mtch_Pi = new TH1D("hist1D_SectorEl_mtch_Pi", "Histogram 1D Reconstructed match Pi;SectorEl;Counts", 6,0,6);

    // Reconstructed or data
    TH2D* hist2D_Sector_PhiPQ_reco = new TH2D("hist2D_Sector_PhiPQ_reco", "Two dimensional map Reco;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_reco = new TH2D("hist2D_SectorEl_PhiPQ_reco", "Two dimensional map Reco;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_reco = new TH2D("hist2D_Sector_ThPQ_reco", "Two dimensional map Reco;Sector;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_reco = new TH2D("hist2D_SectorEl_ThPQ_reco", "Two dimensional map Reco;SectorEl;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_PhiPQ_recoAcc = new TH2D("hist2D_Sector_PhiPQ_recoAcc", "Two dimensional map Reco Acc;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_recoAcc = new TH2D("hist2D_SectorEl_PhiPQ_recoAcc", "Two dimensional map Reco Acc;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_recoAcc = new TH2D("hist2D_Sector_ThPQ_recoAcc", "Two dimensional map Reco Acc;Sector;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_recoAcc = new TH2D("hist2D_SectorEl_ThPQ_recoAcc", "Two dimensional map Reco Acc;SectorEl;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);

    // Reconstructed match
    TH2D* hist2D_Sector_PhiPQ_mtch = new TH2D("hist2D_Sector_PhiPQ_mtch", "Two dimensional map Match;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_mtch = new TH2D("hist2D_SectorEl_PhiPQ_mtch", "Two dimensional map Match;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_mtch = new TH2D("hist2D_Sector_ThPQ_mtch", "Two dimensional map Match;Sector;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_mtch = new TH2D("hist2D_SectorEl_ThPQ_mtch", "Two dimensional map Match;SectorEl;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_PhiPQ_mtchAcc = new TH2D("hist2D_Sector_PhiPQ_mtchAcc", "Two dimensional map Match Acc;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_mtchAcc = new TH2D("hist2D_SectorEl_PhiPQ_mtchAcc", "Two dimensional map Match Acc;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_mtchAcc = new TH2D("hist2D_Sector_ThPQ_mtchAcc", "Two dimensional map Match Acc;Sector;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_mtchAcc = new TH2D("hist2D_SectorEl_ThPQ_mtchAcc", "Two dimensional map Match Acc;SectorEl;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);

    // Generated (MC)
    TH2D* hist2D_Sector_PhiPQ_gene = new TH2D("hist2D_Sector_PhiPQ_gene", "Two dimensional map Generated;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_gene = new TH2D("hist2D_SectorEl_PhiPQ_gene", "Two dimensional map Generated;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_gene = new TH2D("hist2D_Sector_ThPQ_gene", "Two dimensional map Generated;Sector;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_gene = new TH2D("hist2D_SectorEl_ThPQ_gene", "Two dimensional map Generated;SectorEl;#theta_{PQ}" , 6,0,6, 360,-180.0,180.0);

    // Bin migration
    TH2D* histMigrationMatrixSector = new TH2D("histMigrationMatrixSector", "Migration Sector;True Sector; Reco Sector", 6,0,6, 6,0,6);
    TH2D* histMigrationMatrixSectorEl = new TH2D("histMigrationMatrixSectorEl", "Migration SectorEl;True SectorEl; Reco SectorEl", 6,0,6, 6,0,6);
    TH2D* histMigrationMatrixSectorEl_Pi = new TH2D("histMigrationMatrixSectorEl_Pi", "Migration SectorEl Match Pi;True SectorEl; Reco SectorEl", 6,0,6, 6,0,6);

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    unsigned int entries_to_process = nentries;
    std::vector<double> binKinVars;
    int n_pions = 0, n_pions_mc = 0, n_pions_match = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;
    bool at_least_one_pion_mtch = false;

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
        at_least_one_pion_mtch = false;

        if (GoodElectron(ientry, DISLimits))
        {
            good_electron = true;
            hist1D_SectorEl_reco->Fill(SectorEl);
        }

        if (!_isData && GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
            hist1D_SectorEl_gene->Fill(mc_SectorEl);
        }

        if (good_electron && good_electron_mc)
        {
            hist1D_SectorEl_mtch->Fill(SectorEl);

            histMigrationMatrixSectorEl->Fill(mc_SectorEl, SectorEl);
        }

        int vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                good_pion = true;
                n_pions++;

                hist1D_Sector_reco->Fill(Sector->at(i));

                hist2D_Sector_PhiPQ_reco->Fill(Sector->at(i), PhiPQ->at(i));
                hist2D_SectorEl_PhiPQ_reco->Fill(SectorEl, PhiPQ->at(i));

                hist2D_Sector_ThPQ_reco->Fill(Sector->at(i), ThetaPQ->at(i));
                hist2D_SectorEl_ThPQ_reco->Fill(SectorEl, ThetaPQ->at(i));

                binKinVars = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};

                pair<double, double> acc_val = GetCorrectValue(binKinVars, histAcc);
                if (acc_val.first != 0 && acc_val.second != 0)
                {
                    double weight = 1./acc_val.first;

                    hist2D_Sector_PhiPQ_recoAcc->Fill(Sector->at(i), PhiPQ->at(i), weight);
                    hist2D_SectorEl_PhiPQ_recoAcc->Fill(SectorEl, PhiPQ->at(i), weight);

                    hist2D_Sector_ThPQ_recoAcc->Fill(Sector->at(i), ThetaPQ->at(i), weight);
                    hist2D_SectorEl_ThPQ_recoAcc->Fill(SectorEl, ThetaPQ->at(i), weight);
                }
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
                n_pions_mc++;

                hist1D_Sector_gene->Fill(mc_Sector->at(i));

                hist2D_Sector_PhiPQ_gene->Fill(mc_Sector->at(i), mc_PhiPQ->at(i));
                hist2D_SectorEl_PhiPQ_gene->Fill(mc_SectorEl, mc_PhiPQ->at(i));

                hist2D_Sector_ThPQ_gene->Fill(mc_Sector->at(i), mc_ThetaPQ->at(i));
                hist2D_SectorEl_ThPQ_gene->Fill(mc_SectorEl, mc_ThetaPQ->at(i));
            }

            if (good_pion && good_pion_mc)
            {
                at_least_one_pion_mtch = true;
                n_pions_match++;

                hist1D_Sector_mtch->Fill(Sector->at(i));

                hist2D_Sector_PhiPQ_mtch->Fill(Sector->at(i), PhiPQ->at(i));
                hist2D_SectorEl_PhiPQ_mtch->Fill(SectorEl, PhiPQ->at(i));

                hist2D_Sector_ThPQ_mtch->Fill(Sector->at(i), ThetaPQ->at(i));
                hist2D_SectorEl_ThPQ_mtch->Fill(SectorEl, ThetaPQ->at(i));

                binKinVars = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};

                pair<double, double> acc_val = GetCorrectValue(binKinVars, histAcc);
                if (acc_val.first != 0 && acc_val.second != 0)
                {
                    double weight = 1./acc_val.first;

                    hist2D_Sector_PhiPQ_mtchAcc->Fill(Sector->at(i), PhiPQ->at(i), weight);
                    hist2D_SectorEl_PhiPQ_mtchAcc->Fill(SectorEl, PhiPQ->at(i), weight);

                    hist2D_Sector_ThPQ_mtchAcc->Fill(Sector->at(i), ThetaPQ->at(i), weight);
                    hist2D_SectorEl_ThPQ_mtchAcc->Fill(SectorEl, ThetaPQ->at(i), weight);
                }

                histMigrationMatrixSector->Fill(mc_Sector->at(i), Sector->at(i));
            }
        }   // loop over tracks

        if (at_least_one_pion_mtch && good_electron && good_electron_mc)
        {
            hist1D_SectorEl_mtch_Pi->Fill(SectorEl);

            histMigrationMatrixSectorEl_Pi->Fill(mc_SectorEl, SectorEl);
        }
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " matching pions out of " << n_pions_mc << " generated." << std::endl;

    if (_isData)
    {
        hist1D_Sector_mtch->Delete();
        hist1D_Sector_gene->Delete();

        hist1D_SectorEl_mtch->Delete();
        hist1D_SectorEl_gene->Delete();

        hist1D_SectorEl_mtch_Pi->Delete();

        hist2D_Sector_PhiPQ_mtch->Delete();
        hist2D_SectorEl_PhiPQ_mtch->Delete();
        hist2D_Sector_ThPQ_mtch->Delete();
        hist2D_SectorEl_ThPQ_mtch->Delete();

        hist2D_Sector_PhiPQ_mtchAcc->Delete();
        hist2D_SectorEl_PhiPQ_mtchAcc->Delete();
        hist2D_Sector_ThPQ_mtchAcc->Delete();
        hist2D_SectorEl_ThPQ_mtchAcc->Delete();

        hist2D_Sector_PhiPQ_gene->Delete();
        hist2D_SectorEl_PhiPQ_gene->Delete();
        hist2D_Sector_ThPQ_gene->Delete();
        hist2D_SectorEl_ThPQ_gene->Delete();

        histMigrationMatrixSector->Delete();
        histMigrationMatrixSectorEl->Delete();
        histMigrationMatrixSectorEl_Pi->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
    facc->Close();
}
