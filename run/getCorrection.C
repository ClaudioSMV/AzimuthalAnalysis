
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getCorrection(std::string target, int Nbin, int Ndim, std::string cuts = "") {
    TChain ch("ntuple_data");

    if (target.find("D") != std::string::npos) {
        std::cout << "Remember to include the solid target name after D to use a single ";
        std::cout << "dataset. Omitting it will mix all datasets.\n" << std::endl;
    }

    if (check_Existence("../../clas-data")) {
        if (target.find("Fe") != std::string::npos)
            ch.Add("../../clas-data/data_Fe1_light.root");
        else if (target.find("C") != std::string::npos)
            ch.Add("../../clas-data/data_C1_light.root");
        else if (target.find("Pb") != std::string::npos)
            ch.Add("../../clas-data/data_Pb1_light.root");
        else if (target == "D") {
            ch.Add("../../clas-data/data_Fe1_light.root");
            ch.Add("../../clas-data/data_C1_light.root");
            ch.Add("../../clas-data/data_Pb1_light.root");
        }
    }
    else {
        std::string homepath = "/home/csanmart/work/data/out/GetSimpleTuple_data";
        if (target.find("Fe") != std::string::npos)
            ch.Add(Form("%s/Fe/prunedFe_*.root", homepath.c_str()));
        else if (target.find("C") != std::string::npos)
            ch.Add(Form("%s/C/prunedC_*.root", homepath.c_str()));
        else if (target.find("Pb") != std::string::npos)
            ch.Add(Form("%s/Pb/prunedPb_*.root", homepath.c_str()));
        else if (target == "D") {
            ch.Add(Form("%s/Fe/prunedFe_*.root", homepath.c_str()));
            ch.Add(Form("%s/Pb/prunedPb_*.root", homepath.c_str()));
            ch.Add(Form("%s/C/prunedC_*.root", homepath.c_str()));
        }
    }

    Acceptance acc(&ch, target, Nbin, Ndim, cuts, true, true);
    acc.Correction();
}
