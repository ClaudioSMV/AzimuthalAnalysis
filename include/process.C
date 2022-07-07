
//
R__LOAD_LIBRARY(Acceptance_C.so)

void process(std::string target = "Fe", std::string nfold = "*")
{
    TChain ch("ntuple_sim");
    ch.Add(Form("../../clas-HSim/hsim_%s%s.root",target.c_str(),nfold.c_str()));
    // ch.Add("data/hsim_D2.root");
    // ch.Add("data/hsim_D3.root");
    // ch.Add("data/hsim_Fe1.root");
    // ch.Add("data/hsim_Fe2.root");
    // ch.Add("data/hsim_Fe3.root");
    Acceptance acc(&ch);
    acc.setTargName(target);
    acc.Loop();
    // acc.ClosureTest();
}