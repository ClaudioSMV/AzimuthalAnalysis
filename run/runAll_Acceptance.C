
void runAll_Acceptance()
{
    std::cout << " > Calculating Acceptance for all targets" << std::endl;
    gROOT->ProcessLine(".x ../run/getAcceptance.C(\"Fe\")");
    gROOT->ProcessLine(".x ../run/getAcceptance.C(\"C\")");
    gROOT->ProcessLine(".x ../run/getAcceptance.C(\"Pb\")");
    gROOT->ProcessLine(".x ../run/getAcceptance.C(\"D\")");
}
