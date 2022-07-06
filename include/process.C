
//
R__LOAD_LIBRARY(Acceptance_C.so)

void process()
{
   TChain ch("ntuple_sim");
   ch.Add("../../clas-HSim/hsim_Fe1.root");
   // ch.Add("data/hsim_D2.root");
   // ch.Add("data/hsim_D3.root");
   // ch.Add("data/hsim_Fe1.root");
   // ch.Add("data/hsim_Fe2.root");
   // ch.Add("data/hsim_Fe3.root");
   Acceptance acc(&ch);
   acc.setTargTypeCut(2); // 0: bad, 1: liquid or 2: solid
   acc.Loop();
   // acc.ClosureTest();
}