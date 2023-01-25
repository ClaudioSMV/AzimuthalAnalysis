
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getHist2D(std::string target = "Fe", bool isData = true, std::string plot_name = "", std::string cuts = "", int nBinAcc = -1)
{
    TChain ch("ntuple_data");

    if (FileExists("../../clas-HSim"))
    {
        if (isData)
        {
            if (target.find("Fe")!=std::string::npos)
            {
                // ch.Add("../../clas-data/data_Fe1_light.root"); // This file has old cuts :'(
                ch.Add("../../clas-data/prunedFe_41146.root"); // This is the same as in the cluster
            }
            else if (target.find("C")!=std::string::npos)
            {
                ch.Add("../../clas-data/data_C1_light.root");
            }
            else if (target.find("Pb")!=std::string::npos)
            {
                ch.Add("../../clas-data/data_Pb1_light.root");
            }
            else if (target=="DS")
            {
                ch.Add("../../clas-data/data_Fe1_light.root");
                ch.Add("../../clas-data/data_C1_light.root");
                ch.Add("../../clas-data/data_Pb1_light.root");
            }
            else
            {
                std::cout << "Deuterium target requires solid target information!" << std::endl;
                std::cout << "If you want to run over all solid targets for deuterium use \"DS\"" << std::endl;
                return 0;
            }
        }
        else
        {
            ch.SetName("ntuple_sim");
            if (target=="D" || target=="DS")
            {
                ch.Add("../../clas-HSim/hsim_D*.root");
            }
            else if (target.find("D")==std::string::npos)
            {
                ch.Add(Form("../../clas-HSim/hsim_%s*.root",target.c_str()));
            }
            else
            {
                std::cout << "Deuterium simulations don't need solid target info!" << std::endl;
                std::cout << "If you want to run over deuterium simulations use \"D\" or \"DS\"" << std::endl;
                return 0;
            }
        }
    }
    else
    {
        if (isData)
        {
            if (target.find("Fe")!=std::string::npos)
            {
                ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
            }
            else if (target.find("C")!=std::string::npos)
            {
                ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/C/prunedC_*.root");
            }
            else if (target.find("Pb")!=std::string::npos)
            {
                ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
            }
            else if (target=="DS")
            {
                ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
                ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/C/prunedC_*.root");
                ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
            }
            else
            {
                std::cout << "Deuterium target requires solid target information!" << std::endl;
                std::cout << "If you want to run over all solid targets for deuterium use \"DS\"" << std::endl;
                return 0;
            }
        }
        else
        {
            ch.SetName("ntuple_sim");
            if (target=="D" || target=="DS")
            {
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb1/prunedD_*.root");
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb2/prunedD_*.root");
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb3/prunedD_*.root");
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb4_yshiftm03/prunedD_*.root");
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb5_yshiftm03/prunedD_*.root");
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb6_yshiftm03/prunedD_*.root");
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb7_yshiftm03/prunedD_*.root");
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb8_yshiftm03/prunedD_*.root");
                ch.Add("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/D2_pb9_yshiftm03/prunedD_*.root");
            }
            else if (target.find("D")==std::string::npos)
            {
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s1/pruned%s_*.root",target.c_str(),target.c_str()));
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s2/pruned%s_*.root",target.c_str(),target.c_str()));
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s3/pruned%s_*.root",target.c_str(),target.c_str()));
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s4_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str()));
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s5_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str()));
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s6_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str()));
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s7_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str()));
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s8_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str()));
                ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s9_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str()));
            }
            else
            {
                std::cout << "Deuterium simulations don't need solid target info!" << std::endl;
                std::cout << "If you want to run over deuterium simulations use \"D\" or \"DS\"" << std::endl;
                return 0;
            }
        }
    }

    std::string this_type = "Simulation";
    if (isData)
    {
        this_type = "Data";
    }

    Acceptance acc(&ch, isData);
    acc.setTargName(target);
    acc.ActivateCuts(cuts);

    if (plot_name == "KinVars")
    {
        std::cout << "\n >> Running Hist2D_KinVars for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_KinVars();
    }
    else if (plot_name == "XfVsYh")
    {
        std::cout << "\n >> Running Hist2D_XfVsYh for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_XfVsYh();
    }
    else if (plot_name == "ThetaPQ")
    {
        std::cout << "\n >> Running Hist2D_ThetaPQ for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_ThetaPQ();
    }
    else if (plot_name == "LabAngles")
    {
        std::cout << "\n >> Running Hist2D_LabAngles for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_LabAngles();
    }
    else if (plot_name == "PQVsLab")
    {
        std::cout << "\n >> Running Hist2D_PQVsLab for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_PQVsLab();
    }
    else if (plot_name == "VsSector" || plot_name == "PQVsSector")
    {
        // Select a binning for the acceptance!
        int this_bin = nBinAcc;
        // std::cout << "Enter binning for acceptance:" << std::endl;
        // std::cin >> this_bin;
        acc.setBinningType(this_bin);
        std::cout << "\n >> Running Hist2D_PQVsSector for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_PQVsSector();
    }
    else if (plot_name == "VsDeltaSector" || plot_name == "PQVsDeltaSector")
    {
        // Select a binning for the acceptance!
        int this_bin = nBinAcc;
        // std::cout << "Enter binning for acceptance:" << std::endl;
        // std::cin >> this_bin;
        acc.setBinningType(this_bin);
        std::cout << "\n >> Running Hist2D_PQVsDeltaSector for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_PQVsDeltaSector();
    }
    else if (plot_name == "VarsVsXb")
    {
        std::cout << "\n >> Running Hist2D_VarsVsXb for " << target << " target [file type: " << this_type << "]\n" << std::endl;
        acc.Hist2D_VarsVsXb();
    }
    else
    {
        std::cout << "\n >> Enter a valid third parameter for macro name. " << std::endl;
        std::cout << " >> Options: KinVars, XfVsYh, ThetaPQ, LabAngles, PQVsLab," << std::endl;
        std::cout << "             (PQ)VsSector, (PQ)VsDeltaSector, VarsVsXb.\n" << std::endl;
    }
}
