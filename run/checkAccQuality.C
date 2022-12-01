
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
    THnSparse *histAcc_Reconstru = (THnSparse*)facc->Get("histAcc_Reconstru");
    THnSparse *histAcc_ReMtch_mc = (THnSparse*)facc->Get("histAcc_ReMtch_mc");
    THnSparse *histAcc_ReMtch_re = (THnSparse*)facc->Get("histAcc_ReMtch_re");

    TH1D *hPQEmpty_Reconstru = new TH1D("hPQEmpty_Reconstru", "hPQEmpty_Reconstru", this_binning[4].size(), -180., 180.);
    TH1D *hPQEmpty_ReMtch_mc = new TH1D("hPQEmpty_ReMtch_mc", "hPQEmpty_ReMtch_mc", this_binning[4].size(), -180., 180.);
    TH1D *hPQEmpty_ReMtch_re = new TH1D("hPQEmpty_ReMtch_re", "hPQEmpty_ReMtch_re", this_binning[4].size(), -180., 180.);

    TH1D *hAccVal_Reconstru = new TH1D("hAccVal_Reconstru", "hAccVal_Reconstru", 110, 0.0, 1.1);
    TH1D *hAccVal_ReMtch_mc = new TH1D("hAccVal_ReMtch_mc", "hAccVal_ReMtch_mc", 110, 0.0, 1.1);
    TH1D *hAccVal_ReMtch_re = new TH1D("hAccVal_ReMtch_re", "hAccVal_ReMtch_re", 110, 0.0, 1.1);

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
                        int bin_Reconstru = histAcc_Reconstru->GetBin(&kinVars[0]);
                        int bin_ReMtch_mc = histAcc_ReMtch_mc->GetBin(&kinVars[0]);
                        int bin_ReMtch_re = histAcc_ReMtch_re->GetBin(&kinVars[0]);

                        double val_Reconstru = histAcc_Reconstru->GetBinContent(bin_Reconstru);
                        double val_ReMtch_mc = histAcc_ReMtch_mc->GetBinContent(bin_ReMtch_mc);
                        double val_ReMtch_re = histAcc_ReMtch_re->GetBinContent(bin_ReMtch_re);

                        hAccVal_Reconstru->Fill(val_Reconstru);
                        if (val_Reconstru==0)
                        {
                            std::cout << Form("R1: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_Reconstru,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hPQEmpty_Reconstru->Fill(kinVars[4]);
                        }

                        hAccVal_ReMtch_mc->Fill(val_ReMtch_mc);
                        if (val_ReMtch_mc==0)
                        {
                            std::cout << Form("R2: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_ReMtch_mc,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hPQEmpty_ReMtch_mc->Fill(kinVars[4]);
                        }

                        hAccVal_ReMtch_re->Fill(val_ReMtch_re);
                        if (val_ReMtch_re==0)
                        {
                            std::cout << Form("R3: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_ReMtch_re,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hPQEmpty_ReMtch_re->Fill(kinVars[4]);
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
