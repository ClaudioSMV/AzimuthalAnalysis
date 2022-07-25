
void runAll_2DProj()
{
    std::cout << "Data\n" << std::endl;
    gROOT->ProcessLine(".x get2DProj.C(\"Fe\", true)");
    gROOT->ProcessLine(".x get2DProj.C(\"C\", true)");
    gROOT->ProcessLine(".x get2DProj.C(\"Pb\", true)");
    gROOT->ProcessLine(".x get2DProj.C(\"D\", true)");

    std::cout << "Simulations\n" << std::endl;
    gROOT->ProcessLine(".x get2DProj.C(\"Fe\", false)");
    gROOT->ProcessLine(".x get2DProj.C(\"C\", false)");
    gROOT->ProcessLine(".x get2DProj.C(\"Pb\", false)");
    gROOT->ProcessLine(".x get2DProj.C(\"D\", false)");
}