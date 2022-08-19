
void runAll_ClosureTest(int binName = 0, int binNdim = 2)
{
    std::cout << " > Running Closure Test over all targets" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getClosureTest.C(\"Fe\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getClosureTest.C(\"C\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getClosureTest.C(\"Pb\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getClosureTest.C(\"D\",%i,%i)",binName,binNdim));
}