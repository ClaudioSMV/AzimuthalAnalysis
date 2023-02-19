
void runAll_ClosureTest(int binName = 0, int binNdim = 2, int fractionAcc = 50, std::string cuts = "")
{
    std::cout << " > Running Closure Test over all targets" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getClosureTest.C(\"Fe\",%i,%i,%i,\"%s\")",binName,binNdim,fractionAcc,cuts));
    gROOT->ProcessLine(Form(".x ../run/getClosureTest.C(\"C\",%i,%i,%i,\"%s\")",binName,binNdim,fractionAcc,cuts));
    gROOT->ProcessLine(Form(".x ../run/getClosureTest.C(\"Pb\",%i,%i,%i,\"%s\")",binName,binNdim,fractionAcc,cuts));
    gROOT->ProcessLine(Form(".x ../run/getClosureTest.C(\"D\",%i,%i,%i,\"%s\")",binName,binNdim,fractionAcc,cuts));
}