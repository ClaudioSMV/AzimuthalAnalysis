#ifndef Binning_h
#define Binning_h

#include <vector>
#include <map>

namespace DIS
{
    // DIS limits
    // vector<vector<float>> DISLimits = {{1.0, 4.1}, {2.2, 4.2}, {0.0, 1.0}, {0.0, 1.0}, {-180.0, 180.0}}; // Q2, Nu, Zh, Pt2, PhiPQ
    std::vector<std::vector<double>> DISLimits = {{1.0, 2.2, 0.0, 0.0,-180.0},
                                                  {4.1, 4.2, 1.0, 1.0, 180.0}}; // Q2, Nu, Zh, Pt2, PhiPQ

    // int nbins[5] = {3, 3, 5, 5, 40};

    // Ordered always following: Q2, Nu, Zh, Pt2, PhiPQ
    std::vector<std::vector<double>> Bin_Origin = {{1.00, 1.30, 1.80, 4.10},
                                                   {2.20, 3.20, 3.70, 4.20},
                                                   {0.00, 0.15, 0.25, 0.40, 0.70, 1.00},
                                                   {0.00, 0.03, 0.06, 0.10, 0.18, 1.00},
                                                   {-180.00, -171.00, -162.00, -153.00, -144.00, -135.00, -126.00, -117.00, -108.00, -99.00,
                                                     -90.00,  -81.00,  -72.00,  -63.00,  -54.00,  -45.00,  -36.00,  -27.00,  -18.00,  -9.00,
                                                       0.00,    9.00,   18.00,   27.00,   36.00,   45.00,   54.00,   63.00,   72.00,  81.00,
                                                      90.00,   99.00,  108.00,  117.00,  126.00,  135.00,  144.00,  153.00,  162.00, 171.00, 180.00}}; // 40 bins

    std::vector<std::vector<double>> Bin_SplitZ = {{1.00, 1.30, 1.80, 4.10},
                                                   {2.20, 3.20, 3.70, 4.20},
                                                   {0.00, 0.15, 0.25, 0.40, 0.70, 0.90, 1.00},
                                                   {0.00, 0.03, 0.06, 0.10, 0.18, 1.00},
                                                   {-180.00, -171.00, -162.00, -153.00, -144.00, -135.00, -126.00, -117.00, -108.00, -99.00,
                                                     -90.00,  -81.00,  -72.00,  -63.00,  -54.00,  -45.00,  -36.00,  -27.00,  -18.00,  -9.00,
                                                       0.00,    9.00,   18.00,   27.00,   36.00,   45.00,   54.00,   63.00,   72.00,  81.00,
                                                      90.00,   99.00,  108.00,  117.00,  126.00,  135.00,  144.00,  153.00,  162.00, 171.00, 180.00}}; // 40 bins


    std::vector<std::vector<std::vector<double>>> Bin_List = {Bin_Origin, Bin_SplitZ};

    namespace Correction
    {
      // This map uses _binNdims as input, and says if the final bins need to be redefined (irregular = 1) or remain regular (i.e. same length each = 0)
      std::map<int,std::vector<int>> NIrregBins = {{2,{1,1,0,0,0}}, {3,{1,1,1,0,0}}};
    }
}

#endif
