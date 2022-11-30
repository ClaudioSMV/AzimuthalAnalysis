
//
// R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"
#include "../include/Binning.h"

#include <vector>

using namespace DIS;

void checkAccQuality(std::string target = "Fe", int binName = 0)
{
    std::vector<std::vector<double>> this_binning = DIS::Bin_List[binName];

    TFile *facc = TFile::Open(Form("../output/JLab_cluster/Acceptance/Acceptance_%s_B%i.root", target.c_str(), binName), "READ");
    TFile *fout = TFile::Open(Form("Quality_%s_B%i.root", target.c_str(), binName), "RECREATE");

    // Get Acceptance THnSparse
    THnSparse *histAcc_Reconstructed  = (THnSparse*)facc->Get("histAcc_Reconstructed");
    THnSparse *histAcc_RecGoodGen_mc  = (THnSparse*)facc->Get("histAcc_RecGoodGen_mc");
    THnSparse *histAcc_RecGoodGen_rec = (THnSparse*)facc->Get("histAcc_RecGoodGen_rec");

    TH1D *hPQEmpty_Reconstructed = new TH1D("hPQEmpty_Reconstructed", "hPQEmpty_Reconstructed", this_binning[4].size(), -180., 180.);
    TH1D *hPQEmpty_RecGoodGen_mc = new TH1D("hPQEmpty_RecGoodGen_mc", "hPQEmpty_RecGoodGen_mc", this_binning[4].size(), -180., 180.);
    TH1D *hPQEmpty_RecGoodGen_rec = new TH1D("hPQEmpty_RecGoodGen_rec", "hPQEmpty_RecGoodGen_rec", this_binning[4].size(), -180., 180.);

    TH1D *hAccVal_Reconstructed = new TH1D("hAccVal_Reconstructed", "hAccVal_Reconstructed", 110, 0.0, 1.1);
    TH1D *hAccVal_RecGoodGen_mc = new TH1D("hAccVal_RecGoodGen_mc", "hAccVal_RecGoodGen_mc", 110, 0.0, 1.1);
    TH1D *hAccVal_RecGoodGen_rec = new TH1D("hAccVal_RecGoodGen_rec", "hAccVal_RecGoodGen_rec", 110, 0.0, 1.1);

    for (int Qi=0; Qi<this_binning[0].size()-1; Qi++)
    {
        for (int Ni=0; Ni<this_binning[1].size()-1; Ni++)
        {
            for (int Zi=0; Zi<this_binning[2].size()-1; Zi++)
            {
                for (int Pi=0; Pi<this_binning[3].size()-1; Pi++)
                {
                    for (int Ph=0; Ph<this_binning[4].size()-1; Ph++)
                    {
                        std::vector<double> kinVars = {this_binning[0][Qi], this_binning[1][Ni], this_binning[2][Zi], this_binning[3][Pi], this_binning[4][Ph]};
                        int bin_Reconstructed = histAcc_Reconstructed->GetBin(&kinVars[0]);
                        int bin_RecGoodGen_mc = histAcc_RecGoodGen_mc->GetBin(&kinVars[0]);
                        int bin_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBin(&kinVars[0]);

                        double val_Reconstructed = histAcc_Reconstructed->GetBinContent(bin_Reconstructed);
                        double val_RecGoodGen_mc = histAcc_RecGoodGen_mc->GetBinContent(bin_RecGoodGen_mc);
                        double val_RecGoodGen_rec = histAcc_RecGoodGen_rec->GetBinContent(bin_RecGoodGen_rec);

                        hAccVal_Reconstructed->Fill(val_Reconstructed);
                        if (val_Reconstructed==0)
                        {
                            std::cout << Form("R1: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_Reconstructed,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hPQEmpty_Reconstructed->Fill(kinVars[4]);
                        }

                        hAccVal_RecGoodGen_mc->Fill(val_RecGoodGen_mc);
                        if (val_RecGoodGen_mc==0)
                        {
                            std::cout << Form("R2: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_RecGoodGen_mc,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hPQEmpty_RecGoodGen_mc->Fill(kinVars[4]);
                        }

                        hAccVal_RecGoodGen_rec->Fill(val_RecGoodGen_rec);
                        if (val_RecGoodGen_rec==0)
                        {
                            std::cout << Form("R3: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_RecGoodGen_rec,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hPQEmpty_RecGoodGen_rec->Fill(kinVars[4]);
                        }
                    }
                }
            }
        }
    }

    fout->Write();
    fout->Close();
    facc->Close();
}
