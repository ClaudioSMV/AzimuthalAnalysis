
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getHist2D(std::string target = "Fe", bool isData = true, std::string vars = "", int nBinAcc = -1)
{
    TChain ch("ntuple_data");

    if (FileExists("../../clas-HSim"))
    {
        if (isData && target=="D")
        {
            ch.Add("../../clas-data/data_Fe1_light.root");
            ch.Add("../../clas-data/data_C1_light.root");
            ch.Add("../../clas-data/data_Pb1_light.root");
        }
        else if (isData) ch.Add(Form("../../clas-data/data_%s1_light.root",target.c_str()));
        else
        {
            ch.SetName("ntuple_sim");
            ch.Add(Form("../../clas-HSim/hsim_%s*.root",target.c_str()));
        }
    }
    else
    {
        if (isData && target=="D")
        {
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/C/prunedC_*.root");
        }
        else if (isData) ch.Add(Form("/home/csanmart/work/data/out/GetSimpleTuple_data/%s/pruned%s_*.root",target.c_str(),target.c_str()));
        else
        {
            ch.SetName("ntuple_sim");
            std::string suffix = "";
            if (target=="D") { suffix+="2_pb"; }
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s1/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s2/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s3/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s4_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s5_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s6_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s7_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s8_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s9_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
        }
    }

    std::string this_type = "Simulation";
    if (isData)
    {
        this_type = "Data";
    }

    Acceptance acc(&ch, isData);
    acc.setTargName(target);
    if (vars.find("KinVars") != string::npos)
    {
        std::cout << "\n >> Running Hist2D_KinVars for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_KinVars();
    }
    else if (vars.find("XfVsYh") != string::npos)
    {
        std::cout << "\n >> Running Hist2D_XfVsYh for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_XfVsYh();
    }
    else if (vars.find("ThetaPQ") != string::npos)
    {
        std::cout << "\n >> Running Hist2D_ThetaPQ for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_ThetaPQ();
    }
    else if (vars.find("LabAngles") != string::npos)
    {
        std::cout << "\n >> Running Hist2D_LabAngles for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_LabAngles();
    }
    else if (vars.find("PQVsLab") != string::npos)
    {
        std::cout << "\n >> Running Hist2D_PQVsLab for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_PQVsLab();
    }
    else if (vars.find("VsSector") != string::npos)
    {
        // Select a binning for the acceptance!
        int this_bin = nBinAcc;
        // std::cout << "Enter binning for acceptance:" << std::endl;
        // std::cin >> this_bin;
        acc.setBinningType(this_bin);
        std::cout << "\n >> Running Hist2D_PhiPQVsSector for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_PhiPQVsSector();
    }
    else if (vars.find("VsDeltaSector") != string::npos)
    {
        // Select a binning for the acceptance!
        int this_bin = nBinAcc;
        // std::cout << "Enter binning for acceptance:" << std::endl;
        // std::cin >> this_bin;
        acc.setBinningType(this_bin);
        std::cout << "\n >> Running Hist2D_PhiPQVsDeltaSector for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_PhiPQVsDeltaSector();
    }
    else
    {
        std::cout << "\n >> Enter a valid third parameter for macro name. " << std::endl;
        std::cout << " >> Options: KinVars, XfVsYh, ThetaPQ, LabAngles, PQVsLab," << std::endl;
        std::cout << "             PhiPQVsSector, PhiPQVsDeltaSector.\n" << std::endl;
    }
}
