
void runAll_2DProj()
{
    std::cout << " > Data" << std::endl;
    gROOT->ProcessLine(".x ../run/get2DProj.C(\"Fe\", true)");
    gROOT->ProcessLine(".x ../run/get2DProj.C(\"C\", true)");
    gROOT->ProcessLine(".x ../run/get2DProj.C(\"Pb\", true)");
    gROOT->ProcessLine(".x ../run/get2DProj.C(\"D\", true)");

    std::cout << " > Simulations" << std::endl;
    gROOT->ProcessLine(".x ../run/get2DProj.C(\"Fe\", false)");
    gROOT->ProcessLine(".x ../run/get2DProj.C(\"C\", false)");
    gROOT->ProcessLine(".x ../run/get2DProj.C(\"Pb\", false)");
    gROOT->ProcessLine(".x ../run/get2DProj.C(\"D\", false)");
}