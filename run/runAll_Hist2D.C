
void runAll_Hist2D(std::string vars = "KinVars")
{
    std::cout << " > Data" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"Fe\", true, %s)",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"C\",  true, %s)",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"Pb\", true, %s)",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"D\",  true, %s)",vars.c_str()));

    std::cout << " > Simulations" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"Fe\", false, %s)",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"C\",  false, %s)",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"Pb\", false, %s)",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"D\",  false, %s)",vars.c_str()));
}