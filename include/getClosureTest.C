
//
R__LOAD_LIBRARY(Acceptance_C.so)

void getClosureTest(std::string target = "Fe", std::string nfold = "*")
{
    TChain ch("ntuple_sim");
    ch.Add(Form("../../clas-HSim/hsim_%s%s.root",target.c_str(),nfold.c_str()));
    
    Acceptance acc(&ch);
    acc.setTargName(target);
    acc.ClosureTest();
}