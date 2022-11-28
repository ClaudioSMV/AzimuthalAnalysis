
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getCorrection(std::string target = "Fe", int binName = 0, int binNdim = 1, std::string solid_target = "", bool useFullError = false)
{
    TChain ch("ntuple_data");
    if (FileExists("../../clas-data"))
    {
        if (target!="D")
        {
            ch.Add(Form("../../clas-data/data_%s1_light.root",target.c_str()));
        }
        else if (target=="D" && solid_target=="Fe")
        {
            ch.Add("../../clas-data/data_Fe1_light.root");
        }
        else if (target=="D" && solid_target=="C")
        {
            ch.Add("../../clas-data/data_C1_light.root");
        }
        else if (target=="D" && solid_target=="Pb")
        {
            ch.Add("../../clas-data/data_Pb1_light.root");
        }
        else if (target=="D" && solid_target=="All")
        {
            ch.Add("../../clas-data/data_Fe1_light.root");
            ch.Add("../../clas-data/data_C1_light.root");
            ch.Add("../../clas-data/data_Pb1_light.root");
        }
        else
        {
            std::cout << "Deuterium target requires solid target information! (4th parameter)" << std::endl;
            std::cout << "If you want to run over all solid targets for deuterium, use \"All\"" << std::endl;
            return 0;
        }
    }
    else
    {
        if (target!="D")
        {
            ch.Add(Form("../../data/out/GetSimpleTuple_data/%s/pruned%s_*.root",target.c_str(),target.c_str()));
        }
        else if (target=="D" && solid_target=="Fe")
        {
            ch.Add("../../data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
        }
        else if (target=="D" && solid_target=="C")
        {
            ch.Add("../../data/out/GetSimpleTuple_data/C/prunedC_*.root");
        }
        else if (target=="D" && solid_target=="Pb")
        {
            ch.Add("../../data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
        }
        else if (target=="D" && solid_target=="All")
        {
            ch.Add("../../data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
            ch.Add("../../data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
            ch.Add("../../data/out/GetSimpleTuple_data/C/prunedC_*.root");
        }
        else
        {
            std::cout << "Deuterium target requires solid target information! (4th parameter)" << std::endl;
            std::cout << "If you want to run over all solid targets for deuterium, use \"All\"" << std::endl;
            return 0;
        }
    }

    Acceptance acc(&ch, true); // REALLY IMPORTANT WHEN DEALING WITH DATA!
    acc.setTargName(target, solid_target);
    acc.setBinningType(binName);
    acc.setBinNdims(binNdim);
    // acc.useCut_Xf();
    if (useFullError) { acc.setFullError(); }
    acc.Correction();
}
