
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getCorrection(std::string target = "Fe", int binName = 0, int binNdim = 2)
{
    TChain ch("ntuple_data");
    if (FileExists("../../clas-data"))
    {
        if (target=="D")
        {
            ch.Add("../../clas-data/data_Fe1_light.root");
            ch.Add("../../clas-data/data_C1_light.root");
            ch.Add("../../clas-data/data_Pb1_light.root");
        }
        else ch.Add(Form("../../clas-data/data_%s1_light.root",target.c_str()));
    }
    else
    {
        if (target=="D")
        {
            ch.Add("../../data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
            ch.Add("../../data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
            ch.Add("../../data/out/GetSimpleTuple_data/C/prunedC_*.root");
        }
        else ch.Add(Form("../../data/out/GetSimpleTuple_data/%s/pruned%s_*.root",target.c_str(),target.c_str()));
    }

    Acceptance acc(&ch, true); // REALLY IMPORTANT WHEN DEALING WITH DATA!
    acc.setTargName(target);
    acc.setBinningType(binName);
    acc.setBinNdims(binNdim);
    // acc.useCut_Xf();
    acc.Correction();
}
