
void runAll_ClosureTest()
{
    std::cout << " > Running Closure Test over all targets" << std::endl;
    gROOT->ProcessLine(".x ../run/getClosureTest.C(\"Fe\")");
    gROOT->ProcessLine(".x ../run/getClosureTest.C(\"C\")");
    gROOT->ProcessLine(".x ../run/getClosureTest.C(\"Pb\")");
    gROOT->ProcessLine(".x ../run/getClosureTest.C(\"D\")");
}