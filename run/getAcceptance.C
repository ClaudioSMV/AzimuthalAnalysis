
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getAcceptance(std::string target = "Fe", int binName = 0, int binNdim = 2, std::string nfold = "*")
{
  TChain ch("ntuple_sim");
    if (FileExists("../../clas-HSim"))
    {
        ch.Add(Form("../../clas-HSim/hsim_%s%s.root?#ntuple_sim",target.c_str(),nfold.c_str()));
    }
    else
    {
        ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s/pruned%s_*.root",target.c_str(),nfold.c_str(),target.c_str())); // prunedFe_80.root
    }
    // ch.Add("data/hsim_D2.root");
    // ch.Add("data/hsim_D3.root");
    // ch.Add("data/hsim_Fe1.root");
    // ch.Add("data/hsim_Fe2.root");
    // ch.Add("data/hsim_Fe3.root");
    Acceptance acc(&ch);
    acc.setTargName(target);
    acc.setBinningType(binName);
    // acc.useCut_Xf();
    acc.Loop();
}
