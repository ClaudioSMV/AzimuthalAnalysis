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

using namespace BINNING;

inline float DEG2RAD(float x) {
    return 0.017453293 * x;
}

void Acceptance::activateBranches() {
    fChain->SetBranchStatus("*",0); // Deactivate all branches
    std::vector<string> activeBranches = {
        "TargType", "Q2", "Nu", "Xb", "Yb", "W", "vyec", "Zh", "Pt2", "PhiPQ",
        "pid", "Xf", // "Nphe"
    };
    std::vector<string> activeBranches_mc = {
        "mc_TargType", "mc_Q2", "mc_Nu", "mc_Xb", "mc_Yb", "mc_W", "mc_Zh", "mc_Pt2",
        "mc_PhiPQ", "mc_pid", "mc_Xf",
    };

    //  Enable branches per cut
    /////////////////////////////

    if (cutIsUsed("DS") || cutIsUsed("BS")) {
        activeBranches.push_back("SectorEl");
        activeBranches.push_back("Sector");
        activeBranches_mc.push_back("mc_SectorEl");
        activeBranches_mc.push_back("mc_Sector");
    }
    if (cutIsUsed("PF")) {
        activeBranches.push_back("Sector");
        activeBranches.push_back("P");
        activeBranches.push_back("ThetaLab");
        activeBranches.push_back("PhiLab");
        activeBranches_mc.push_back("mc_Sector");
        activeBranches_mc.push_back("mc_P");
        activeBranches_mc.push_back("mc_ThetaLab");
        activeBranches_mc.push_back("mc_PhiLab");
    }
    if (cutIsUsed("MM") || cutIsUsed("M2")) {
        activeBranches.push_back("P");
        activeBranches.push_back("Nphe");
    }
    if (cutIsUsed("Pe")) {
        activeBranches.push_back("NpheEl");
        activeBranches.push_back("Nphe");
    }

    for (const auto &activeBranch : activeBranches)
        fChain->SetBranchStatus(activeBranch.c_str(), 1);

    if (!_isData) {
        for (const auto &activeBranch : activeBranches_mc)
            fChain->SetBranchStatus(activeBranch.c_str(), 1);
    }
    // Save binning info in .py file to use in python macros later!
    write_python_file(BINNING::Bin_List);
}

void Acceptance::Loop() {
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

    activateBranches();

    std::string folderName;
    std::string fileName;
    if (!_isClosureTest) {
        folderName = "../output/localJul2025/Acceptance" +
            formatCutsInName(_cutList);
        fileName = Form("Acceptance_%s", _infoTag_Acceptance.c_str());
    }
    else {
        folderName = "../output/localJul2025/ClosureTest" +
            std::to_string(_fractionClosureTest) + "p" + formatCutsInName(_cutList);
        fileName = Form("AccCT_%s", _infoTag_Acceptance.c_str());
    }
    create_Dir(folderName);
    TFile *fout =
        TFile::Open(Form("%s/%s.root", folderName.c_str(), fileName.c_str()), "RECREATE");

    std::cout << "\n\nBeginning Acceptance calculations for ";
    std::cout << _nameTarget << " target\n" << std::endl;

    //////////////////////////////////////////////////////////////////////////////////////
    //  Histograms definition
    //////////////////////////////////////////////////////////////////////////////////////

    // One-dimensional efficiency
    // TEfficiency* efficiency_Q2 = new TEfficiency("efficiency_Q2",
    //     ";Q^{2} (GeV^{2});Reconstruction efficiency", 20, _minimum["Q2"], _maximum["Q2"]);
    // TEfficiency* efficiency_Nu = new TEfficiency("efficiency_Nu",
    //     ";#nu (GeV);Reconstruction efficiency", 20, _minimum["Nu"], _maximum["Nu"]);
    TEfficiency* efficiency_Zh = new TEfficiency("efficiency_Zh",
        ";Z_{h};Reconstruction efficiency", 20, _minimum["Zh"], _maximum["Zh"]);
    TEfficiency* efficiency_Pt2 = new TEfficiency("efficiency_Pt2",
        ";p_{T}^{2} (GeV^{2});Reconstruction efficiency", 20, _minimum["Pt2"], _maximum["Pt2"]);
    TEfficiency* efficiency_PhiPQ = new TEfficiency("efficiency_PhiPQ",
        ";#phi_{PQ} (deg);Reconstruction efficiency", 60, _minimum["PhiPQ"], _maximum["PhiPQ"]);

    // One-dimensional resolution
    TH1F* resolution_Q2 = new TH1F("resolution_Q2", ";Q^{2}-mc_Q^{2};Counts", 64, -0.3, 0.3);
    TH1F* resolution_Nu = new TH1F("resolution_Nu", ";#nu-mc_#nu;Counts", 64, -0.3, 0.3);
    TH1F* resolution_Xb = new TH1F("resolution_Xb", ";X_{b}-mc_X_{b};Counts", 64, -0.3, 0.3);
    TH1F* resolution_Zh = new TH1F("resolution_Zh", ";z_{h}-mc_z_{h};Counts", 64, -0.15, 0.15);
    TH1F* resolution_Pt2 = new TH1F("resolution_Pt2", ";p_{T}^{2}-mc_p_{T}^{2};Counts", 64, -0.15, 0.15);
    TH1F* resolution_PhiPQ = new TH1F("resolution_PhiPQ", ";#phi_{PQ}-mc_#phi_{PQ};Counts", 80, -4.0, 4.0);

    // Bin migration map
    TH2F* binMigrationMap_Q2 = new TH2F("binMigrationMap_Q2", ";True Q^{2}; Reco Q^{2}",
        50, _minimum["Q2"], _maximum["Q2"], 50, _minimum["Q2"], _maximum["Q2"]);
    TH2F* binMigrationMap_Zh = new TH2F("binMigrationMap_Zh", ";True Z_{h}; Reco Z_{h}",
        50, _minimum["Zh"], _maximum["Zh"], 50, _minimum["Zh"], _maximum["Zh"]);
    TH2F* binMigrationMap_Pt2 = new TH2F("binMigrationMap_Pt2", ";True p_{T}^{2} (GeV^{2});Reco p_{T}^{2} (GeV^{2})",
        50, _minimum["Pt2"], _maximum["Pt2"], 50, _minimum["Pt2"], _maximum["Pt2"]);
    TH2F* binMigrationMap_PhiPQ = new TH2F("binMigrationMap_PhiPQ", ";True #phi_{PQ} (deg);Reco #phi_{PQ} (deg)",
        120, _minimum["PhiPQ"], _maximum["PhiPQ"], 120, _minimum["PhiPQ"], _maximum["PhiPQ"]);
    double var2_min = (_minimum.count("Nu"))? _minimum["Nu"] : _minimum["Xb"];
    double var2_max = (_maximum.count("Nu"))? _maximum["Nu"] : _maximum["Xb"];
    TH2F* binMigrationMap_Nu = new TH2F("binMigrationMap_Nu", ";True #nu; Reco #nu",
            50, var2_min, var2_max, 50, var2_min, var2_max);
    TH2F* binMigrationMap_Xb = new TH2F("binMigrationMap_Xb", ";True X_{b}; Reco X_{b}",
            50, var2_min, var2_max, 50, var2_min, var2_max);

    // THnSparse
    std::vector<std::vector<double>> ordered_limits =
        map_to_vector_in_order<std::vector<double>>(_limitsMap, _variables);
    std::vector<double> ordered_min =
        map_to_vector_in_order<double>(_minimum, _variables);
    std::vector<double> ordered_max =
        map_to_vector_in_order<double>(_maximum, _variables);
    // Generated: Good Generated (Doesn't need Reco), filled with Generated kinematic vars
    // Reconstructed: Good Reco (Doesn't need Generated), filled with Reco kinematic vars
    // Match_GenVars: Good Reco & Generated, filled with Generated kinematic vars
    // Match_RecoVars: Good Reco & Generated, filled with Reco kinematic vars
    THnSparse* hGenerated = create_THnSparse("hGenerated", ordered_limits,
        ordered_min, ordered_max, NULL, "True");
    THnSparse* hReconstructed = create_THnSparse("hReconstructed", ordered_limits,
        ordered_min, ordered_max, NULL, "Reconstructed only");
    THnSparse* hMatch_GenVars = create_THnSparse("hMatch_GenVars", ordered_limits,
        ordered_min, ordered_max, NULL, "Good reconstructed with mc_vars");
    THnSparse* hMatch_RecoVars = create_THnSparse("hMatch_RecoVars", ordered_limits,
        ordered_min, ordered_max, NULL, "Good reconstructed with reco_vars");

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    unsigned int entries_to_process = nentries;
    if (_isClosureTest)
        entries_to_process *= _fractionClosureTest / 100.;

    auto counterMap = create_MapCounter();
    counterMap["Total_entries"] = nentries;
    for (unsigned int jentry = 0; jentry < entries_to_process; jentry++) {
        if (jentry % 1000000 == 0) {
            printf("Processing entry %10u out of %10llu, progress at %3.2f%%\n", jentry,
                nentries, 100. * (double)jentry / entries_to_process);
        }

        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        // if (Cut(ientry) < 0) continue;

        // Clean variables
        bool good_electron_gen = false;
        bool good_electron_rec = false;
        int n_pion_gen = 0;
        int n_pion_rec = 0;

        if (GoodElectron_MC(ientry)) {
            good_electron_gen = true;
            counterMap["Gen_GoodElectron"]++;
        }
        else {
            counterMap["Gen_GoodElectronNOT"]++;
            if (mc_TargType != _cut_TargType)
                counterMap["Gen_WrongTargType"]++;
            else
                counterMap["Gen_OutDISRange"]++;
        }

        if (GoodElectron(ientry)) {
            good_electron_rec = true;
            counterMap["Reco_GoodElectron"]++;
        }
        else {
            counterMap["Reco_GoodElectronNOT"]++;
            if (TargType != _cut_TargType)
                counterMap["Reco_WrongTargType"]++;
            else if ((vyec < -1.4) || (1.4 < vyec))
                counterMap["Reco_OutVertexY"]++;
            else
                counterMap["Reco_OutDISRange"]++;
        }

        if (good_electron_gen && good_electron_rec)
            counterMap["Total_MatchElectrons"]++;

        if (PhiPQ->size() != mc_PhiPQ->size()) {
            counterMap["Total_DifferentVectorSize"]++;
            continue;
        }

		for (int i = 0; i < (int)PhiPQ->size(); i++) {
            // Clean variables
            bool good_pion_gen = false;
            bool good_pion_rec = false;
            // inclusive_count++;

            if (good_electron_gen && GoodPiPlus_MC(ientry, i)) {
                good_pion_gen = true;
                counterMap["Gen_GoodPiPlus"]++;
                n_pion_gen++;
                if (n_pion_gen == 1)
                    counterMap["Gen_Pi+Single"]++;
                else if (n_pion_gen == 2)
                    counterMap["Gen_Pi+Two"]++;
                else
                    counterMap["Gen_Pi+Three+"]++;
            }
            else
                counterMap["Gen_GoodPiPlusNOT"]++;
            
            if (good_electron_rec && GoodPiPlus(ientry, i)) {
                good_pion_rec = true;
                counterMap["Reco_GoodPiPlus"]++;
                n_pion_rec++;
                if (n_pion_rec == 1)
                    counterMap["Reco_Pi+Single"]++;
                else if (n_pion_rec == 2)
                    counterMap["Reco_Pi+Two"]++;
                else
                    counterMap["Reco_Pi+Three+"]++;
            }
            else
                counterMap["Reco_GoodPiPlusNOT"]++;

            if (!good_pion_gen && !good_pion_rec)
                continue;

            if (good_pion_gen && good_pion_rec)
                counterMap["Total_MatchPiPlus"]++;

            double bin_gen[] = {mc_Q2, 0, mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i)};
            bin_gen[1] = (_limitsMap.count("Nu"))? mc_Nu : mc_Xb;
            double bin_rec[] = {Q2, 0, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};
            bin_rec[1] = (_limitsMap.count("Nu"))? Nu : Xb;

            if (good_pion_gen)
                hGenerated->Fill(bin_gen);

            if (good_pion_rec)
                hReconstructed->Fill(bin_rec);

            if (good_pion_gen && good_pion_rec) {
                binMigrationMap_Zh->Fill(mc_Zh->at(i), Zh->at(i));
                binMigrationMap_Pt2->Fill(mc_Pt2->at(i), Pt2->at(i));
                binMigrationMap_PhiPQ->Fill(mc_PhiPQ->at(i), PhiPQ->at(i));

                resolution_Zh->Fill(Zh->at(i) - mc_Zh->at(i));
                resolution_Pt2->Fill(Pt2->at(i) - mc_Pt2->at(i));

                // Save PhiPQ considering that it's a cyclic variable
                double delta_PhiPQ = PhiPQ->at(i) - mc_PhiPQ->at(i);
                if (abs(delta_PhiPQ) > 350.)
                    if (delta_PhiPQ > 0)
                        resolution_PhiPQ->Fill(delta_PhiPQ - 360);
                    else
                        resolution_PhiPQ->Fill(delta_PhiPQ + 360);
                else
                    resolution_PhiPQ->Fill(delta_PhiPQ);

                hMatch_GenVars->Fill(bin_gen);
                hMatch_RecoVars->Fill(bin_rec);
            }

            efficiency_Zh->Fill((good_pion_gen && good_pion_rec), mc_Zh->at(i));
            efficiency_Pt2->Fill((good_pion_gen && good_pion_rec), mc_Pt2->at(i));
            efficiency_PhiPQ->Fill((good_pion_gen && good_pion_rec), mc_PhiPQ->at(i));
        }  // loop over tracks (particles associated to scattered electron)

        if ((n_pion_gen >= 1) && (n_pion_rec >= 1)) {
            binMigrationMap_Q2->Fill(mc_Q2, Q2);
            resolution_Q2->Fill(Q2 - mc_Q2);
            if (_limitsMap.count("Nu")) {
                binMigrationMap_Nu->Fill(mc_Nu, Nu);
                resolution_Nu->Fill(Nu - mc_Nu);
            }
            else if (_limitsMap.count("Xb")) {
                binMigrationMap_Xb->Fill(mc_Xb, Xb);
                resolution_Xb->Fill(Xb - mc_Xb);
            }
        }
    }  // loop over entries (scattered electron)

    // Acceptance
    THnSparse* Acceptance_Reconstructed =
        (THnSparse*)hReconstructed->Clone("Acceptance_Reconstructed");
    Acceptance_Reconstructed->Divide(hReconstructed, hGenerated, 1, 1, "B");
    THnSparse* Acceptance_Match_GenVars =
        (THnSparse*)hMatch_GenVars->Clone( "Acceptance_Match_GenVars");
    Acceptance_Match_GenVars->Divide(hMatch_GenVars, hGenerated, 1, 1, "B");
    THnSparse* Acceptance_Match_RecoVars =
        (THnSparse*)hMatch_RecoVars->Clone("Acceptance_Match_RecoVars");
    Acceptance_Match_RecoVars->Divide(hMatch_RecoVars, hGenerated, 1, 1, "B");

    // Summary table
    print_EventSummary(Form("%s/Summary_%s.txt", folderName.c_str(),
        _infoTag_Acceptance.c_str()), counterMap);

    if (!_limitsMap.count("Nu")) {
        binMigrationMap_Nu->Delete();
        resolution_Nu->Delete();
    }
    else if (!_limitsMap.count("Xb")) {
        binMigrationMap_Xb->Delete();
        resolution_Xb->Delete();
    }

    print_BinsFilled(Acceptance_Reconstructed);
    print_BinsFilled(Acceptance_Match_GenVars);
    print_BinsFilled(Acceptance_Match_RecoVars);

    hGenerated->Write();
    hReconstructed->Write();
    hMatch_GenVars->Write();
    hMatch_RecoVars->Write();

    Acceptance_Reconstructed->Write();
    Acceptance_Match_GenVars->Write();
    Acceptance_Match_RecoVars->Write();

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

void Acceptance::Correction() {
    activateBranches();

    std::string folderName;
    std::string fileName;
    // Opening Acceptance file
    folderName = "../output/localJul2025/Acceptance" + formatCutsInName(_cutList);
    fileName = Form("Acceptance_%s", _infoTag_Acceptance.c_str());
    create_Dir(folderName);
    TFile *facc =
        TFile::Open(Form("%s/%s.root", folderName.c_str(), fileName.c_str()), "READ");
    // Creating Correction file
    folderName = "../output/localJul2025/Correction" + formatCutsInName(_cutList, true);
    fileName = Form("Correction_%s", _infoTag.c_str());
    create_Dir(folderName);
    TFile *fout =
        TFile::Open(Form("%s/%s.root", folderName.c_str(), fileName.c_str()), "RECREATE");

    std::cout << "\n\nBeginning Correction of data for ";
    std::cout << _nameTarget << " target\n" << std::endl;

    // Get Acceptance THnSparse
    THnSparse *hAcc_Reconstructed = (THnSparse*)facc->Get("Acceptance_Reconstructed");
    THnSparse *hAcc_Match_GenVars = (THnSparse*)facc->Get("Acceptance_Match_GenVars");
    THnSparse *hAcc_Match_RecoVars = (THnSparse*)facc->Get("Acceptance_Match_RecoVars");

    // Create Final THnSparse
    std::vector<std::vector<double>> ordered_limits =
        map_to_vector_in_order<std::vector<double>>(_limitsMap, _variables);
    std::vector<double> ordered_min =
        map_to_vector_in_order<double>(_minimum, _variables);
    std::vector<double> ordered_max =
        map_to_vector_in_order<double>(_maximum, _variables);

    THnSparse *hCorr_Reconstructed = create_THnSparse("Correction_Reconstructed",
        ordered_limits, ordered_min, ordered_max, &_irregularBins);
    THnSparse *hCorr_Match_GenVars = create_THnSparse("Correction_Match_GenVars",
        ordered_limits, ordered_min, ordered_max, &_irregularBins);
    THnSparse *hCorr_Match_RecoVars = create_THnSparse("Correction_Match_RecoVars",
        ordered_limits, ordered_min, ordered_max, &_irregularBins);
    THnSparse *hRawData = create_THnSparse("Raw_data",
        ordered_limits, ordered_min, ordered_max, &_irregularBins);

    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;

    for (unsigned int jentry = 0; jentry < nentries; jentry++) {
        if (jentry % 1000000 == 0) {
            printf("Processing entry %10u out of %10llu, progress at %3.2f%%\n", jentry,
                nentries, 100. * (double)jentry / nentries);
        }

        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;

        if (!GoodElectron(ientry))
            continue;

		for (int i = 0; i < (int)PhiPQ->size(); i++) {
            if (!GoodPiPlus(ientry, i))
                continue;

            std::vector<double> bin = {Q2, 0, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};
            bin[1] = (_limitsMap.count("Nu"))? Nu : Xb;

            correct_Histogram(bin, hAcc_Reconstructed, hCorr_Reconstructed,
                cutIsUsed("FE"), cutIsUsed("AQ"));
            correct_Histogram(bin, hAcc_Match_GenVars, hCorr_Match_GenVars,
                cutIsUsed("FE"), cutIsUsed("AQ"));
            correct_Histogram(bin, hAcc_Match_RecoVars, hCorr_Match_RecoVars,
                cutIsUsed("FE"), cutIsUsed("AQ"));
            hRawData->Fill(bin.data());
        }  // loop over tracks (particles associated to scattered electron)
    }  // loop over entries (scattered electron)

    hCorr_Reconstructed->Write();
    hCorr_Match_GenVars->Write();
    hCorr_Match_RecoVars->Write();
    hRawData->Write();

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
    facc->Close();
}

/*
void Acceptance::ClosureTest()
{ // TODO: LEFT HERE! UPDATE THIS FUNCTION AND THE NEXT ONES!
    // Run over half of the sim and save in "../output/ClosureTest/AccCT_%s_B%i_%iD.root"
    // setClosureTest();

    std::string ct_folder = "../output/ClosureTest" + std::to_string(_fracCT) + "p" + getFoldNameExt();
    if (!check_Existence(Form("%s/AccCT_%s.root", ct_folder.c_str(), getAccFileName().c_str())))
    {
        std::cout << "Acceptance for ClosureTest doesn't exist. Creating file." << std::endl;
        Loop();
    }
    else
    {
        std::cout << "Acceptance for ClosureTest already exists! Using it." << std::endl;
        activateBranches();
    }

    auto& ThisBins = Bin_List[_binIndex];
    int nbins[5] = {static_cast<int>(ThisBins[0].size()-1), static_cast<int>(ThisBins[1].size()-1),
                    static_cast<int>(ThisBins[2].size()-1), static_cast<int>(ThisBins[3].size()-1),
                    static_cast<int>(ThisBins[4].size()-1)};

    // Begin Closure Test
    std::cout << "\n\nBeginning Closure Test for " << _nameTarget << " target\n" << std::endl;

    TFile *facc = TFile::Open(Form("%s/AccCT_%s.root", ct_folder.c_str(), getAccFileName().c_str()), "READ");
    TFile *fout = TFile::Open(Form("%s/ClosureTest_%s.root", ct_folder.c_str(), _infoTag.c_str()), "RECREATE");

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
    unsigned int first_entry = _fracCT*nentries/100.; // Default for ClosureTest is 50.

    Long64_t nbytes = 0, nb = 0;
    
    int global_bin=-1, global_bin_True=-1;
    int vec_entries=0, count = 0;
    bool good_electron_mc = false, good_electron = false;
    bool good_pion_mc = false, good_pion = false;
    std::vector<double> binKinVars, binKinVars_mc;
    for (unsigned int jentry = first_entry; jentry < nentries; jentry++)
    {
        count++;
        if ((jentry-first_entry) % 1000000 == 0)
            printf("Processing entry %9u, progress at %6.2f%%\n",jentry-first_entry,100.*(double)(jentry-first_entry)/(nentries-first_entry));

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
                if (_useXb) binKinVars_mc[1] = mc_Xb;
            }

            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                good_pion = true;
                binKinVars = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};
                if (_useXb) binKinVars[1] = Xb;
            }

            if (!good_pion_mc && !good_pion) continue;

            if (good_pion_mc)
            {
                histTrue->Fill(&binKinVars_mc[0]);
            }

            if (good_pion)
            {
                // Reconstructed
                CorrectBin(binKinVars, histAcc_Reconstru, histCorr_Reconstru, _useFullError, _useAccQlt);

                // ReMtch_mc
                CorrectBin(binKinVars, histAcc_ReMtch_mc, histCorr_ReMtch_mc, _useFullError, _useAccQlt);

                // ReMtch_re
                CorrectBin(binKinVars, histAcc_ReMtch_re, histCorr_ReMtch_re, _useFullError, _useAccQlt);
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
    activateBranches();

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    create_Dir(h2d_folder);

    if (_isData) fout = TFile::Open(Form("%s/KinematicVars_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/KinematicVars_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

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
    activateBranches();
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
    create_Dir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/XfVsYh_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/XfVsYh_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

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
    activateBranches();
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
    create_Dir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/ThetaPQ_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/ThetaPQ_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

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
    activateBranches();
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
    create_Dir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/LabAngles_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/LabAngles_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

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
    activateBranches();
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
    create_Dir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/PQVsLab_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/PQVsLab_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

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

void Acceptance::Hist2D_PQVsSector()
{
    activateBranches();
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
    if (!check_Existence(Form("%s/Acceptance_%s.root", acc_folder.c_str(), getAccFileName().c_str())))
    {
        if (!check_Existence(Form("../output/Acceptance%s/Acceptance_%s.root", getAccFoldNameExt().c_str(), getAccFileName().c_str())))
        {
            std::cout << "Acceptance file not found. Run getAcceptance before!" << std::endl;
            exit(0);
        }
        else
        {
            std::cout << "Acceptance file not found in JLab_cluster folder." << std::endl;
            std::cout << "Using Acceptance from /output/." << std::endl;
            acc_folder = "../output/Acceptance" + getAccFoldNameExt();
        }
    }
    TFile *facc = TFile::Open(Form("%s/Acceptance_%s.root", acc_folder.c_str(), getAccFileName().c_str()), "READ");
    THnSparse *histAcc = (THnSparse*)facc->Get("histAcc_Reconstru");

    setBinningType(-1);
    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    create_Dir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/PQVsSector_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/PQVsSector_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

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

    TH2D* hist2D_Sector_ThPQ_reco = new TH2D("hist2D_Sector_ThPQ_reco", "Two dimensional map Reco;Sector;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_reco = new TH2D("hist2D_SectorEl_ThPQ_reco", "Two dimensional map Reco;SectorEl;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);

    TH2D* hist2D_Sector_PhiPQ_recoAcc = new TH2D("hist2D_Sector_PhiPQ_recoAcc", "Two dimensional map Reco Acc;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_recoAcc = new TH2D("hist2D_SectorEl_PhiPQ_recoAcc", "Two dimensional map Reco Acc;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_recoAcc = new TH2D("hist2D_Sector_ThPQ_recoAcc", "Two dimensional map Reco Acc;Sector;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_recoAcc = new TH2D("hist2D_SectorEl_ThPQ_recoAcc", "Two dimensional map Reco Acc;SectorEl;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);

    // Reconstructed match
    TH2D* hist2D_Sector_PhiPQ_mtch = new TH2D("hist2D_Sector_PhiPQ_mtch", "Two dimensional map Match;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_mtch = new TH2D("hist2D_SectorEl_PhiPQ_mtch", "Two dimensional map Match;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_mtch = new TH2D("hist2D_Sector_ThPQ_mtch", "Two dimensional map Match;Sector;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_mtch = new TH2D("hist2D_SectorEl_ThPQ_mtch", "Two dimensional map Match;SectorEl;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);

    TH2D* hist2D_Sector_PhiPQ_mtchAcc = new TH2D("hist2D_Sector_PhiPQ_mtchAcc", "Two dimensional map Match Acc;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_mtchAcc = new TH2D("hist2D_SectorEl_PhiPQ_mtchAcc", "Two dimensional map Match Acc;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_mtchAcc = new TH2D("hist2D_Sector_ThPQ_mtchAcc", "Two dimensional map Match Acc;Sector;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_mtchAcc = new TH2D("hist2D_SectorEl_ThPQ_mtchAcc", "Two dimensional map Match Acc;SectorEl;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);

    // Generated (MC)
    TH2D* hist2D_Sector_PhiPQ_gene = new TH2D("hist2D_Sector_PhiPQ_gene", "Two dimensional map Generated;Sector;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);
    TH2D* hist2D_SectorEl_PhiPQ_gene = new TH2D("hist2D_SectorEl_PhiPQ_gene", "Two dimensional map Generated;SectorEl;#phi_{PQ}" , 6,0,6, 360,-180.0,180.0);

    TH2D* hist2D_Sector_ThPQ_gene = new TH2D("hist2D_Sector_ThPQ_gene", "Two dimensional map Generated;Sector;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);
    TH2D* hist2D_SectorEl_ThPQ_gene = new TH2D("hist2D_SectorEl_ThPQ_gene", "Two dimensional map Generated;SectorEl;#theta_{PQ}" , 6,0,6, 180,0.0,180.0);

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

void Acceptance::Hist2D_PQVsDeltaSector()
{
    activateBranches();
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
    if (!check_Existence(Form("%s/Acceptance_%s.root", acc_folder.c_str(), getAccFileName().c_str())))
    {
        if (!check_Existence(Form("../output/Acceptance%s/Acceptance_%s.root", getAccFoldNameExt().c_str(), getAccFileName().c_str())))
        {
            std::cout << "Acceptance file not found. Run getAcceptance before!" << std::endl;
            exit(0);
        }
        else
        {
            std::cout << "Acceptance file not found in JLab_cluster folder." << std::endl;
            std::cout << "Using Acceptance from /output/." << std::endl;
            acc_folder = "../output/Acceptance" + getAccFoldNameExt();
        }
    }
    TFile *facc = TFile::Open(Form("%s/Acceptance_%s.root", acc_folder.c_str(), getAccFileName().c_str()), "READ");
    THnSparse *histAcc = (THnSparse*)facc->Get("histAcc_Reconstru");

    setBinningType(-1);
    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    create_Dir(h2d_folder);
    if (_isData) fout = TFile::Open(Form("%s/PQVsDeltaSector_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/PQVsDeltaSector_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

    //// Define Histograms
    // Simple TH1
    TH1D* hist1D_DeltaSector_reco = new TH1D("hist1D_DeltaSector_reco", "Histogram 1D Reconstructed;DeltaSector (Pi-El);Counts", 11,-5,6);
    TH1D* hist1D_DeltaSector_mtch = new TH1D("hist1D_DeltaSector_mtch", "Histogram 1D Reconstructed match;DeltaSector (Pi-El);Counts", 11,-5,6);
    TH1D* hist1D_DeltaSector_gene = new TH1D("hist1D_DeltaSector_gene", "Histogram 1D Generated;DeltaSector (Pi-El);Counts", 11,-5,6);

    // Reconstructed or data
    TH2D* hist2D_DeltaSector_PhiPQ_reco = new TH2D("hist2D_DeltaSector_PhiPQ_reco", "Two dimensional map Reco;DeltaSector (Pi-El);#phi_{PQ}" , 11,-5,6, 360,-180.0,180.0);
    TH2D* hist2D_DeltaSector_ThPQ_reco = new TH2D("hist2D_DeltaSector_ThPQ_reco", "Two dimensional map Reco;DeltaSector (Pi-El);#theta_{PQ}" , 11,-5,6, 180,0.0,180.0);

    TH2D* hist2D_DeltaSector_PhiPQ_recoAcc = new TH2D("hist2D_DeltaSector_PhiPQ_recoAcc", "Two dimensional map Reco Acc;DeltaSector (Pi-El);#phi_{PQ}" , 11,-5,6, 360,-180.0,180.0);
    TH2D* hist2D_DeltaSector_ThPQ_recoAcc = new TH2D("hist2D_DeltaSector_ThPQ_recoAcc", "Two dimensional map Reco Acc;DeltaSector (Pi-El);#theta_{PQ}" , 11,-5,6, 180,0.0,180.0);

    // Reconstructed match
    TH2D* hist2D_DeltaSector_PhiPQ_mtch = new TH2D("hist2D_DeltaSector_PhiPQ_mtch", "Two dimensional map Match;DeltaSector (Pi-El);#phi_{PQ}" , 11,-5,6, 360,-180.0,180.0);
    TH2D* hist2D_DeltaSector_ThPQ_mtch = new TH2D("hist2D_DeltaSector_ThPQ_mtch", "Two dimensional map Match;DeltaSector (Pi-El);#theta_{PQ}" , 11,-5,6, 180,0.0,180.0);

    TH2D* hist2D_DeltaSector_PhiPQ_mtchAcc = new TH2D("hist2D_DeltaSector_PhiPQ_mtchAcc", "Two dimensional map Match Acc;DeltaSector (Pi-El);#phi_{PQ}" , 11,-5,6, 360,-180.0,180.0);
    TH2D* hist2D_DeltaSector_ThPQ_mtchAcc = new TH2D("hist2D_DeltaSector_ThPQ_mtchAcc", "Two dimensional map Match Acc;DeltaSector (Pi-El);#theta_{PQ}" , 11,-5,6, 180,0.0,180.0);

    // Generated (MC)
    TH2D* hist2D_DeltaSector_PhiPQ_gene = new TH2D("hist2D_DeltaSector_PhiPQ_gene", "Two dimensional map Generated;DeltaSector (Pi-El);#phi_{PQ}" , 11,-5,6, 360,-180.0,180.0);
    TH2D* hist2D_DeltaSector_ThPQ_gene = new TH2D("hist2D_DeltaSector_ThPQ_gene", "Two dimensional map Generated;DeltaSector (Pi-El);#theta_{PQ}" , 11,-5,6, 180,0.0,180.0);

    // Bin migration
    TH2D* histMigrationMatrixDeltaSector = new TH2D("histMigrationMatrixDeltaSector", "Migration DeltaSector (Pi-El);True DeltaSector; Reco DeltaSector", 11,-5,6, 11,-5,6);

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
                good_pion = true;
                n_pions++;

                hist1D_DeltaSector_reco->Fill(Sector->at(i)-SectorEl);

                hist2D_DeltaSector_PhiPQ_reco->Fill(Sector->at(i)-SectorEl, PhiPQ->at(i));
                hist2D_DeltaSector_ThPQ_reco->Fill(Sector->at(i)-SectorEl, ThetaPQ->at(i));

                binKinVars = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};

                pair<double, double> acc_val = GetCorrectValue(binKinVars, histAcc);
                if (acc_val.first != 0 && acc_val.second != 0)
                {
                    double weight = 1./acc_val.first;

                    hist2D_DeltaSector_PhiPQ_recoAcc->Fill(Sector->at(i)-SectorEl, PhiPQ->at(i), weight);
                    hist2D_DeltaSector_ThPQ_recoAcc->Fill(Sector->at(i)-SectorEl, ThetaPQ->at(i), weight);
                }
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
                n_pions_mc++;

                hist1D_DeltaSector_gene->Fill(mc_Sector->at(i)-mc_SectorEl);

                hist2D_DeltaSector_PhiPQ_gene->Fill(mc_Sector->at(i)-mc_SectorEl, mc_PhiPQ->at(i));
                hist2D_DeltaSector_ThPQ_gene->Fill(mc_Sector->at(i)-mc_SectorEl, mc_ThetaPQ->at(i));
            }

            if (good_pion && good_pion_mc)
            {
                at_least_one_pion_mtch = true;
                n_pions_match++;

                hist1D_DeltaSector_mtch->Fill(Sector->at(i)-SectorEl);

                hist2D_DeltaSector_PhiPQ_mtch->Fill(Sector->at(i)-SectorEl, PhiPQ->at(i));
                hist2D_DeltaSector_ThPQ_mtch->Fill(Sector->at(i)-SectorEl, ThetaPQ->at(i));

                binKinVars = {Q2, Nu, Zh->at(i), Pt2->at(i), PhiPQ->at(i)};

                pair<double, double> acc_val = GetCorrectValue(binKinVars, histAcc);
                if (acc_val.first != 0 && acc_val.second != 0)
                {
                    double weight = 1./acc_val.first;

                    hist2D_DeltaSector_PhiPQ_mtchAcc->Fill(Sector->at(i)-SectorEl, PhiPQ->at(i), weight);
                    hist2D_DeltaSector_ThPQ_mtchAcc->Fill(Sector->at(i)-SectorEl, ThetaPQ->at(i), weight);
                }

                histMigrationMatrixDeltaSector->Fill(mc_Sector->at(i)-mc_SectorEl, Sector->at(i)-SectorEl);
            }
        }   // loop over tracks

        // if (at_least_one_pion_mtch && good_electron && good_electron_mc)
        // {
        // }
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " matching pions out of " << n_pions_mc << " generated." << std::endl;

    if (_isData)
    {
        hist1D_DeltaSector_mtch->Delete();
        hist1D_DeltaSector_gene->Delete();

        hist2D_DeltaSector_PhiPQ_mtch->Delete();
        hist2D_DeltaSector_ThPQ_mtch->Delete();

        hist2D_DeltaSector_PhiPQ_mtchAcc->Delete();
        hist2D_DeltaSector_ThPQ_mtchAcc->Delete();

        hist2D_DeltaSector_PhiPQ_gene->Delete();
        hist2D_DeltaSector_ThPQ_gene->Delete();

        histMigrationMatrixDeltaSector->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
    facc->Close();
}

void Acceptance::Hist2D_VarsVsXb()
{
    activateBranches();

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    create_Dir(h2d_folder);

    if (_isData) fout = TFile::Open(Form("%s/VarsVsXb_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/VarsVsXb_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

    //// Define Histograms
    // Reconstructed or data
    TH2D* hist2D_Xb_Q2_reco = new TH2D("hist2D_Xb_Q2_reco", "Two dimensional Map;X_{b};Q^{2} [GeV^{2}]",                  100, 0.0, 1.0,  50, DISLimits[0][0], DISLimits[1][0]);
    TH2D* hist2D_Xb_Nu_reco = new TH2D("hist2D_Xb_Nu_reco", "Two dimensional Map;X_{b};#nu [GeV]",                        100, 0.0, 1.0,  50, DISLimits[0][1], DISLimits[1][1]);
    TH2D* hist2D_Xb_Zh_reco = new TH2D("hist2D_Xb_Zh_reco", "Two dimensional Map;X_{b};Z_{h}",                            100, 0.0, 1.0,  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Xb_Pt_reco = new TH2D("hist2D_Xb_Pt_reco", "Two dimensional Map;X_{b};P_{t}^{2} [GeV^{2}]",              100, 0.0, 1.0,  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Xb_PQ_reco = new TH2D("hist2D_Xb_PQ_reco", "Two dimensional Map;X_{b};#phi_{PQ} [deg]",                  100, 0.0, 1.0, 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Xb_Q2_goodPi_reco = new TH2D("hist2D_Xb_Q2_goodPi_reco", "Two dimensional Map;X_{b};Q^{2} [GeV^{2}]",    100, 0.0, 1.0,  50, DISLimits[0][0], DISLimits[1][0]);
    TH2D* hist2D_Xb_Nu_goodPi_reco = new TH2D("hist2D_Xb_Nu_goodPi_reco", "Two dimensional Map;X_{b};#nu [GeV]",          100, 0.0, 1.0,  50, DISLimits[0][1], DISLimits[1][1]);

    // Reconstructed match
    TH2D* hist2D_Xb_Q2_mtch = new TH2D("hist2D_Xb_Q2_mtch", "Two dimensional Map (Reco match);X_{b};Q^{2} [GeV^{2}]",                 100, 0.0, 1.0,  50, DISLimits[0][0], DISLimits[1][0]);
    TH2D* hist2D_Xb_Nu_mtch = new TH2D("hist2D_Xb_Nu_mtch", "Two dimensional Map (Reco match);X_{b};#nu [GeV]",                       100, 0.0, 1.0,  50, DISLimits[0][1], DISLimits[1][1]);
    TH2D* hist2D_Xb_Zh_mtch = new TH2D("hist2D_Xb_Zh_mtch", "Two dimensional Map (Reco match);X_{b};Z_{h}",                           100, 0.0, 1.0,  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Xb_Pt_mtch = new TH2D("hist2D_Xb_Pt_mtch", "Two dimensional Map (Reco match);X_{b};P_{t}^{2} [GeV^{2}]",             100, 0.0, 1.0,  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Xb_PQ_mtch = new TH2D("hist2D_Xb_PQ_mtch", "Two dimensional Map (Reco match);X_{b};#phi_{PQ} [deg]",                 100, 0.0, 1.0, 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Xb_Q2_goodPi_mtch = new TH2D("hist2D_Xb_Q2_goodPi_mtch", "Two dimensional Map (Reco match);X_{b};Q^{2} [GeV^{2}]",   100, 0.0, 1.0,  50, DISLimits[0][0], DISLimits[1][0]);
    TH2D* hist2D_Xb_Nu_goodPi_mtch = new TH2D("hist2D_Xb_Nu_goodPi_mtch", "Two dimensional Map (Reco match);X_{b};#nu [GeV]",         100, 0.0, 1.0,  50, DISLimits[0][1], DISLimits[1][1]);

    // Generated (MC)
    TH2D* hist2D_Xb_Q2_gene = new TH2D("hist2D_Xb_Q2_gene", "Two dimensional Map (Generated);X_{b};Q^{2} [GeV^{2}]",                  100, 0.0, 1.0,  50, DISLimits[0][0], DISLimits[1][0]);
    TH2D* hist2D_Xb_Nu_gene = new TH2D("hist2D_Xb_Nu_gene", "Two dimensional Map (Generated);X_{b};#nu [GeV]",                        100, 0.0, 1.0,  50, DISLimits[0][1], DISLimits[1][1]);
    TH2D* hist2D_Xb_Zh_gene = new TH2D("hist2D_Xb_Zh_gene", "Two dimensional Map (Generated);X_{b};Z_{h}",                            100, 0.0, 1.0,  50, DISLimits[0][2], DISLimits[1][2]);
    TH2D* hist2D_Xb_Pt_gene = new TH2D("hist2D_Xb_Pt_gene", "Two dimensional Map (Generated);X_{b};P_{t}^{2} [GeV^{2}]",              100, 0.0, 1.0,  50, DISLimits[0][3], DISLimits[1][3]);
    TH2D* hist2D_Xb_PQ_gene = new TH2D("hist2D_Xb_PQ_gene", "Two dimensional Map (Generated);X_{b};#phi_{PQ} [deg]",                  100, 0.0, 1.0, 180, DISLimits[0][4], DISLimits[1][4]);
    TH2D* hist2D_Xb_Q2_goodPi_gene = new TH2D("hist2D_Xb_Q2_goodPi_gene", "Two dimensional Map (Generated);X_{b};Q^{2} [GeV^{2}]",    100, 0.0, 1.0,  50, DISLimits[0][0], DISLimits[1][0]);
    TH2D* hist2D_Xb_Nu_goodPi_gene = new TH2D("hist2D_Xb_Nu_goodPi_gene", "Two dimensional Map (Generated);X_{b};#nu [GeV]",          100, 0.0, 1.0,  50, DISLimits[0][1], DISLimits[1][1]);

    // Bin migration
    TH2D* histMigrationMatrixXb = new TH2D("histMigrationMatrixXb", "Migration X_{b};True X_{b}; Reco X_{b}",                 100, 0.0, 1.0, 100, 0.0, 1.0);
    TH2D* histMigrationMatrixXb_goodPi = new TH2D("histMigrationMatrixXb_goodPi", "Migration X_{b};True X_{b}; Reco X_{b}",   100, 0.0, 1.0, 100, 0.0, 1.0);
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
            hist2D_Xb_Q2_reco->Fill(Xb,Q2);
            hist2D_Xb_Nu_reco->Fill(Xb,Nu);
        }

        if (!_isData && GoodElectron_MC(ientry, DISLimits))
        {
            good_electron_mc = true;
            hist2D_Xb_Q2_gene->Fill(mc_Xb,mc_Q2);
            hist2D_Xb_Nu_gene->Fill(mc_Xb,mc_Nu);
        }

        if (good_electron && good_electron_mc)
        {
            hist2D_Xb_Q2_mtch->Fill(Xb,Q2);
            hist2D_Xb_Nu_mtch->Fill(Xb,Nu);

            histMigrationMatrixXb->Fill(mc_Xb,Xb);
        }

        int vec_entries = PhiPQ->size();

		for (int i=0; i<vec_entries; i++)
        {
            good_pion_mc = false, good_pion = false;
            if (good_electron && GoodPiPlus(ientry, i, DISLimits))
            {
                n_pions++;
                good_pion = true;
                hist2D_Xb_Zh_reco->Fill(Xb, Zh->at(i));
                hist2D_Xb_Pt_reco->Fill(Xb, Pt2->at(i));
                hist2D_Xb_PQ_reco->Fill(Xb, PhiPQ->at(i));

                at_least_one_Pion = true;
            }

            if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            {
                good_pion_mc = true;
                hist2D_Xb_Zh_gene->Fill(mc_Xb, mc_Zh->at(i));
                hist2D_Xb_Pt_gene->Fill(mc_Xb, mc_Pt2->at(i));
                hist2D_Xb_PQ_gene->Fill(mc_Xb, mc_PhiPQ->at(i));

                at_least_one_mcPion = true;
            }

            if (good_pion && good_pion_mc)
            {
                n_pions_match++;
                hist2D_Xb_Zh_mtch->Fill(Xb, Zh->at(i));
                hist2D_Xb_Pt_mtch->Fill(Xb, Pt2->at(i));
                hist2D_Xb_PQ_mtch->Fill(Xb, PhiPQ->at(i));

                at_least_one_Pion_mtch = true;
            }
        }   // loop over tracks

        if (at_least_one_Pion)
        {
            hist2D_Xb_Q2_goodPi_reco->Fill(Xb,Q2);
            hist2D_Xb_Nu_goodPi_reco->Fill(Xb,Nu);
        }

        if (at_least_one_mcPion)
        {
            hist2D_Xb_Q2_goodPi_gene->Fill(mc_Xb,mc_Q2);
            hist2D_Xb_Nu_goodPi_gene->Fill(mc_Xb,mc_Nu);
        }

        if (at_least_one_Pion_mtch)
        {
            hist2D_Xb_Q2_goodPi_mtch->Fill(Xb,Q2);
            hist2D_Xb_Nu_goodPi_mtch->Fill(Xb,Nu);

            histMigrationMatrixXb_goodPi->Fill(mc_Xb,Xb);
        }
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    if (!_isData) std::cout << "There are " << n_pions_match << " final state Pions matching generated." << std::endl;

    if (_isData)
    {
        // Reconstructed match
        hist2D_Xb_Q2_mtch->Delete();
        hist2D_Xb_Nu_mtch->Delete();
        hist2D_Xb_Zh_mtch->Delete();
        hist2D_Xb_Pt_mtch->Delete();
        hist2D_Xb_PQ_mtch->Delete();
        hist2D_Xb_Q2_goodPi_mtch->Delete();
        hist2D_Xb_Nu_goodPi_mtch->Delete();

        // Generated (MC)
        hist2D_Xb_Q2_gene->Delete();
        hist2D_Xb_Nu_gene->Delete();
        hist2D_Xb_Zh_gene->Delete();
        hist2D_Xb_Pt_gene->Delete();
        hist2D_Xb_PQ_gene->Delete();
        hist2D_Xb_Q2_goodPi_gene->Delete();
        hist2D_Xb_Nu_goodPi_gene->Delete();

        // Bin migration
        histMigrationMatrixXb->Delete();
        histMigrationMatrixXb_goodPi->Delete();
    }

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

void Acceptance::Hist2D_PiCherenkovCounter()
{
    activateBranches();
    fChain->SetBranchStatus("Nphe", 1);
    fChain->SetBranchStatus("P", 1);

    fChain->SetBranchStatus("Mass2", 1);

    std::vector<std::vector<double>> all_space = {{DISLimits[0][0], DISLimits[1][0]}, {DISLimits[0][1], DISLimits[1][1]}, {0.0, 1.0}, {0.0, 5.0}, {-180., 180.}};
    UpdateDISLimits(DISLimits, all_space);

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    create_Dir(h2d_folder);

    if (_isData) fout = TFile::Open(Form("%s/CC_NpheVsP_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/CC_NpheVsP_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

    //// Define Histograms
    // Reconstructed or data
    TH1D* hist1D_NoNphe_P_Pi = new TH1D("hist1D_NoNphe_P_Pi", "P_{#pi^{+}} with NULL Nphe;P_{#pi^{+}} [GeV];Counts ", 150, 0.0, 5.0);
    TH2D* hist2D_Nphe_P_Pi = new TH2D("hist2D_Nphe_P_Pi", "P_{#pi^{+}} vs Nphe;P_{#pi^{+}} [GeV];Nphe ", 150, 0.0, 5.0, 150, 0.0, 300.0);

    TH1D* hist1D_NoNphe_P_Pi_MassCut = new TH1D("hist1D_NoNphe_P_Pi_MassCut", "P_{#pi^{+}} with NULL Nphe MassCut;P_{#pi^{+}} [GeV];Counts ", 150, 0.0, 5.0);
    TH2D* hist2D_Nphe_P_Pi_MassCut = new TH2D("hist2D_Nphe_P_Pi_MassCut", "P_{#pi^{+}} vs Nphe MassCut;P_{#pi^{+}} [GeV];Nphe ", 150, 0.0, 5.0, 150, 0.0, 300.0);

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

                if (Nphe->at(i) < 0){ hist1D_NoNphe_P_Pi->Fill(P->at(i)); }
                hist2D_Nphe_P_Pi->Fill(P->at(i), Nphe->at(i));

                if (Mass2->at(i) < 0.08)
                {
                    if (Nphe->at(i) < 0){ hist1D_NoNphe_P_Pi_MassCut->Fill(P->at(i)); }
                    hist2D_Nphe_P_Pi_MassCut->Fill(P->at(i), Nphe->at(i));
                }

                at_least_one_Pion = true;
            }

            // if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            // {
            //     good_pion_mc = true;

            //     at_least_one_mcPion = true;
            // }

            // if (good_pion && good_pion_mc)
            // {
            //     n_pions_match++;

            //     at_least_one_Pion_mtch = true;
            // }
        }   // loop over tracks

        // if (at_least_one_Pion)
        // {
        // }

        // if (at_least_one_mcPion)
        // {
        // }

        // if (at_least_one_Pion_mtch)
        // {
        // }
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    // if (!_isData) std::cout << "There are " << n_pions_match << " final state Pions matching generated." << std::endl;

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}

void Acceptance::Hist2D_NpheVs()
{
    activateBranches();
    fChain->SetBranchStatus("Nphe", 1);
    fChain->SetBranchStatus("NpheEl", 1);

    fChain->SetBranchStatus("P", 1);
    fChain->SetBranchStatus("Mass2", 1);
    fChain->SetBranchStatus("PhiLabEl", 1);
    fChain->SetBranchStatus("PhiLab", 1);
    fChain->SetBranchStatus("ThetaLabEl", 1);
    fChain->SetBranchStatus("ThetaLab", 1);
    fChain->SetBranchStatus("ThetaPQ", 1);

    std::vector<std::vector<double>> all_space = {{DISLimits[0][0], DISLimits[1][0]}, {DISLimits[0][1], DISLimits[1][1]}, {0.0, 1.0}, {0.0, 5.0}, {-180., 180.}};
    UpdateDISLimits(DISLimits, all_space);

    TFile *fout;
    std::string h2d_folder = "../output/Hist2D" + getFoldNameExt();
    create_Dir(h2d_folder);

    if (_isData) fout = TFile::Open(Form("%s/NpheVs_%s_data.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");
    else         fout = TFile::Open(Form("%s/NpheVs_%s_hsim.root", h2d_folder.c_str(), _infoTag.c_str()), "RECREATE");

    //// Define Histograms
    // Reconstructed or data

    // Nphe
    /////////
    TH1D* hist1D_NoNphe_vsNpheEl = new TH1D("hist1D_NoNphe_vsNpheEl", "N_{phe}^{e} with NULL N_{phe}^{#pi};N_{phe}^{e};Counts", 300,0.0,300.0);
    TH2D* hist2D_Nphe_vsNpheEl = new TH2D("hist2D_Nphe_vsNpheEl", "N_{phe}^{e} vs N_{phe}^{#pi};N_{phe}^{e};N_{phe}^{#pi}", 300,0.0,300.0, 300,0.0,300.0);

    TH1D* hist1D_NoNphe_vsPHad = new TH1D("hist1D_NoNphe_vsPHad", "P^{had} with NULL Nphe;P^{had} [GeV];Counts", 150,0.0,5.0);
    TH2D* hist2D_Nphe_vsPHad = new TH2D("hist2D_Nphe_vsPHad", "P^{had} vs Nphe;P^{had} [GeV];Nphe", 150,0.0,5.0, 300,0,300);

    TH1D* hist1D_NoNphe_vsMass2 = new TH1D("hist1D_NoNphe_vsMass2", "Mass^{2} with NULL Nphe;Mass^{2} [GeV^{2}];Counts", 100,-0.02,0.08);
    TH2D* hist2D_Nphe_vsMass2 = new TH2D("hist2D_Nphe_vsMass2", "Mass2 vs Nphe;Mass^{2} [GeV^{2}];Nphe", 100,-0.02,0.08, 300,0,300);

    TH1D* hist1D_NoNphe_vsXf = new TH1D("hist1D_NoNphe_vsXf", "X_{f} with NULL Nphe;X_{f};Counts", 100,-1,1);
    TH2D* hist2D_Nphe_vsXf = new TH2D("hist2D_Nphe_vsXf", "X_{f} vs Nphe;X_{f};Nphe", 100,-1,1, 300,0,300);

    TH1D* hist1D_NoNphe_vsPhiLabEl = new TH1D("hist1D_NoNphe_vsPhiLabEl", "#phi_{lab}^{e} with NULL Nphe;#phi_{lab}^{e} [deg];Counts", 360,-30,330);
    TH2D* hist2D_Nphe_vsPhiLabEl = new TH2D("hist2D_Nphe_vsPhiLabEl", "#phi_{lab}^{e} vs Nphe;#phi_{lab}^{e} [deg];Nphe", 360,-30,330, 300,0,300);

    TH1D* hist1D_NoNphe_vsPhiLab = new TH1D("hist1D_NoNphe_vsPhiLab", "#phi_{lab}^{#pi} with NULL Nphe;#phi_{lab}^{#pi} [deg];Counts", 360,-30,330);
    TH2D* hist2D_Nphe_vsPhiLab = new TH2D("hist2D_Nphe_vsPhiLab", "#phi_{lab}^{#pi} vs Nphe;#phi_{lab}^{#pi} [deg];Nphe", 360,-30,330, 300,0,300);

    TH1D* hist1D_NoNphe_vsThetaLabEl = new TH1D("hist1D_NoNphe_vsThetaLabEl", "#theta_{lab}^{e} with NULL Nphe;#theta_{lab}^{e} [deg];Counts", 100,0,100);
    TH2D* hist2D_Nphe_vsThetaLabEl = new TH2D("hist2D_Nphe_vsThetaLabEl", "#theta_{lab}^{e} vs Nphe;#theta_{lab}^{e} [deg];Nphe", 100,0,100, 300,0,300);

    TH1D* hist1D_NoNphe_vsThetaLab = new TH1D("hist1D_NoNphe_vsThetaLab", "#theta_{lab}^{#pi} with NULL Nphe;#theta_{lab}^{#pi} [deg];Counts", 100,0,100);
    TH2D* hist2D_Nphe_vsThetaLab = new TH2D("hist2D_Nphe_vsThetaLab", "#theta_{lab}^{#pi} vs Nphe;#theta_{lab}^{#pi} [deg];Nphe", 100,0,100, 300,0,300);

    TH1D* hist1D_NoNphe_vsPhiPQ = new TH1D("hist1D_NoNphe_vsPhiPQ", "#phi_{PQ} with NULL Nphe;#phi_{PQ} [deg];Counts", 360,-180,180);
    TH2D* hist2D_Nphe_vsPhiPQ = new TH2D("hist2D_Nphe_vsPhiPQ", "#phi_{PQ} vs Nphe;#phi_{PQ} [deg];Nphe", 360,-180,180, 300,0,300);

    TH1D* hist1D_NoNphe_vsThetaPQ = new TH1D("hist1D_NoNphe_vsThetaPQ", "#theta_{PQ} with NULL Nphe;#theta_{PQ} [deg];Counts", 100,0,100);
    TH2D* hist2D_Nphe_vsThetaPQ = new TH2D("hist2D_Nphe_vsThetaPQ", "#theta_{PQ} vs Nphe;#theta_{PQ} [deg];Nphe", 100,0,100, 300,0,300);

    // NpheEl
    ///////////
    TH2D* hist2D_NpheEl_vsPHad = new TH2D("hist2D_NpheEl_vsPHad", "P^{had} vs NpheEl;P^{had} [GeV];NpheEl", 150,0.0,5.0, 300,0,300);

    TH2D* hist2D_NpheEl_vsMass2 = new TH2D("hist2D_NpheEl_vsMass2", "Mass2 vs NpheEl;Mass^{2} [GeV^{2}];NpheEl", 100,-0.02,0.08, 300,0,300);

    TH2D* hist2D_NpheEl_vsXf = new TH2D("hist2D_NpheEl_vsXf", "X_{f} vs NpheEl;X_{f};NpheEl", 100,-1,1, 300,0,300);

    TH2D* hist2D_NpheEl_vsPhiLabEl_AllEvts = new TH2D("hist2D_NpheEl_vsPhiLabEl_AllEvts", "#phi_{lab}^{e} vs NpheEl;#phi_{lab}^{e} [deg];NpheEl", 360,-30,330, 300,0,300);
    TH2D* hist2D_NpheEl_vsPhiLabEl = new TH2D("hist2D_NpheEl_vsPhiLabEl", "#phi_{lab}^{e} vs NpheEl;#phi_{lab}^{e} [deg];NpheEl", 360,-30,330, 300,0,300);

    TH2D* hist2D_NpheEl_vsPhiLab = new TH2D("hist2D_NpheEl_vsPhiLab", "#phi_{lab}^{#pi} vs NpheEl;#phi_{lab}^{#pi} [deg];NpheEl", 360,-30,330, 300,0,300);

    TH2D* hist2D_NpheEl_vsThetaLabEl_AllEvts = new TH2D("hist2D_NpheEl_vsThetaLabEl_AllEvts", "#theta_{lab}^{e} vs NpheEl;#theta_{lab}^{e} [deg];NpheEl", 100,0,100, 300,0,300);
    TH2D* hist2D_NpheEl_vsThetaLabEl = new TH2D("hist2D_NpheEl_vsThetaLabEl", "#theta_{lab}^{e} vs NpheEl;#theta_{lab}^{e} [deg];NpheEl", 100,0,100, 300,0,300);

    TH2D* hist2D_NpheEl_vsThetaLab = new TH2D("hist2D_NpheEl_vsThetaLab", "#theta_{lab}^{#pi} vs NpheEl;#theta_{lab}^{#pi} [deg];NpheEl", 100,0,100, 300,0,300);

    TH2D* hist2D_NpheEl_vsPhiPQ = new TH2D("hist2D_NpheEl_vsPhiPQ", "#phi_{PQ} vs NpheEl;#phi_{PQ} [deg];NpheEl", 360,-180,180, 300,0,300);

    TH2D* hist2D_NpheEl_vsThetaPQ = new TH2D("hist2D_NpheEl_vsThetaPQ", "#theta_{PQ} vs NpheEl;#theta_{PQ} [deg];NpheEl", 100,0,100, 300,0,300);

    // Diff NpheEl - Nphe
    ///////////////////////
    TH2D* hist2D_DiffNphe_vsPHad = new TH2D("hist2D_DiffNphe_vsPHad", "P^{had} vs DiffNphe;P^{had} [GeV];NpheEl - Nphe", 150,0.0,5.0, 120,-20,100);

    TH2D* hist2D_DiffNphe_vsMass2 = new TH2D("hist2D_DiffNphe_vsMass2", "Mass2 vs DiffNphe;Mass^{2} [GeV^{2}];NpheEl - Nphe", 100,-0.02,0.08, 120,-20,100);

    TH2D* hist2D_DiffNphe_vsXf = new TH2D("hist2D_DiffNphe_vsXf", "X_{f} vs DiffNphe;X_{f};NpheEl - Nphe", 100,-1,1, 120,-20,100);

    TH2D* hist2D_DiffNphe_vsPhiLabEl = new TH2D("hist2D_DiffNphe_vsPhiLabEl", "#phi_{lab}^{e} vs DiffNphe;#phi_{lab}^{e} [deg];NpheEl - Nphe", 360,-30,330, 120,-20,100);

    TH2D* hist2D_DiffNphe_vsPhiLab = new TH2D("hist2D_DiffNphe_vsPhiLab", "#phi_{lab}^{#pi} vs DiffNphe;#phi_{lab}^{#pi} [deg];NpheEl - Nphe", 360,-30,330, 120,-20,100);

    TH2D* hist2D_DiffNphe_vsThetaLabEl = new TH2D("hist2D_DiffNphe_vsThetaLabEl", "#theta_{lab}^{e} vs DiffNphe;#theta_{lab}^{e} [deg];NpheEl - Nphe", 100,0,100, 120,-20,100);

    TH2D* hist2D_DiffNphe_vsThetaLab = new TH2D("hist2D_DiffNphe_vsThetaLab", "#theta_{lab}^{#pi} vs DiffNphe;#theta_{lab}^{#pi} [deg];NpheEl - Nphe", 100,0,100, 120,-20,100);

    TH2D* hist2D_DiffNphe_vsPhiPQ = new TH2D("hist2D_DiffNphe_vsPhiPQ", "#phi_{PQ} vs DiffNphe;#phi_{PQ} [deg];NpheEl - Nphe", 360,-180,180, 120,-20,100);

    TH2D* hist2D_DiffNphe_vsThetaPQ = new TH2D("hist2D_DiffNphe_vsThetaPQ", "#theta_{PQ} vs DiffNphe;#theta_{PQ} [deg];NpheEl - Nphe", 100,0,100, 120,-20,100);

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

            hist2D_NpheEl_vsPhiLabEl_AllEvts->Fill(PhiLabEl, NpheEl);
            hist2D_NpheEl_vsThetaLabEl_AllEvts->Fill(ThetaLabEl, NpheEl);
        }

        // if (!_isData && GoodElectron_MC(ientry, DISLimits))
        // {
        //     good_electron_mc = true;
        // }

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

                if (Nphe->at(i) < 0)
                {
                    hist1D_NoNphe_vsNpheEl->Fill(NpheEl);
                    hist1D_NoNphe_vsPHad->Fill(P->at(i));
                    hist1D_NoNphe_vsMass2->Fill(Mass2->at(i));
                    hist1D_NoNphe_vsXf->Fill(Xf->at(i));
                    hist1D_NoNphe_vsPhiLabEl->Fill(PhiLabEl);
                    hist1D_NoNphe_vsPhiLab->Fill(PhiLab->at(i));
                    hist1D_NoNphe_vsThetaLabEl->Fill(ThetaLabEl);
                    hist1D_NoNphe_vsThetaLab->Fill(ThetaLab->at(i));
                    hist1D_NoNphe_vsPhiPQ->Fill(PhiPQ->at(i));
                    hist1D_NoNphe_vsThetaPQ->Fill(ThetaPQ->at(i));
                }

                hist2D_Nphe_vsNpheEl->Fill(NpheEl, Nphe->at(i));
                hist2D_Nphe_vsPHad->Fill(P->at(i), Nphe->at(i));
                hist2D_Nphe_vsMass2->Fill(Mass2->at(i), Nphe->at(i));
                hist2D_Nphe_vsXf->Fill(Xf->at(i), Nphe->at(i));
                hist2D_Nphe_vsPhiLabEl->Fill(PhiLabEl, Nphe->at(i));
                hist2D_Nphe_vsPhiLab->Fill(PhiLab->at(i), Nphe->at(i));
                hist2D_Nphe_vsThetaLabEl->Fill(ThetaLabEl, Nphe->at(i));
                hist2D_Nphe_vsThetaLab->Fill(ThetaLab->at(i), Nphe->at(i));
                hist2D_Nphe_vsPhiPQ->Fill(PhiPQ->at(i), Nphe->at(i));
                hist2D_Nphe_vsThetaPQ->Fill(ThetaPQ->at(i), Nphe->at(i));

                hist2D_NpheEl_vsPHad->Fill(P->at(i), NpheEl);
                hist2D_NpheEl_vsMass2->Fill(Mass2->at(i), NpheEl);
                hist2D_NpheEl_vsXf->Fill(Xf->at(i), NpheEl);
                hist2D_NpheEl_vsPhiLab->Fill(PhiLab->at(i), NpheEl);
                hist2D_NpheEl_vsThetaLab->Fill(ThetaLab->at(i), NpheEl);
                hist2D_NpheEl_vsPhiPQ->Fill(PhiPQ->at(i), NpheEl);
                hist2D_NpheEl_vsThetaPQ->Fill(ThetaPQ->at(i), NpheEl);

                hist2D_DiffNphe_vsPHad->Fill(P->at(i), NpheEl - Nphe->at(i));
                hist2D_DiffNphe_vsMass2->Fill(Mass2->at(i), NpheEl - Nphe->at(i));
                hist2D_DiffNphe_vsXf->Fill(Xf->at(i), NpheEl - Nphe->at(i));
                hist2D_DiffNphe_vsPhiLabEl->Fill(PhiLabEl, NpheEl - Nphe->at(i));
                hist2D_DiffNphe_vsPhiLab->Fill(PhiLab->at(i), NpheEl - Nphe->at(i));
                hist2D_DiffNphe_vsThetaLabEl->Fill(ThetaLabEl, NpheEl - Nphe->at(i));
                hist2D_DiffNphe_vsThetaLab->Fill(ThetaLab->at(i), NpheEl - Nphe->at(i));
                hist2D_DiffNphe_vsPhiPQ->Fill(PhiPQ->at(i), NpheEl - Nphe->at(i));
                hist2D_DiffNphe_vsThetaPQ->Fill(ThetaPQ->at(i), NpheEl - Nphe->at(i));

                at_least_one_Pion = true;
            }

            // if (!_isData && good_electron_mc && GoodPiPlus_MC(ientry, i, DISLimits))
            // {
            //     good_pion_mc = true;

            //     at_least_one_mcPion = true;
            // }

            // if (good_pion && good_pion_mc)
            // {
            //     n_pions_match++;

            //     at_least_one_Pion_mtch = true;
            // }
        }   // loop over tracks

        if (at_least_one_Pion)
        {
            hist2D_NpheEl_vsPhiLabEl->Fill(PhiLabEl, NpheEl);
            hist2D_NpheEl_vsThetaLabEl->Fill(ThetaLabEl, NpheEl);
        }

        // if (at_least_one_mcPion)
        // {
        // }

        // if (at_least_one_Pion_mtch)
        // {
        // }
    }       // loop over entries

    std::cout << "There are " << n_pions << " final state Pions." << std::endl;
    // if (!_isData) std::cout << "There are " << n_pions_match << " final state Pions matching generated." << std::endl;

    std::cout << "Made it to the end. Saving..." << std::endl;

    fout->Write();
    fout->Close();
}
*/
