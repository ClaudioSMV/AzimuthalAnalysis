
void runAll_Correction(int binName = 0, int binNdim = 2, std::string cuts = "")
{
    std::cout << " > Calculating Correction for all targets" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"Fe\",%i,%i,\"%s\")",binName,binNdim,cuts));
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"C\",%i,%i,\"%s\")",binName,binNdim,cuts));
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"Pb\",%i,%i,\"%s\")",binName,binNdim,cuts));
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"DFe\",%i,%i,\"%s\")",binName,binNdim,cuts));
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"DC\",%i,%i,\"%s\")",binName,binNdim,cuts));
    gROOT->ProcessLine(Form(".x ../run/getCorrection.C(\"DPb\",%i,%i,\"%s\")",binName,binNdim,cuts));
}
