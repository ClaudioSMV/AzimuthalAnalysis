
void runAll_Correction(int binName = 0, int binNdim = 2)
{
    std::cout << " > Calculating Correction for all targets" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"Fe\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"C\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"Pb\",%i,%i)",binName,binNdim));
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"D\",%i,%i)",binName,binNdim));
}
