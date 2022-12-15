
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getCorrection(std::string target = "Fe", int binName = 0, int binNdim = 1, std::string cuts = "", std::string solid_target = "")
// Cuts: "Xf": X Feynman; "DS": Delta Sector != 0; "FE": Full error
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
        else if (target=="D" && (solid_target=="All" || solid_target=="DS"))
        {
            ch.Add("../../clas-data/data_Fe1_light.root");
            ch.Add("../../clas-data/data_C1_light.root");
            ch.Add("../../clas-data/data_Pb1_light.root");
        }
        else
        {
            std::cout << "Deuterium target requires solid target information! (5th parameter)" << std::endl;
            std::cout << "If you want to run over all solid targets for deuterium use \"DS\"" << std::endl;
            return 0;
        }
    }
    else
    {
        if (target!="D")
        {
            ch.Add(Form("/home/csanmart/work/data/out/GetSimpleTuple_data/%s/pruned%s_*.root",target.c_str(),target.c_str()));
        }
        else if (target=="D" && solid_target=="Fe")
        {
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
        }
        else if (target=="D" && solid_target=="C")
        {
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/C/prunedC_*.root");
        }
        else if (target=="D" && solid_target=="Pb")
        {
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
        }
        else if (target=="D" && solid_target=="All")
        {
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
            ch.Add("/home/csanmart/work/data/out/GetSimpleTuple_data/C/prunedC_*.root");
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
    if ( strstr(cuts.c_str(), "Xf") ) { acc.useCut_Xf(); std::cout << "Using Xf cut" << std::endl; }
    if ( strstr(cuts.c_str(), "DS") ) { acc.useCut_DeltaSector0(); std::cout << "Using Delta Sector != 0 cut" << std::endl; }
    if ( strstr(cuts.c_str(), "FE") ) { acc.setFullError(); std::cout << "Using full error calculation" << std::endl; }
    acc.Correction();
}
