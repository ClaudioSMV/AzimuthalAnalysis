
void runAll_Acceptance(int binName = 0, int binNdim = 2)
{
    std::cout << " > Calculating Acceptance for all targets" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getAcceptance.C(\"Fe\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getAcceptance.C(\"C\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getAcceptance.C(\"Pb\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getAcceptance.C(\"D\",%i,%i)",binName,binNdim));
}
