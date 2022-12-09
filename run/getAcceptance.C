
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getAcceptance(std::string target = "Fe", int binName = 0, std::string cuts = "", std::string nfold = "*")
// Cuts: "Xf": X Feynman
{
    TChain ch("ntuple_sim");
    if (FileExists("../../clas-HSim"))
    {
        ch.Add(Form("../../clas-HSim/hsim_%s%s.root",target.c_str(),nfold.c_str()));
    }
    else
    {
        std::string suffix = "";
        if (target=="D") { suffix+="2_pb"; }
        if (nfold=="1" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s1/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); } // prunedFe_80.root
        if (nfold=="2" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s2/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); }
        if (nfold=="3" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s3/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); }
        if (nfold=="4" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s4_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); }
        if (nfold=="5" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s5_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); }
        if (nfold=="6" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s6_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); }
        if (nfold=="7" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s7_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); }
        if (nfold=="8" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s8_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); }
        if (nfold=="9" || nfold=="*") { ch.Add(Form("/home/csanmart/work/sim/out/GetSimpleTuple_HSim/%s%s9_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str())); }
    }

    Acceptance acc(&ch);
    acc.setTargName(target);
    acc.setBinningType(binName);
    if ( strstr(cuts.c_str(), "Xf") ) { acc.useCut_Xf(); std::cout << "Using Xf cut" << std::endl; }
    acc.Loop();
}
