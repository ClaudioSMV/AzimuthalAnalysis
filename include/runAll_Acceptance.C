
void runAll_Acceptance()
{
    std::cout << " > Calculating Acceptance for all targets" << std::endl;
    gROOT->ProcessLine(".x getAcceptance.C(\"Fe\")");
    gROOT->ProcessLine(".x getAcceptance.C(\"C\")");
    gROOT->ProcessLine(".x getAcceptance.C(\"Pb\")");
    gROOT->ProcessLine(".x getAcceptance.C(\"D\")");
}
