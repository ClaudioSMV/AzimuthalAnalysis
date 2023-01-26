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
    // Xb {0.11, 0.56}

    // Ordered always following: Q2, Nu, Zh, Pt2, PhiPQ
    // B 0
    std::vector<std::vector<double>> Bin_Origin = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 9,000
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.00, 0.15, 0.25, 0.40, 0.70, 1.00}, // 5
                                                   {0.00, 0.03, 0.06, 0.10, 0.18, 1.00}, // 5
                                                   {-180.00, -171.00, -162.00, -153.00, -144.00, -135.00, -126.00, -117.00, -108.00, -99.00,
                                                     -90.00,  -81.00,  -72.00,  -63.00,  -54.00,  -45.00,  -36.00,  -27.00,  -18.00,  -9.00,
                                                       0.00,    9.00,   18.00,   27.00,   36.00,   45.00,   54.00,   63.00,   72.00,  81.00,
                                                      90.00,   99.00,  108.00,  117.00,  126.00,  135.00,  144.00,  153.00,  162.00, 171.00, 180.00}}; // 40 bins

    // B 1
    std::vector<std::vector<double>> Bin_SplitZ = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 10,800
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.00, 0.15, 0.25, 0.40, 0.70, 0.90, 1.00}, // 6
                                                   {0.00, 0.03, 0.06, 0.10, 0.18, 1.00}, // 5
                                                   {-180.00, -171.00, -162.00, -153.00, -144.00, -135.00, -126.00, -117.00, -108.00, -99.00,
                                                     -90.00,  -81.00,  -72.00,  -63.00,  -54.00,  -45.00,  -36.00,  -27.00,  -18.00,  -9.00,
                                                       0.00,    9.00,   18.00,   27.00,   36.00,   45.00,   54.00,   63.00,   72.00,  81.00,
                                                      90.00,   99.00,  108.00,  117.00,  126.00,  135.00,  144.00,  153.00,  162.00, 171.00, 180.00}}; // 40 bins

    // B 2
    std::vector<std::vector<double>> Bin_ThinZh = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 18,000
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00}, // 10
                                                   {0.00, 0.03, 0.06, 0.10, 0.18, 1.00}, // 5
                                                   {-180.00, -171.00, -162.00, -153.00, -144.00, -135.00, -126.00, -117.00, -108.00, -99.00,
                                                     -90.00,  -81.00,  -72.00,  -63.00,  -54.00,  -45.00,  -36.00,  -27.00,  -18.00,  -9.00,
                                                       0.00,    9.00,   18.00,   27.00,   36.00,   45.00,   54.00,   63.00,   72.00,  81.00,
                                                      90.00,   99.00,  108.00,  117.00,  126.00,  135.00,  144.00,  153.00,  162.00, 171.00, 180.00}}; // 40 bins

    // B 3
    std::vector<std::vector<double>> Bin_ThinPt = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 15,120
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.00, 0.15, 0.25, 0.40, 0.70, 0.90, 1.00}, // 6
                                                   {0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0}, // 7
                                                   {-180.00, -171.00, -162.00, -153.00, -144.00, -135.00, -126.00, -117.00, -108.00, -99.00,
                                                     -90.00,  -81.00,  -72.00,  -63.00,  -54.00,  -45.00,  -36.00,  -27.00,  -18.00,  -9.00,
                                                       0.00,    9.00,   18.00,   27.00,   36.00,   45.00,   54.00,   63.00,   72.00,  81.00,
                                                      90.00,   99.00,  108.00,  117.00,  126.00,  135.00,  144.00,  153.00,  162.00, 171.00, 180.00}}; // 40 bins

    // B 4
    std::vector<std::vector<double>> Bin_ThinZP = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 25,200
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00}, // 10
                                                   {0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0}, // 7
                                                   {-180.00, -171.00, -162.00, -153.00, -144.00, -135.00, -126.00, -117.00, -108.00, -99.00,
                                                     -90.00,  -81.00,  -72.00,  -63.00,  -54.00,  -45.00,  -36.00,  -27.00,  -18.00,  -9.00,
                                                       0.00,    9.00,   18.00,   27.00,   36.00,   45.00,   54.00,   63.00,   72.00,  81.00,
                                                      90.00,   99.00,  108.00,  117.00,  126.00,  135.00,  144.00,  153.00,  162.00, 171.00, 180.00}}; // 40 bins

    // B 5
    std::vector<std::vector<double>> Bin_ThinZh_CoarsePhi = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 9,000
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00}, // 10
                                                   {0.00, 0.03, 0.06, 0.10, 0.18, 1.00}, // 5
                                                   {-180.00, -162.00, -144.00, -126.00, -108.00, -90.00, -72.00, -54.00, -36.00, -18.00, 0.00,
                                                     18.00, 36.00, 54.00, 72.00, 90.00, 108.00, 126.00, 144.00, 162.00, 180.00}}; // 20 bins

    // B 6
    std::vector<std::vector<double>> Bin_ThinZP_CoarsePhi = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 12,600
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00}, // 10
                                                   {0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0}, // 7
                                                   {-180.00, -162.00, -144.00, -126.00, -108.00, -90.00, -72.00, -54.00, -36.00, -18.00, 0.00,
                                                     18.00, 36.00, 54.00, 72.00, 90.00, 108.00, 126.00, 144.00, 162.00, 180.00}}; // 20 bins

    // B 7
    std::vector<std::vector<double>> Bin_ThinZP_OddPhi = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 9,450
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00}, // 10
                                                   {0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0}, // 7
                                                   {-180.00, -156.00, -132.00, -108.00, -84.00, -60.00, -36.00, -12.00, 12.00, 36.00, 60.00,
                                                      84.00, 108.00, 132.00, 156.00, 180.00}}; // 15 bins

    // B 8
    std::vector<std::vector<double>> Bin_ThinZHighP_OddPhi = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 12,150
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00}, // 10
                                                   {0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0, 1.7, 3.0}, // 9
                                                   {-180.00, -156.00, -132.00, -108.00, -84.00, -60.00, -36.00, -12.00, 12.00, 36.00, 60.00,
                                                      84.00, 108.00, 132.00, 156.00, 180.00}}; // 15 bins

    // B 9
    std::vector<std::vector<double>> Bin_ThinZPeakP_OddPhi = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 13,500
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00}, // 10
                                                   {0.027, 0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0, 1.7, 3.0}, // 10
                                                   {-180.00, -156.00, -132.00, -108.00, -84.00, -60.00, -36.00, -12.00, 12.00, 36.00, 60.00,
                                                      84.00, 108.00, 132.00, 156.00, 180.00}}; // 15 bins

    // B 10
    std::vector<std::vector<double>> Bin_CoarseOddPhi = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 6,552
                                                   {2.20, 3.20, 3.70, 4.20}, // 3
                                                   {0.10, 0.22, 0.32, 0.40, 0.50, 0.60, 0.75, 0.85, 1.00}, // 8
                                                   {0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.2}, // 7
                                                   {-180.00, -152.31, -124.62, -96.92, -69.23, -41.54, -13.85, 13.85, 41.54, 69.23, 96.92,
                                                     124.62, 152.31, 180.00}}; // 13 bins

    // B 11
    std::vector<std::vector<double>> Bin_Xb_B10 = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 6,552
                                                   {0.110, 0.220, 0.290, 0.56}, // 3 Xb
                                                   {0.10, 0.22, 0.32, 0.40, 0.50, 0.60, 0.75, 0.85, 1.00}, // 8
                                                   {0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.2}, // 7
                                                   {-180.00, -152.31, -124.62, -96.92, -69.23, -41.54, -13.85, 13.85, 41.54, 69.23, 96.92,
                                                     124.62, 152.31, 180.00}}; // 13 bins

    // // TEST BINNING WITH MORE BINS IN Q2 AND NU
    // std::vector<std::vector<double>> Bin_ThinZPeakP_OddPhi = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 13,500
    //                                                {2.20, 3.20, 3.70, 4.20}, // 3
    //                                                {0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00}, // 10
    //                                                {0.027, 0.047, 0.073, 0.112, 0.173, 0.267, 0.411, 0.633, 1.0, 1.7, 3.0}, // 10
    //                                                {-180.00, -156.00, -132.00, -108.00, -84.00, -60.00, -36.00, -12.00, 12.00, 36.00, 60.00,
    //                                                   84.00, 108.00, 132.00, 156.00, 180.00}}; // 15 bins

    // 0.047 cut in Pt2 removes the initial peak near 0 and the next peak. Is that ok?

    std::vector<std::vector<std::vector<double>>> Bin_List = {Bin_Origin, Bin_SplitZ, Bin_ThinZh, Bin_ThinPt, Bin_ThinZP, Bin_ThinZh_CoarsePhi,
                                                              Bin_ThinZP_CoarsePhi, Bin_ThinZP_OddPhi, Bin_ThinZHighP_OddPhi, Bin_ThinZPeakP_OddPhi,
                                                              Bin_CoarseOddPhi};

    namespace Correction
    {
      // This map uses _binNdims as input, and says if the final bins need to be redefined (irregular = 1) or remain regular (i.e. same length each = 0)
      // This should be related to what is known as Unbinned Acceptance Correction
      // As far as I know, setting all bins irregular (use 1 option) should be equivalent to use Binned Acceptance Correction
      std::map<int,std::vector<int>> NIrregBins = {{1,{1,1,1,1,1}}, {2,{1,1,0,0,0}}, {3,{1,1,1,0,0}}};
    }
}

#endif
