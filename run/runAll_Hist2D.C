
void runAll_Hist2D(std::string vars = "KinVars")
{
    std::cout << " > Data" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"Fe\", true, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"C\",  true, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"Pb\", true, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"DFe\",  true, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"DC\",  true, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"DPb\",  true, \"%s\")",vars.c_str()));

    std::cout << " > Simulations" << std::endl;
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"Fe\", false, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"C\",  false, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"Pb\", false, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"DFe\",  false, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"DC\",  false, \"%s\")",vars.c_str()));
    gROOT->ProcessLine(Form(".x ../run/getHist2D.C(\"DPb\",  false, \"%s\")",vars.c_str()));
}
