
void runAll_Acceptance(int binName = 0, std::string cuts = "")
{
    std::cout << " > Calculating Acceptance for all targets" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getAcceptance.C(\"Fe\",%i,\"%s\")",binName,cuts));
    gROOT->ProcessLine(Form(".x ../run/getAcceptance.C(\"C\",%i,\"%s\")",binName,cuts));
    gROOT->ProcessLine(Form(".x ../run/getAcceptance.C(\"Pb\",%i,\"%s\")",binName,cuts));
    gROOT->ProcessLine(Form(".x ../run/getAcceptance.C(\"D\",%i,\"%s\")",binName,cuts));
}
