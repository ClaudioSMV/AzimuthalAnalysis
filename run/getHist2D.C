
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)
#include "../include/Utility.h"

void getHist2D(std::string target = "Fe", bool isData = true, std::string vars = "KinVars")
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
            ch.Add("../../data/out/GetSimpleTuple_data/Fe/prunedFe_*.root");
            ch.Add("../../data/out/GetSimpleTuple_data/Pb/prunedPb_*.root");
            ch.Add("../../data/out/GetSimpleTuple_data/C/prunedC_*.root");
        }
        else if (isData) ch.Add(Form("../../data/out/GetSimpleTuple_data/%s/pruned%s_*.root",target.c_str(),target.c_str()));
        else
        {
            ch.SetName("ntuple_sim");
            std::string suffix = "";
            if (target=="D") { suffix+="2_pb"; }
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s1/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s2/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s3/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s4_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s5_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s6_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s7_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s8_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
            ch.Add(Form("../../sim/out/GetSimpleTuple_HSim/%s%s9_yshiftm03/pruned%s_*.root",target.c_str(),suffix.c_str(),target.c_str()));
        }
    }
    
    Acceptance acc(&ch, isData);
    acc.setTargName(target);
    if (vars.find("KinVars") != string::npos)
    {
        std::cout << "\n >> Running Hist2D_KinVars for " << target << " target [file type: " << isData << "]\n" << std::endl;
        acc.Hist2D_KinVars();
    }
    else if (vars.find("Yh") != string::npos)
    {
        std::cout << "\n >> Running Hist2D_XfVsYh for " << target << " target [file type: " << isData << "]\n" << std::endl;
        acc.Hist2D_XfVsYh();
    }
}