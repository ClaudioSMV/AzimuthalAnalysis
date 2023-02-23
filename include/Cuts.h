#ifndef Cuts_h
#define Cuts_h
#include <TH1.h>
#include <THnSparse.h>

#include <iostream>
#include <stdlib.h>
#include <vector>


/*** PiPlus Parameters for DC Fiducial Cuts ***/

// For parameter 0 of the FidPhiMinPiPlus calculation for pi+
const Double_t kFidPar0Low0_PiPlus[6] = {25., 25., 25., 25., 25., 25.};
const Double_t kFidPar1Low0_PiPlus[6] = {-12., -12., -12., -12, -12, -12};
const Double_t kFidPar2Low0_PiPlus[6] = {1.64476, 1.51915, 1.1095, 0.977829, 0.955366, 0.969146};
const Double_t kFidPar3Low0_PiPlus[6] = {4.4, 4.4, 4.4, 4.4, 4.4, 4.4};

// For parameter 1 of the FidPhiMinPiPlus calculation for pi+
const Double_t kFidPar0Low1_PiPlus[6] = {4., 4., 2.78427, 3.58539, 3.32277, 4.};
const Double_t kFidPar1Low1_PiPlus[6] = {2., 2., 2., 1.38233, 0.0410601, 2.};
const Double_t kFidPar2Low1_PiPlus[6] = {-0.978469, -2., -1.73543, -2., -0.953828, -2.};
const Double_t kFidPar3Low1_PiPlus[6] = {0.5, 0.5, 0.5, 0.5, 0.5, 1.08576};

// For FidThetaMinPiPlus calculation for pi+
const Double_t kThetaMinPar0_PiPlus[6] = {7.00823, 5.5, 7.06596, 6.32763, 5.5, 5.5};
const Double_t kThetaMinPar1_PiPlus[6] = {0.207249, 0.1, 0.127764, 0.1, 0.211012, 0.281549};
const Double_t kThetaMinPar2_PiPlus[6] = {0.169287, 0.506354, -0.0663754, 0.221727, 0.640963, 0.358452};
const Double_t kThetaMinPar3_PiPlus[6] = {0.1, 0.1, 0.100003, 0.1, 0.1, 0.1};
const Double_t kThetaMinPar4_PiPlus[6] = {0.1, 3.30779, 4.499, 5.30981, 3.20347, 0.776161};
const Double_t kThetaMinPar5_PiPlus[6] = {-0.1, -0.651811, -3.1793, -3.3461, -1.10808, -0.462045};

// For parameter 0 of the FidPhiMaxPiPlus calculation for pi+
const Double_t kFidPar0High0_PiPlus[6] = {25., 24.8096, 24.8758, 25., 25., 25.};
const Double_t kFidPar1High0_PiPlus[6] = {-11.9735, -8., -8., -12., -8.52574, -8.};
const Double_t kFidPar2High0_PiPlus[6] = {0.803484, 0.85143, 1.01249, 0.910994, 0.682825, 0.88846};
const Double_t kFidPar3High0_PiPlus[6] = {4.40024, 4.8, 4.8, 4.4, 4.79866, 4.8};

// For parameter 1 of the FidPhiMaxPiPlus calculation for pi+
const Double_t kFidPar0High1_PiPlus[6] = {2.53606, 2.65468, 3.17084, 2.47156, 2.42349, 2.64394};
const Double_t kFidPar1High1_PiPlus[6] = {0.442034, 0.201149, 1.27519, 1.76076, 1.25399, 0.15892};
const Double_t kFidPar2High1_PiPlus[6] = {-2., -0.179631, -2., -1.89436, -2., -2.};
const Double_t kFidPar3High1_PiPlus[6] = {1.02806, 1.6, 0.5, 1.03961, 0.815707, 1.31013};


/*** PiPlus DC Fiducial Cuts ***/

Double_t FidThetaMinPiPlus(Int_t sector, float momentum)
{
    return kThetaMinPar0_PiPlus[sector] + kThetaMinPar1_PiPlus[sector] / TMath::Power(momentum, 2) +
            kThetaMinPar2_PiPlus[sector] * momentum + kThetaMinPar3_PiPlus[sector] / momentum +
            kThetaMinPar4_PiPlus[sector] * TMath::Exp(kThetaMinPar5_PiPlus[sector] * momentum);
}

Double_t FidFuncPiPlus(Int_t sector, float momentum, Int_t side, Int_t param)
{
    if (side == 0 && param == 0)
    {
        return kFidPar0Low0_PiPlus[sector] +
                kFidPar1Low0_PiPlus[sector] * TMath::Exp(kFidPar2Low0_PiPlus[sector] * (momentum - kFidPar3Low0_PiPlus[sector]));
    }
    else if (side == 1 && param == 0)
    {
        return kFidPar0High0_PiPlus[sector] +
                kFidPar1High0_PiPlus[sector] * TMath::Exp(kFidPar2High0_PiPlus[sector] * (momentum - kFidPar3High0_PiPlus[sector]));
    }
    else if (side == 0 && param == 1)
    {
        return kFidPar0Low1_PiPlus[sector] +
                kFidPar1Low1_PiPlus[sector] * momentum *
                    TMath::Exp(kFidPar2Low1_PiPlus[sector] * TMath::Power((momentum - kFidPar3Low1_PiPlus[sector]), 2));
    } else if (side == 1 && param == 1)
    {
        return kFidPar0High1_PiPlus[sector] +
                kFidPar1High1_PiPlus[sector] * momentum *
                    TMath::Exp(kFidPar2High1_PiPlus[sector] * TMath::Power((momentum - kFidPar3High1_PiPlus[sector]), 2));
    }  // closure
    return 0.0;
}

Double_t FidPhiMinPiPlus(Int_t sector, float momentum, float ThetaLab)
{
    if (ThetaLab > FidThetaMinPiPlus(sector, momentum))
    {
        return 60. * sector - FidFuncPiPlus(sector, momentum, 0, 0) *
                (1 - 1 / (1 + (ThetaLab - FidThetaMinPiPlus(sector, momentum)) / FidFuncPiPlus(sector, momentum, 0, 1)));
    }  // closure
    return 60. * sector;
}

Double_t FidPhiMaxPiPlus(Int_t sector, float momentum, float ThetaLab)
{
    if (ThetaLab > FidThetaMinPiPlus(sector, momentum))
    {
        return 60. * sector + FidFuncPiPlus(sector, momentum, 1, 0) *
                (1 - 1 / (1 + (ThetaLab - FidThetaMinPiPlus(sector, momentum)) / FidFuncPiPlus(sector, momentum, 1, 1)));
    }  // closure
    return 60. * sector;
}

Bool_t FidCheckCutPiPlus(Int_t sector, float momentum, float ThetaLab, float PhiLab)
{
    // checks DC fiducial cut for pi+
    if (ThetaLab > FidThetaMinPiPlus(sector, momentum) && PhiLab > FidPhiMinPiPlus(sector, momentum, ThetaLab) &&
        PhiLab < FidPhiMaxPiPlus(sector, momentum, ThetaLab))
    {
        return 1;
    }  // closure
    return 0;
}





/*** Pass functions definition ***/

bool pass_Xf(float this_Xf)
{
    return this_Xf > 0;
}

bool pass_DeltaSect0(float this_SectorEl, float this_SectorPi)
{
    return abs(this_SectorEl - this_SectorPi)>0;
}

bool pass_rmBadSect(float this_SectorEl, float this_SectorPi)
{
    return ((this_SectorEl != 5) && (this_SectorPi != 5));
}

bool pass_PiFiducial(int sector, float momentum, float ThetaLab, float PhiLab)
{
    return FidCheckCutPiPlus(sector, momentum, ThetaLab, PhiLab);
}

bool pass_MirrorMatch(float momentum, float Nph)
{
    return ((momentum < 2.7 && Nph < 25) || (momentum > 2.7));
}

/*** Cut name info ***/

// Add cuts in pairs with short name first and folder name next {XX, XXXXX}
std::string lookuptable_cutAcc[10][2] = {{"Xf","Xf"}, {"DS","DSect0"}, {"BS","NoBadSec"}, {"PF","PiFid"}, {"MM","MMtch"}};
std::string lookuptable_cutCor[10][2] = {{"FE","FErr"}};

#endif // #ifdef Cuts_h
