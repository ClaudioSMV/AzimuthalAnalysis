
//
// R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"
#include "../include/Binning.h"

#include <vector>

using namespace DIS;

void hist2DQuantiles(const int *n_bins, std::string target = "Fe", std::string cuts = "", std::string hist2d_name = "KinematicVars", bool isLocal = false)
{
    // n_bins should be of the form { 3,  3,  7,   7,    10,  0}
    //                              {Q2, Nu, Zh, Pt2, PhiPQ, Xb}
    // std::vector<std::vector<double>> this_binning = DIS::Bin_List[binName];

    if (cuts!="")
    {
        cuts = "_" + cuts;
    }
    std::string in_path = Form("../output/JLab_cluster/Hist2D%s",cuts.c_str());
    std::string out_path = Form("../output/JLab_cluster/Quantiles%s/%s",cuts.c_str(),hist2d_name.c_str());
    if (isLocal)
    {
        in_path = Form("../output/Hist2D%s",cuts.c_str());
        out_path = Form("../output/Quantiles%s/%s",cuts.c_str(),hist2d_name.c_str());
    }

    CreateDir(out_path);

    TFile *fin  = TFile::Open(Form("%s/%s_%s_hsim.root", in_path.c_str(), hist2d_name.c_str(), target.c_str()), "READ");
    // TFile *fout = TFile::Open(Form("%s/Quantile_%s.root", out_path.c_str(), target.c_str()), "RECREATE");

    std::string vars[6] = {"Q2", "Nu", "Zh", "Pt", "PQ", "Xb"};

    auto *key_list = fin->GetListOfKeys();

    for (auto *elem : *key_list)
    {
        std::string obj_name = elem->GetName();
        if (obj_name.find("_gene")!=std::string::npos)
        {
            // std::cout << "Good! " <<  elem->Class_Name() << "  " << elem->GetName() << std::endl;

            int ivarX=-1, ivarY=-1;
            int posInObjName1=-1, posInObjName2=-1;

            for (int j=0; j<6; j++)
            {
                if (obj_name.find(vars[j]) !=std::string::npos)
                {
                    if (posInObjName1==-1)
                    {
                        posInObjName1 = obj_name.find(vars[j]);
                        ivarX = j;
                    }
                    else
                    {
                        posInObjName2 = obj_name.find(vars[j]);
                        ivarY = j;
                    }
                }
            }

            // If the var1 is not the first in the name, associated to X, we switch them
            if (posInObjName1 > posInObjName2)
            {
                int itmp = ivarX;
                ivarX = ivarY;
                ivarY = itmp;
            }

            TH2D *this_hist2D = (TH2D*)fin->Get(obj_name.c_str());

            std::cout << "Name: " <<  obj_name << std::endl;

            // Get quantile of var1
            std::cout << "\t    {";
            const int nqX = n_bins[ivarX]+1;
            Double_t xq1[nqX+1];  // position where to compute the quantiles in [0,1]
            Double_t yq1[nqX+1];  // array to contain the quantiles
            // for (Int_t i=0;i<nqX;i++) xq1[i] = Float_t(i)/nqX;
            for (Int_t i=0;i<nqX+1;i++){
                xq1[i] = Float_t(i)/nqX;
                printf("%.3f",xq1[i]);
                if (i!=nqX) std::cout << ", ";
                else std::cout <<  "}" << std::endl;
            }
            std::cout << "\t" << vars[ivarX] << ": {";

            TH1D *hx_proj = (TH1D*)this_hist2D->ProjectionX();
            hx_proj->GetQuantiles(nqX+1,yq1,xq1);

            for (Int_t i=0;i<nqX+1;i++){
                printf("%.3f",yq1[i]);
                if (i!=nqX) std::cout << ", ";
                else std::cout <<  "}" << std::endl;
            }

            // Get quantile of var2
            std::cout << "\t    {";
            const int nqY = n_bins[ivarY]+1;
            Double_t xq2[nqY+1];  // position where to compute the quantiles in [0,1]
            Double_t yq2[nqY+1];  // array to contain the quantiles
            // for (Int_t i=0;i<nqY;i++) xq2[i] = Float_t(i)/nqY;
            for (Int_t i=0;i<nqY+1;i++){
                xq2[i] = Float_t(i)/nqY;
                printf("%.3f",xq2[i]);
                if (i!=nqY) std::cout << ", ";
                else std::cout <<  "}" << std::endl;
            }
            std::cout << "\t" << vars[ivarY] << ": {";

            TH1D *hy_proj = (TH1D*)this_hist2D->ProjectionY();
            hy_proj->GetQuantiles(nqY+1,yq2,xq2);

            for (Int_t i=0;i<nqY+1;i++){
                printf("%.3f",yq2[i]);
                if (i!=nqY) std::cout << ", ";
                else std::cout <<  "}\n" << std::endl;
            }
        }
    }

    // fout->Write();
    // fout->Close();
    fin->Close();
}
