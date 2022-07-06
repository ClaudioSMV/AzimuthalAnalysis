#define Acceptance_cxx
#include "Acceptance.h"
#include "Utility.h"
#include <TEfficiency.h>
#include <TH1.h>
#include <TH2.h>
#include <TH3.h>
#include <TMath.h>
#include <TStyle.h>
#include <TCanvas.h>

#include <iostream>
#include <vector>
#include <string>

const int elBINS = 9;
// DIS limits
vector<vector<float>> DISLimits = {{1.0, 4.1}, {2.2, 4.2}, {0.0, 1.0}, {0.0, 1.0}, {-180.0, 180.0}}; // Q2, Nu, Zh, Pt2, PhiPQ

// add underflow and overflow bins?
vector<double> Q2_binning = {1.0, 1.3, 1.8, 4.1};
vector<double> Nu_binning = {2.2, 3.2, 3.7, 4.2};

vector<vector<double>> virtual_limits = {Q2_binning, Nu_binning};

inline float DEG2RAD(float x)
{
    return 0.017453293 * x;
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

    fChain->SetBranchStatus("*",0);
    std::vector<string> activeBranches = {"TargType", "mc_TargType", "Q2", "mc_Q2", "Nu", "mc_Nu", "Xb", "mc_Xb",
                                          "Yb", "mc_Yb", "W", "mc_W", "vyec", "Zh", "mc_Zh", "Pt2", "mc_Pt2",
                                          "PhiPQ", "mc_PhiPQ", "pid", "mc_pid", "Nphe"}; //, "Xf"};
    for (const auto &activeBranch : activeBranches)
    {
        fChain->SetBranchStatus(activeBranch.c_str(), 1);
    }

    TFile *fout = TFile::Open("../output/test_acceptance.root", "RECREATE");

    // TH1::SetDefaultSumw2();

    // one-dimensional efficiency histogramss
    TH1F *h_test = new TH1F("h_test","Testing", 180,-180.,180.);

    // std::cout << "Setting up unfolding objects done" << std::endl;

    if (fChain == 0)
        return;
    Long64_t nentries = fChain->GetEntries();
    Long64_t nbytes = 0, nb = 0;
    // for (Long64_t jentry = 0; jentry < nentries; jentry++) {
    const int entries_to_process = nentries / 2;
    int global_bin;
    int vec_entries=0, vec_entries_MC=0;
    std::map<std::string, int> error_counter = {{"Wrong TargType",0}, {"Out of DIS range",0}, {"Out of VertexY Correction",0}, {"Different vector size",0}};
    std::map<std::string, int> particle_counter = {{"Leading Pion",0}, {"No Leading Pion",0}, {"Total Pions",0},
                               {"Good mc_Electron",0}, {"Good mc_Pion",0}};
    std::vector<double> kinematical_vars, mc_kinematical_vars;
    for (Long64_t jentry = 0; jentry < entries_to_process; jentry++)
    {
        if (jentry % 1000000 == 0)
            std::cout << "Processing entry " << jentry << ", progress at " << (double)jentry/(entries_to_process) << "%" << std::endl;

        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0)
            break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;
        // if (Cut(ientry) < 0) continue;

        if (!GoodElectron(ientry, DISLimits))
        {
            if (TargType!=_targTypeCut) error_counter["Wrong TargType"]++;
            if (Q2<DISLimits[0][0] || DISLimits[0][1]<Q2 || Yb>0.85 || W<2 || Nu<DISLimits[1][0] || DISLimits[1][1]<Nu) error_counter["Out of DIS range"]++;
            if (vyec<-1.4 || 1.4<vyec) error_counter["Out of VertexY Correction"]++;
            continue;
        }

        kinematical_vars = {Q2, Nu};
        global_bin = GlobalVarPosition(&kinematical_vars, &virtual_limits);

        vec_entries = PhiPQ->size();
        vec_entries_MC = mc_PhiPQ->size();
        if (vec_entries!=vec_entries_MC) error_counter["Different vector size"]++;

		for (int i=0; i<vec_entries; i++)
        {
            if (!GoodPiPlus(ientry, i, DISLimits)) continue;

            h_test->Fill(PhiPQ->at(i));
        }   // loop over tracks
    }       // loop over entries

    

    fout->Write();
    fout->Close();
}

////
/*
		int corbin = binNu + binQ2*NNu;

		float lead_Zh=-999, lead_Pt2=-999, lead_PhiPQ=-999;
		int lead_Sector=-1;
		int ientries = PhiPQ->size();
		for (int i=0; i<ientries; i++){
			if ((*pid)[i]==211 && (*Xf)[i]>0 && (*Zh)[i]>Limits[2][0] && (*Zh)[i]<Limits[2][1] && (*Pt2)[i]>Limits[3][0] &&
				(*Pt2)[i]<Limits[3][1] && (*PhiPQ)[i]>Limits[4][0] && (*PhiPQ)[i]<Limits[4][1] && (*Sector)[i]!=-9999){

				good_hcut = true;
				if ((*Zh)[i] > lead_Zh){
					lead_Zh = (*Zh)[i];
					lead_Pt2 = (*Pt2)[i];
					lead_PhiPQ = (*PhiPQ)[i];
					lead_Sector = (*Sector)[i];
				}

				if (good_ecut){
					count_NLP_raw_pi++;
					Double_t accbin_NLP[] = {Q2, Nu, (*Zh)[i], (*Pt2)[i], (*PhiPQ)[i]};

					hrawd_NLP_Vec[corbin]->Fill((*Zh)[i], (*Pt2)[i], (*PhiPQ)[i]);
					
					Int_t bin = hacc_Vec[(*Sector)[i]]->GetBin(accbin_NLP);
					Double_t acc_value = hacc_Vec[(*Sector)[i]]->GetBinContent(bin);
					if (acc_value!=0){
						hcorr_NLP_Vec[corbin]->Fill((*Zh)[i], (*Pt2)[i], (*PhiPQ)[i],1./acc_value);
						count_NLP_corr_pi++;
					}
				}
			}
		} // end of hadrons' loop

		if (good_ecut && good_hcut){
			count_lead_raw_pi++;
			Double_t accbin[] = {Q2, Nu, lead_Zh, lead_Pt2, lead_PhiPQ};

			hrawd_Vec[corbin]->Fill(lead_Zh,lead_Pt2,lead_PhiPQ);
			
			Int_t bin = hacc_Vec[lead_Sector]->GetBin(accbin);
			Double_t acc_value = hacc_Vec[lead_Sector]->GetBinContent(bin);
			if (acc_value!=0){
				hcorr_Vec[corbin]->Fill(lead_Zh,lead_Pt2,lead_PhiPQ,1./acc_value);
				count_lead_corr_pi++;
			}
		}
  	} // end filling loop

	std::cout << "\t100%" << " Correction loop finished!" << std::endl;
	std::cout << "Ratio leading pion / NLP: " << count_lead_raw_pi << " / " << count_NLP_raw_pi;
	std::cout << " (" << Form("%.3f",100*(float)count_lead_raw_pi/count_NLP_raw_pi) << "%)\n" << std::endl;

	std::cout << "Number of well corrected lead pions (acc_val!=0): " << count_lead_corr_pi << " out of " << count_lead_raw_pi;
	std::cout << " (" << Form("%.3f",100*(float)count_lead_corr_pi/count_lead_raw_pi) << "%)\n" << std::endl;
	std::cout << "Number of well corrected NLP pions (acc_val!=0): " << count_NLP_corr_pi << " out of " << count_NLP_raw_pi;
	std::cout << " (" << Form("%.3f",100*(float)count_NLP_corr_pi/count_NLP_raw_pi) << "%)\n" << std::endl;

	std::cout << "Saving and closing." << std::endl;

*/
////
        // if (TargType != _targTypeCut)
        //     continue;

        // if (mc_Q2 < Q2_binning[0] || mc_Q2 > Q2_binning[Q2_binning.size() - 1])
        //     continue;
        // if (mc_Nu < Nu_binning[0] || mc_Nu > Nu_binning[Nu_binning.size() - 1])
        //     continue;

        // auto idx = get_bin_index(mc_Q2, mc_Nu);
        // if (idx == -1)
        // {
        //     std::cout << "Error: index not found. Skipping event..." << std::endl;
        //     continue;
        // }

        // if (Zh->size() != mc_Zh->size())
        // {
        //     std::cout << "[ event: " << jentry << " ]: Zh.size() != mc_Zh.size()" << std::endl;
        // }

    //     for (size_t i = 0; i < mc_Zh->size(); i++)
    //     {
    //         if (mc_pid->at(i) != 211)
    //             continue;

    //         bool passed(false);

    //         histTrueZhPt2->Fill(mc_Zh->at(i), mc_Pt2->at(i));
    //         histTrueZhPt2PhiPQ->Fill(mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i));
    //         histTrueZh->Fill(mc_Zh->at(i));
    //         histTruePt2->Fill(mc_Pt2->at(i));
    //         histTruePhiPQ->Fill(mc_PhiPQ->at(i));

    //         if (pid->at(i) == 211 && Zh->at(i) > 0)
    //         {
    //             passed = true;
    //             histPassedZhPt2->Fill(mc_Zh->at(i), mc_Pt2->at(i));
    //             histPassedZhPt2PhiPQ->Fill(mc_Zh->at(i), mc_Pt2->at(i), mc_PhiPQ->at(i));

    //             histRecoZh->Fill(Zh->at(i));
    //             histRecoPt2->Fill(Pt2->at(i));
    //             histRecoPhiPQ->Fill(PhiPQ->at(i));

    //             histMigrationMatrixZh->Fill(mc_Zh->at(i), Zh->at(i));
    //             histMigrationMatrixPt2->Fill(mc_Pt2->at(i), Pt2->at(i));
    //             histMigrationMatrixPhiPQ->Fill(mc_PhiPQ->at(i), PhiPQ->at(i));

    //             float deltaZh = mc_Zh->at(i) - Zh->at(i);
    //             histResolutionZh->Fill(deltaZh / mc_Zh->at(i));

    //             float deltaPt2 = mc_Pt2->at(i) - Pt2->at(i);
    //             histResolutionPt2->Fill(deltaPt2 / mc_Pt2->at(i));

    //             // get the angle difference from a dot product to avoid angle conversions
    //             float cosp1cosp2 = TMath::Cos(DEG2RAD(mc_PhiPQ->at(i))) * TMath::Cos(DEG2RAD(PhiPQ->at(i)));
    //             float sinp1sinp2 = TMath::Sin(DEG2RAD(mc_PhiPQ->at(i))) * TMath::Sin(DEG2RAD(PhiPQ->at(i)));
    //             float deltaPhiPQ = TMath::ACos(cosp1cosp2 + sinp1sinp2) * 180.0 / TMath::Pi();
    //             histResolutionPhiPQ->Fill(deltaPhiPQ / mc_PhiPQ->at(i));
    //         }

    //         effZh->Fill(passed, mc_Zh->at(i));
    //         effPt2->Fill(passed, mc_Pt2->at(i));
    //         effPhiPQ->Fill(passed, mc_PhiPQ->at(i));

    //         if (passed)
    //         {
    //             responseZh[idx]->Fill(Zh->at(i), mc_Zh->at(i));
    //             responsePt2[idx]->Fill(Pt2->at(i), mc_Pt2->at(i));
    //             responsePhiPQ[idx]->Fill(PhiPQ->at(i), mc_PhiPQ->at(i));
    //             response2D[idx]->Fill(Zh->at(i), PhiPQ->at(i), mc_Zh->at(i), mc_PhiPQ->at(i));
    //         }
    //         else
    //         {
    //             responseZh[idx]->Miss(mc_Zh->at(i));
    //             responsePt2[idx]->Miss(mc_Pt2->at(i));
    //             responsePhiPQ[idx]->Miss(mc_PhiPQ->at(i));
    //             response2D[idx]->Miss(mc_Zh->at(i), mc_PhiPQ->at(i));
    //         }
    //         if (pid->at(i) > -9999 &&
    //             mc_pid->at(i) > -9999 &&
    //             mc_pid->at(i) != pid->at(i))
    //         {
    //             responseZh[idx]->Fake(mc_Zh->at(i));
    //             responsePt2[idx]->Fake(mc_Pt2->at(i));
    //             responsePhiPQ[idx]->Fake(mc_PhiPQ->at(i));
    //             response2D[idx]->Fake(mc_Zh->at(i), mc_PhiPQ->at(i));
    //         }
    //     } // loop over tracks
    // }     // loop over entries

//     effZh->Write();
//     effPt2->Write();
//     effPhiPQ->Write();

//     TH2F *accZhPt2 = (TH2F *)histPassedZhPt2->Clone("accZhPt2");
//     accZhPt2->Divide(histTrueZhPt2);
//     TH3F *accZhPt2PhiPQ = (TH3F *)histPassedZhPt2PhiPQ->Clone("accZhPt2PhiPQ");
//     accZhPt2PhiPQ->Divide(histTrueZhPt2PhiPQ);

//     std::cout << "Writing reponse objects to output file..." << std::endl;
//     for (int i = 0; i < elBINS; ++i)
//     {
//         responseZh[i]->Write();
//         responsePt2[i]->Write();
//         responsePhiPQ[i]->Write();
//         response2D[i]->Write();
//     }

//     fout->Write();
//     fout->Close();
// }
/*
void Acceptance::ClosureTest()
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
