
//
R__LOAD_LIBRARY(Acceptance_C.so)

void get2DProj(std::string target = "Fe", bool isData = true)
{
    TChain ch;

    if (isData && target=="D")
    {
                     ch.Add("../../clas-data/data_Fe1_light.root?#ntuple_data");
                     ch.Add("../../clas-data/data_C1_light.root?#ntuple_data");
                     ch.Add("../../clas-data/data_Pb1_light.root?#ntuple_data");
    }
    else if (isData) ch.Add(Form("../../clas-data/data_%s1_light.root?#ntuple_data",target.c_str()));
    else
    {
        ch.SetName("ntuple_sim");
        ch.Add(Form("../../clas-HSim/hsim_%s*.root",target.c_str()));
    }
    
    std::cout << "\n >> Running Get2DProj for " << target << " target [file type: " << isData << "]\n" << std::endl;
    Acceptance acc(&ch, isData);
    acc.setTargName(target);
    acc.Get2DProj();
    // acc.ClosureTest();
}