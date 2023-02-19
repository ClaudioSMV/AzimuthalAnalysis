
//
// R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"
#include "../include/Binning.h"

#include <vector>

using namespace DIS;

void checkAccQuality(std::string target = "Fe", int binName = 0, std::string acc_cuts = "", bool isLocal = false)
{
    std::vector<std::vector<double>> this_binning = DIS::Bin_List[binName];

    if (acc_cuts!="")
    {
        acc_cuts = "_" + acc_cuts;
    }
    std::string acc_path = Form("../output/JLab_cluster/Acceptance%s",acc_cuts.c_str());
    std::string out_path = Form("../output/JLab_cluster/QualityCheck%s",acc_cuts.c_str());
    if (isLocal)
    {
        acc_path = Form("../output/Acceptance%s",acc_cuts.c_str());
        out_path = Form("../output/QualityCheck%s",acc_cuts.c_str());
    }

    CreateDir(out_path);

    TFile *facc = TFile::Open(Form("%s/Acceptance_%s_%iB.root", acc_path.c_str(), target.c_str(), binName), "READ");
    TFile *fout = TFile::Open(Form("%s/Quality_%s_%iB.root", out_path.c_str(), target.c_str(), binName), "RECREATE");

    // Get Acceptance THnSparse
    THnSparse *histAcc_Reconstru = (THnSparse*)facc->Get("histAcc_Reconstru");
    THnSparse *histAcc_ReMtch_mc = (THnSparse*)facc->Get("histAcc_ReMtch_mc");
    THnSparse *histAcc_ReMtch_re = (THnSparse*)facc->Get("histAcc_ReMtch_re");

    // Get empty bin projections
    TH1D *hQ2Empty_Reconstru = new TH1D("hQ2Empty_Reconstru", "hQ2Empty_Reconstru", this_binning[0].size()-1, &this_binning[0][0]);
    TH1D *hQ2Empty_ReMtch_mc = new TH1D("hQ2Empty_ReMtch_mc", "hQ2Empty_ReMtch_mc", this_binning[0].size()-1, &this_binning[0][0]);
    TH1D *hQ2Empty_ReMtch_re = new TH1D("hQ2Empty_ReMtch_re", "hQ2Empty_ReMtch_re", this_binning[0].size()-1, &this_binning[0][0]);

    TH1D *hNuEmpty_Reconstru = new TH1D("hNuEmpty_Reconstru", "hNuEmpty_Reconstru", this_binning[1].size()-1, &this_binning[1][0]);
    TH1D *hNuEmpty_ReMtch_mc = new TH1D("hNuEmpty_ReMtch_mc", "hNuEmpty_ReMtch_mc", this_binning[1].size()-1, &this_binning[1][0]);
    TH1D *hNuEmpty_ReMtch_re = new TH1D("hNuEmpty_ReMtch_re", "hNuEmpty_ReMtch_re", this_binning[1].size()-1, &this_binning[1][0]);

    TH1D *hXbEmpty_Reconstru = new TH1D("hXbEmpty_Reconstru", "hXbEmpty_Reconstru", this_binning[1].size()-1, &this_binning[1][0]);
    TH1D *hXbEmpty_ReMtch_mc = new TH1D("hXbEmpty_ReMtch_mc", "hXbEmpty_ReMtch_mc", this_binning[1].size()-1, &this_binning[1][0]);
    TH1D *hXbEmpty_ReMtch_re = new TH1D("hXbEmpty_ReMtch_re", "hXbEmpty_ReMtch_re", this_binning[1].size()-1, &this_binning[1][0]);

    TH1D *hZhEmpty_Reconstru = new TH1D("hZhEmpty_Reconstru", "hZhEmpty_Reconstru", this_binning[2].size()-1, &this_binning[2][0]);
    TH1D *hZhEmpty_ReMtch_mc = new TH1D("hZhEmpty_ReMtch_mc", "hZhEmpty_ReMtch_mc", this_binning[2].size()-1, &this_binning[2][0]);
    TH1D *hZhEmpty_ReMtch_re = new TH1D("hZhEmpty_ReMtch_re", "hZhEmpty_ReMtch_re", this_binning[2].size()-1, &this_binning[2][0]);

    TH1D *hPtEmpty_Reconstru = new TH1D("hPtEmpty_Reconstru", "hPtEmpty_Reconstru", this_binning[3].size()-1, &this_binning[3][0]);
    TH1D *hPtEmpty_ReMtch_mc = new TH1D("hPtEmpty_ReMtch_mc", "hPtEmpty_ReMtch_mc", this_binning[3].size()-1, &this_binning[3][0]);
    TH1D *hPtEmpty_ReMtch_re = new TH1D("hPtEmpty_ReMtch_re", "hPtEmpty_ReMtch_re", this_binning[3].size()-1, &this_binning[3][0]);

    TH1D *hPQEmpty_Reconstru = new TH1D("hPQEmpty_Reconstru", "hPQEmpty_Reconstru", this_binning[4].size()-1, &this_binning[4][0]);
    TH1D *hPQEmpty_ReMtch_mc = new TH1D("hPQEmpty_ReMtch_mc", "hPQEmpty_ReMtch_mc", this_binning[4].size()-1, &this_binning[4][0]);
    TH1D *hPQEmpty_ReMtch_re = new TH1D("hPQEmpty_ReMtch_re", "hPQEmpty_ReMtch_re", this_binning[4].size()-1, &this_binning[4][0]);

    // Get Acceptance values and error
    TH1D *hAccVal_Reconstru = new TH1D("hAccVal_Reconstru", "hAccVal_Reconstru", 220, 0.0, 1.1);
    TH1D *hAccVal_ReMtch_mc = new TH1D("hAccVal_ReMtch_mc", "hAccVal_ReMtch_mc", 220, 0.0, 1.1);
    TH1D *hAccVal_ReMtch_re = new TH1D("hAccVal_ReMtch_re", "hAccVal_ReMtch_re", 220, 0.0, 1.1);

    TH1D *hAccErr_Reconstru = new TH1D("hAccErr_Reconstru", "hAccErr_Reconstru", 300, 0.0, 0.3);
    TH1D *hAccErr_ReMtch_mc = new TH1D("hAccErr_ReMtch_mc", "hAccErr_ReMtch_mc", 300, 0.0, 0.3);
    TH1D *hAccErr_ReMtch_re = new TH1D("hAccErr_ReMtch_re", "hAccErr_ReMtch_re", 300, 0.0, 0.3);

    // Get ratio  other method / Reconstructed
    TH1D *hAccRatio_ReMtch_mc = new TH1D("hAccRatio_ReMtch_mc", "hAccRatio_ReMtch_mc", 400, 0.0, 2.0);
    TH1D *hAccRatio_ReMtch_re = new TH1D("hAccRatio_ReMtch_re", "hAccRatio_ReMtch_re", 400, 0.0, 2.0);

    // Other methods when Reconstru is zero
    TH1D *hAccVal_ReMtch_mc_Reco0 = new TH1D("hAccVal_ReMtch_mc_Reco0", "hAccVal_ReMtch_mc_Reco0", 220, 0.0, 1.1);
    TH1D *hAccVal_ReMtch_re_Reco0 = new TH1D("hAccVal_ReMtch_re_Reco0", "hAccVal_ReMtch_re_Reco0", 220, 0.0, 1.1);

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

                        // Fill Reconstru
                        hAccVal_Reconstru->Fill(val_Reconstru);
                        if (val_Reconstru==0)
                        {
                            std::cout << Form("R1: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_Reconstru,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hQ2Empty_Reconstru->Fill(kinVars[0]);
                            if (DIS::list_boolXb[binName]) hXbEmpty_Reconstru->Fill(kinVars[1]);
                            else hNuEmpty_Reconstru->Fill(kinVars[1]);
                            hZhEmpty_Reconstru->Fill(kinVars[2]);
                            hPtEmpty_Reconstru->Fill(kinVars[3]);
                            hPQEmpty_Reconstru->Fill(kinVars[4]);

                            hAccVal_ReMtch_mc_Reco0->Fill(val_ReMtch_mc);
                            hAccVal_ReMtch_re_Reco0->Fill(val_ReMtch_re);
                        }
                        else
                        {
                            hAccErr_Reconstru->Fill(histAcc_Reconstru->GetBinError(bin_Reconstru));

                            // Fill ratio plots
                            hAccRatio_ReMtch_mc->Fill(val_ReMtch_mc/val_Reconstru);
                            hAccRatio_ReMtch_re->Fill(val_ReMtch_re/val_Reconstru);
                        }

                        // Fill ReMtch_mc
                        hAccVal_ReMtch_mc->Fill(val_ReMtch_mc);
                        if (val_ReMtch_mc==0)
                        {
                            std::cout << Form("R2: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_ReMtch_mc,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hQ2Empty_ReMtch_mc->Fill(kinVars[0]);
                            if (DIS::list_boolXb[binName]) hXbEmpty_ReMtch_mc->Fill(kinVars[1]);
                            else hNuEmpty_ReMtch_mc->Fill(kinVars[1]);
                            hZhEmpty_ReMtch_mc->Fill(kinVars[2]);
                            hPtEmpty_ReMtch_mc->Fill(kinVars[3]);
                            hPQEmpty_ReMtch_mc->Fill(kinVars[4]);
                        }
                        else
                        {
                            hAccErr_ReMtch_mc->Fill(histAcc_ReMtch_mc->GetBinError(bin_ReMtch_mc));
                        }

                        // Fill ReMtch_re
                        hAccVal_ReMtch_re->Fill(val_ReMtch_re);
                        if (val_ReMtch_re==0)
                        {
                            std::cout << Form("R3: Bin %i is empty! >> (%.2f, %.2f, %.2f, %.2f, %.2f)",bin_ReMtch_re,kinVars[0],kinVars[1],kinVars[2],kinVars[3],kinVars[4]) << std::endl;
                            hQ2Empty_ReMtch_re->Fill(kinVars[0]);
                            if (DIS::list_boolXb[binName]) hXbEmpty_ReMtch_re->Fill(kinVars[1]);
                            else hNuEmpty_ReMtch_re->Fill(kinVars[1]);
                            hZhEmpty_ReMtch_re->Fill(kinVars[2]);
                            hPtEmpty_ReMtch_re->Fill(kinVars[3]);
                            hPQEmpty_ReMtch_re->Fill(kinVars[4]);
                        }
                        else
                        {
                            hAccErr_ReMtch_re->Fill(histAcc_ReMtch_re->GetBinError(bin_ReMtch_re));
                        }
                    }
                }
            }
        }
    }

    if (DIS::list_boolXb[binName]){
        hNuEmpty_Reconstru->Delete();
        hNuEmpty_ReMtch_mc->Delete();
        hNuEmpty_ReMtch_re->Delete();
    }
    else{
        hXbEmpty_Reconstru->Delete();
        hXbEmpty_ReMtch_mc->Delete();
        hXbEmpty_ReMtch_re->Delete();
    }

    fout->Write();
    fout->Close();
    facc->Close();
}
