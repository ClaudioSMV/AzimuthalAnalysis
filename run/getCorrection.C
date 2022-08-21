
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)

void getCorrection(std::string target = "Fe", int binName = 0, int binNdim = 2)
{
    TChain ch;

    if (target=="D")
    {
         ch.Add("../../clas-data/data_Fe1_light.root?#ntuple_data");
         ch.Add("../../clas-data/data_C1_light.root?#ntuple_data");
         ch.Add("../../clas-data/data_Pb1_light.root?#ntuple_data");
    }
    else ch.Add(Form("../../clas-data/data_%s1_light.root?#ntuple_data",target.c_str()));
    // ch.Add("data/hsim_D2.root");
    // ch.Add("data/hsim_D3.root");
    // ch.Add("data/hsim_Fe1.root");
    // ch.Add("data/hsim_Fe2.root");
    // ch.Add("data/hsim_Fe3.root");
    Acceptance acc(&ch, true); // REALLY IMPORTANT WHEN DEALING WITH DATA!
    acc.setTargName(target);
    acc.setBinningType(binName);
    acc.setBinNdims(binNdim);
    // acc.useCut_Xf();
    acc.Correction();
}
