
void runAll_Correction()
{
    std::cout << " > Calculating Correction for all targets" << std::endl;
    gROOT->ProcessLine(".x ../run/getCorrection.C(\"Fe\")");
    gROOT->ProcessLine(".x ../run/getCorrection.C(\"C\")");
    gROOT->ProcessLine(".x ../run/getCorrection.C(\"Pb\")");
    gROOT->ProcessLine(".x ../run/getCorrection.C(\"D\")");
}
