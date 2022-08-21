
//
R__LOAD_LIBRARY(../include/Acceptance_C.so)

void getClosureTest(std::string target = "Fe", int binName = 0, int binNdim = 2, std::string nfold = "*")
{
    TChain ch("ntuple_sim");
    ch.Add(Form("../../clas-HSim/hsim_%s%s.root",target.c_str(),nfold.c_str()));
    
    Acceptance acc(&ch);
    acc.setTargName(target);
    acc.setBinningType(binName);
    acc.setBinNdims(binNdim);
    // acc.useCut_Xf();
    acc.ClosureTest();
}
