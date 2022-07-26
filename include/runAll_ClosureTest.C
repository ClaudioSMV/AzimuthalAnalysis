
void runAll_ClosureTest()
{
    std::cout << " > Running Closure Test over all targets" << std::endl;
    gROOT->ProcessLine(".x getClosureTest.C(\"Fe\")");
    gROOT->ProcessLine(".x getClosureTest.C(\"C\")");
    gROOT->ProcessLine(".x getClosureTest.C(\"Pb\")");
    gROOT->ProcessLine(".x getClosureTest.C(\"D\")");
}