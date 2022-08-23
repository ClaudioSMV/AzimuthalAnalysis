
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getAcceptance(std::string target = "Fe", int binName = 0, int binNdim = 2, std::string nfold = "*")
{
    TChain ch("ntuple_sim");
    if (FileExists("../../clas-HSim"))
    {
        ch.Add(Form("../../clas-HSim/hsim_%s%s.root",target.c_str(),nfold.c_str()));
    }
    else
    {
        if (target=="D") { target+="2_pb"; }
        if (nfold=="1" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s1/pruned%s_*.root",target.c_str(),target.c_str())); } // prunedFe_80.root
        if (nfold=="2" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s2/pruned%s_*.root",target.c_str(),target.c_str())); }
        if (nfold=="3" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s3/pruned%s_*.root",target.c_str(),target.c_str())); }
        if (nfold=="4" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s4_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str())); }
        if (nfold=="5" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s5_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str())); }
        if (nfold=="6" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s6_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str())); }
        if (nfold=="7" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s7_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str())); }
        if (nfold=="8" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s8_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str())); }
        if (nfold=="9" || nfold=="*") { ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s9_yshiftm03/pruned%s_*.root",target.c_str(),target.c_str())); }
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
