
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getClosureTest(std::string target, int Nbin, int Ndim, std::string cuts = "",
                    int fraction = 50, std::string nfold = "*"){
    TChain ch("ntuple_sim");
    if (check_Existence("../../clas-HSim")) {
        ch.Add(Form("../../clas-HSim/hsim_%s%s.root",target.c_str(),nfold.c_str()));
    }
    else {
        std::string homepath = "/home/csanmart/work/sim/out/GetSimpleTuple_HSim";
        std::string folder = target;
        if (target == "D")
            folder += "2_pb";
        if (nfold == "1" || nfold == "*")
            ch.Add(Form("%s/%s1/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str())); // prunedFe_80.root
        if (nfold == "9" || nfold == "*")
            ch.Add(Form("%s/%s9_yshiftm03/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str()));
        if (nfold == "2" || nfold == "*")
            ch.Add(Form("%s/%s2/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str()));
        if (nfold == "8" || nfold == "*")
            ch.Add(Form("%s/%s8_yshiftm03/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str()));
        if (nfold == "3" || nfold == "*")
            ch.Add(Form("%s/%s3/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str()));
        if (nfold == "7" || nfold == "*")
            ch.Add(Form("%s/%s7_yshiftm03/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str()));
        if (nfold == "4" || nfold == "*")
            ch.Add(Form("%s/%s4_yshiftm03/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str()));
        if (nfold == "6" || nfold == "*")
            ch.Add(Form("%s/%s6_yshiftm03/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str()));
        if (nfold == "5" || nfold == "*")
            ch.Add(Form("%s/%s5_yshiftm03/pruned%s_*.root", homepath.c_str(), folder.c_str(), target.c_str()));
    }

    Acceptance acc(&ch, target, Nbin, Ndim, cuts, false, false);
    acc.ClosureTest(fraction);
}
