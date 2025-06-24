#ifndef Acceptance_h
#define Acceptance_h

#include "Cuts.h"
#include "Utility.h"
#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include <iostream>
#include "vector"
#include "string"

using namespace BINNING;

class Acceptance {
private:
    // Dataset info
    std::string _infoTag = "";
    std::string _infoTag_Acceptance = "";
    bool _isData = false;
    bool _useCorrectionCuts = false;
    bool _isClosureTest = false;
    int _binIndex = -1;
    int _binNdims = 0;
    std::vector<std::string> _variables = {"Q2", "Nu", "Xb", "Zh", "Pt2", "PhiPQ"};
    std::unordered_map<std::string, std::vector<double>> _limitsMap;
    std::unordered_map<std::string, double> _minimum;
    std::unordered_map<std::string, double> _maximum;
    std::vector<bool> _irregularBins;
    // Target info
    int _cut_TargType = -1;
    std::string _nameTarget;
    std::string _nameSolidTarget = "";
    // Closure Test info
    int _fractionClosureTest;
    // Cuts info
    std::vector<std::string> _cutList = {};

    int _count = 0; // Usefull for debug

public:
    TTree *fChain;  //! pointer to the analyzed TTree or TChain
    Int_t fCurrent; //! current Tree number in a TChain

    // Fixed size dimensions of array or collections stored in the TTree if any.

    // Declaration of leaf types
    Float_t Q2;
    Float_t W;
    Float_t Nu;
    Float_t Xb;
    Float_t Yb;
    Float_t vxe;
    Float_t vye;
    Float_t vze;
    Int_t SectorEl;
    Int_t TargType;
    Float_t Pex;
    Float_t Pey;
    Float_t Pez;
    Float_t Pe;
    Float_t BettaEl;
    Float_t Etote;
    Float_t Eine;
    Float_t Eoute;
    Float_t vxec;
    Float_t vyec;
    Float_t vzec;
    Float_t XECe;
    Float_t YECe;
    Float_t ZECe;
    Float_t PhiLabEl;
    Float_t ThetaLabEl;
    Float_t StatDCEl;
    Float_t DCStatusEl;
    Float_t StatECEl;
    Float_t ECStatusEl;
    Float_t TimeECEl;
    Float_t PathECEl;
    Float_t Chi2ECEl;
    Float_t StatSCEl;
    Float_t SCStatusEl;
    Float_t TimeSCEl;
    Float_t PathSCEl;
    Float_t StatCCEl;
    Float_t CCStatusEl;
    Float_t NpheEl;
    Float_t Chi2CCEl;
    Float_t StatusEl;
    Float_t NRowsDCEl;
    Float_t NRowsECEl;
    Float_t NRowsSCEl;
    Float_t NRowsCCEl;
    vector<float> *Eh;
    vector<float> *Zh;
    vector<float> *ThetaPQ;
    vector<float> *Pt2;
    vector<float> *Pl2;
    vector<float> *PhiPQ;
    vector<float> *Mx2;
    vector<float> *T;
    vector<float> *PhiLab;
    vector<float> *ThetaLab;
    vector<float> *vxh;
    vector<float> *vyh;
    vector<float> *vzh;
    vector<int> *Sector;
    vector<float> *Px;
    vector<float> *Py;
    vector<float> *Pz;
    vector<float> *P;
    vector<float> *Betta;
    vector<float> *Mass2;
    vector<float> *Etot;
    vector<float> *Ein;
    vector<float> *Eout;
    vector<float> *XEC;
    vector<float> *YEC;
    vector<float> *ZEC;
    vector<int> *pid;
    vector<float> *T4;
    vector<float> *Xf;
    vector<float> *deltaZ;
    vector<float> *StatDC;
    vector<float> *DCStatus;
    vector<float> *StatEC;
    vector<float> *ECStatus;
    vector<float> *TimeEC;
    vector<float> *PathEC;
    vector<float> *Chi2EC;
    vector<float> *StatSC;
    vector<float> *SCStatus;
    vector<float> *TimeSC;
    vector<float> *PathSC;
    vector<float> *StatCC;
    vector<float> *CCStatus;
    vector<float> *Nphe;
    vector<float> *Chi2CC;
    vector<float> *Status;
    vector<float> *NRowsDC;
    vector<float> *NRowsEC;
    vector<float> *NRowsSC;
    vector<float> *NRowsCC;
    Float_t evnt;
    Float_t mc_Q2;
    Float_t mc_W;
    Float_t mc_Nu;
    Float_t mc_Xb;
    Float_t mc_Yb;
    Float_t mc_vxe;
    Float_t mc_vye;
    Float_t mc_vze;
    Int_t mc_SectorEl;
    Int_t mc_TargType;
    Float_t mc_Pex;
    Float_t mc_Pey;
    Float_t mc_Pez;
    Float_t mc_Pe;
    Float_t mc_BettaEl;
    Float_t mc_ThetaLabEl;
    Float_t mc_PhiLabEl;
    vector<float> *mc_Eh;
    vector<float> *mc_Zh;
    vector<float> *mc_ThetaPQ;
    vector<float> *mc_Pt2;
    vector<float> *mc_Pl2;
    vector<float> *mc_PhiPQ;
    vector<float> *mc_Mx2;
    vector<float> *mc_T;
    vector<float> *mc_ThetaLab;
    vector<float> *mc_PhiLab;
    vector<float> *mc_vxh;
    vector<float> *mc_vyh;
    vector<float> *mc_vzh;
    vector<int> *mc_Sector;
    vector<float> *mc_Px;
    vector<float> *mc_Py;
    vector<float> *mc_Pz;
    vector<float> *mc_P;
    vector<float> *mc_Betta;
    vector<float> *mc_Mass2;
    vector<int> *mc_pid;
    vector<float> *mc_Xf;
    vector<float> *mc_deltaZ;

    // Declare functions
    Acceptance(TTree*, std::string, int, int, std::string, bool, bool);
    virtual ~Acceptance();
    // Set info
    virtual void set_InfoTag();
    virtual void set_TargetInfo(std::string);
    virtual void set_Cuts(std::string);
    virtual void set_Binning();
    std::string get_FormatInfoTagName();
    void set_ClosureTest(int);
    virtual Int_t Cut(Long64_t);
    virtual Bool_t GoodElectron_MC(Long64_t);
    virtual Bool_t GoodPiPlus_MC(Long64_t, int);
    virtual Bool_t GoodElectron(Long64_t);
    virtual Bool_t GoodPiPlus(Long64_t, int);
    virtual Int_t GetEntry(Long64_t);
    virtual Long64_t LoadTree(Long64_t);
    virtual void Init(TTree*);
    virtual void activateBranches();

    virtual bool cutIsUsed(std::string);
    virtual void Loop();
    virtual void Correction();
    // virtual void ClosureTest();

    virtual Bool_t Notify();
    virtual void Show(Long64_t entry = -1);
};

#endif // #ifndef Acceptance_h

#ifdef Acceptance_cxx
Acceptance::Acceptance(TTree *tree, std::string target, int Nbin, int Ndim,
                                     std::string cuts, bool isData,
                                     bool useCorrectionCuts = false)
    : fChain(0), _binIndex(Nbin), _binNdims(Ndim), _isData(isData),
    _useCorrectionCuts(useCorrectionCuts) {
    // if parameter tree is not specified (or zero), connect the file used to generate this
    // class and read the Tree.
    if (tree == 0) {
        TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("hsim_D1.root");
        if (!f || !f->IsOpen()) {
            f = new TFile("hsim_D1.root");
        }
        f->GetObject("ntuple_sim", tree);
    }
    set_TargetInfo(target);
    set_InfoTag();
    set_Cuts(cuts);
    set_Binning();
    Init(tree);

    std::cout << "Attributes in this run:" << std::endl;
    std::cout << "-----------------------" << std::endl;
    std::cout << "_infoTag: " << _infoTag << std::endl;
    std::cout << "_infoTag_Acceptance: " << _infoTag_Acceptance << std::endl;
    std::cout << "_isData: " << _isData << std::endl;
    std::cout << "_useCorrectionCuts: " << _useCorrectionCuts << std::endl;
    std::cout << "_isClosureTest: " << _isClosureTest << std::endl;
    std::cout << "_binIndex: " << _binIndex << std::endl;
    std::cout << "_binNdims: " << _binNdims << std::endl;
    std::cout << "_cut_TargType: " << _cut_TargType << std::endl;
    std::cout << "_nameTarget: " << _nameTarget << std::endl;
    std::cout << "_nameSolidTarget: " << _nameSolidTarget << std::endl;
}

Acceptance::~Acceptance() {
    if (!fChain)
        return;
    delete fChain->GetCurrentFile();
}

Int_t Acceptance::GetEntry(Long64_t entry) {
    // Read contents of entry.
    if (!fChain)
        return 0;
    return fChain->GetEntry(entry);
}

Long64_t Acceptance::LoadTree(Long64_t entry) {
    // Set the environment to read one entry
    if (!fChain)
        return -5;
    Long64_t centry = fChain->LoadTree(entry);
    if (centry < 0)
        return centry;
    if (fChain->GetTreeNumber() != fCurrent) {
        fCurrent = fChain->GetTreeNumber();
        Notify();
    }
    return centry;
}

//////////////////////////////////////////////////////////////////////////////////////////
//  Setting class attributes
//////////////////////////////////////////////////////////////////////////////////////////

void Acceptance::set_TargetInfo(std::string targetName) {
    _cut_TargType = (targetName.find("D") != std::string::npos)? 1 : 2; // D: 1; Solid: 2;
    _nameTarget = targetName;
    if ((targetName.find("D") != std::string::npos) && (targetName.size() > 1)) {
        _nameTarget = "D";
        _nameSolidTarget = targetName.substr(1); // Gets what is after "D"
    }
}

void Acceptance::set_InfoTag() {
// Info tag format: <target>_<_binIndex>B<_binNdims> ; NOTE: Deuterium shows: DC, DFe, DPb
    _infoTag = _nameTarget;
    _infoTag_Acceptance = _nameTarget;
    if ((_nameTarget == "D") && (_nameSolidTarget != ""))
        _infoTag += _nameSolidTarget;
    if (_binIndex > -1) {
        _infoTag += "_" + std::to_string(_binIndex) + "B";
        _infoTag_Acceptance += "_" + std::to_string(_binIndex) + "B";
    }
    if (_useCorrectionCuts && _binNdims)
        _infoTag += std::to_string(_binNdims);
    std::cout << "Information tag: " << _infoTag << std::endl;
}

void Acceptance::set_Binning() {
    _limitsMap = BINNING::Bin_List[_binIndex];
    for (const auto& pair : _limitsMap) {
        _minimum.insert({pair.first, pair.second.front()});
        _maximum.insert({pair.first, pair.second.back()});
    }
    _irregularBins = BINNING::irregular_axes[_binNdims];
    std::vector<std::string> temporal;
    for (const auto& var : _variables){
        if (!_limitsMap.count(var))
            continue;
        temporal.push_back(var);
    }
    _variables = temporal;
}

void Acceptance::set_Cuts(std::string str_cuts) {
    for (const std::string& cut : cutsInOrder_Acceptance) {
        if(str_cuts.find(cut) == std::string::npos)
            continue;
        cuts_LUT[cut].usingCut = true;
        _cutList.push_back(cut);
    }
    if (!_useCorrectionCuts)
        return;

    for (const std::string& cut : cutsInOrder_Correction) {
        if(str_cuts.find(cut) == std::string::npos)
            continue;
        cuts_LUT[cut].usingCut = true;
        _cutList.push_back(cut);
    }
    return;
}

void Acceptance::set_ClosureTest(int fraction = 50) {
    _isClosureTest = true;
    _fractionClosureTest = fraction;
    std::string percentage = Form("%i%%", fraction);
    std::cout << "Using " << percentage << " of simulations in Closure Test";
    std::cout << " acceptance calculation." << std::endl;
}

//////////////////////////////////////////////////////////////////////////////////////////
//  Useful functions
//////////////////////////////////////////////////////////////////////////////////////////

bool Acceptance::cutIsUsed(std::string name) {
    return (find(_cutList.begin(), _cutList.end(), name) != _cutList.end());
}

std::string Acceptance::get_FormatInfoTagName() {
    std::string formatName = Form("%s_%iB", _nameTarget.c_str(), _binIndex);
    if (_useCorrectionCuts)
        formatName += std::to_string(_binNdims);

    return formatName;
}

void Acceptance::Init(TTree *tree) {
    // The Init() function is called when the selector needs to initialize
    // a new tree or chain. Typically here the branch addresses and branch
    // pointers of the tree will be set.
    // It is normally not necessary to make changes to the generated
    // code, but the routine can be extended by the user if needed.
    // Init() will be called many times when running on PROOF
    // (once per file to be processed).

    // Set object pointer
    Eh = 0;
    Zh = 0;
    ThetaPQ = 0;
    Pt2 = 0;
    Pl2 = 0;
    PhiPQ = 0;
    Mx2 = 0;
    T = 0;
    PhiLab = 0;
    ThetaLab = 0;
    vxh = 0;
    vyh = 0;
    vzh = 0;
    Sector = 0;
    Px = 0;
    Py = 0;
    Pz = 0;
    P = 0;
    Betta = 0;
    Mass2 = 0;
    Etot = 0;
    Ein = 0;
    Eout = 0;
    XEC = 0;
    YEC = 0;
    ZEC = 0;
    pid = 0;
    T4 = 0;
    Xf = 0;
    deltaZ = 0;
    StatDC = 0;
    DCStatus = 0;
    StatEC = 0;
    ECStatus = 0;
    TimeEC = 0;
    PathEC = 0;
    Chi2EC = 0;
    StatSC = 0;
    SCStatus = 0;
    TimeSC = 0;
    PathSC = 0;
    StatCC = 0;
    CCStatus = 0;
    Nphe = 0;
    Chi2CC = 0;
    Status = 0;
    NRowsDC = 0;
    NRowsEC = 0;
    NRowsSC = 0;
    NRowsCC = 0;
    if (!_isData)
    {
        mc_Eh = 0;
        mc_Zh = 0;
        mc_ThetaPQ = 0;
        mc_Pt2 = 0;
        mc_Pl2 = 0;
        mc_PhiPQ = 0;
        mc_Mx2 = 0;
        mc_T = 0;
        mc_ThetaLab = 0;
        mc_PhiLab = 0;
        mc_vxh = 0;
        mc_vyh = 0;
        mc_vzh = 0;
        mc_Sector = 0;
        mc_Px = 0;
        mc_Py = 0;
        mc_Pz = 0;
        mc_P = 0;
        mc_Betta = 0;
        mc_Mass2 = 0;
        mc_pid = 0;
        mc_Xf = 0;
        mc_deltaZ = 0;
    }
    // Set branch addresses and branch pointers
    if (!tree)
        return;
    fChain = tree;
    fCurrent = -1;
    // fChain->SetMakeClass(1);

    fChain->SetBranchAddress("Q2", &Q2);
    fChain->SetBranchAddress("W", &W);
    fChain->SetBranchAddress("Nu", &Nu);
    fChain->SetBranchAddress("Xb", &Xb);
    fChain->SetBranchAddress("Yb", &Yb);
    fChain->SetBranchAddress("vxe", &vxe);
    fChain->SetBranchAddress("vye", &vye);
    fChain->SetBranchAddress("vze", &vze);
    fChain->SetBranchAddress("SectorEl", &SectorEl);
    fChain->SetBranchAddress("TargType", &TargType);
    fChain->SetBranchAddress("Pex", &Pex);
    fChain->SetBranchAddress("Pey", &Pey);
    fChain->SetBranchAddress("Pez", &Pez);
    fChain->SetBranchAddress("Pe", &Pe);
    fChain->SetBranchAddress("BettaEl", &BettaEl);
    fChain->SetBranchAddress("Etote", &Etote);
    fChain->SetBranchAddress("Eine", &Eine);
    fChain->SetBranchAddress("Eoute", &Eoute);
    fChain->SetBranchAddress("vxec", &vxec);
    fChain->SetBranchAddress("vyec", &vyec);
    fChain->SetBranchAddress("vzec", &vzec);
    fChain->SetBranchAddress("XECe", &XECe);
    fChain->SetBranchAddress("YECe", &YECe);
    fChain->SetBranchAddress("ZECe", &ZECe);
    fChain->SetBranchAddress("PhiLabEl", &PhiLabEl);
    fChain->SetBranchAddress("ThetaLabEl", &ThetaLabEl);
    fChain->SetBranchAddress("StatDCEl", &StatDCEl);
    fChain->SetBranchAddress("DCStatusEl", &DCStatusEl);
    fChain->SetBranchAddress("StatECEl", &StatECEl);
    fChain->SetBranchAddress("ECStatusEl", &ECStatusEl);
    fChain->SetBranchAddress("TimeECEl", &TimeECEl);
    fChain->SetBranchAddress("PathECEl", &PathECEl);
    fChain->SetBranchAddress("Chi2ECEl", &Chi2ECEl);
    fChain->SetBranchAddress("StatSCEl", &StatSCEl);
    fChain->SetBranchAddress("SCStatusEl", &SCStatusEl);
    fChain->SetBranchAddress("TimeSCEl", &TimeSCEl);
    fChain->SetBranchAddress("PathSCEl", &PathSCEl);
    fChain->SetBranchAddress("StatCCEl", &StatCCEl);
    fChain->SetBranchAddress("CCStatusEl", &CCStatusEl);
    fChain->SetBranchAddress("NpheEl", &NpheEl);
    fChain->SetBranchAddress("Chi2CCEl", &Chi2CCEl);
    fChain->SetBranchAddress("StatusEl", &StatusEl);
    fChain->SetBranchAddress("NRowsDCEl", &NRowsDCEl);
    fChain->SetBranchAddress("NRowsECEl", &NRowsECEl);
    fChain->SetBranchAddress("NRowsSCEl", &NRowsSCEl);
    fChain->SetBranchAddress("NRowsCCEl", &NRowsCCEl);
    fChain->SetBranchAddress("Eh", &Eh);
    fChain->SetBranchAddress("Zh", &Zh);
    fChain->SetBranchAddress("ThetaPQ", &ThetaPQ);
    fChain->SetBranchAddress("Pt2", &Pt2);
    fChain->SetBranchAddress("Pl2", &Pl2);
    fChain->SetBranchAddress("PhiPQ", &PhiPQ);
    fChain->SetBranchAddress("Mx2", &Mx2);
    fChain->SetBranchAddress("T", &T);
    fChain->SetBranchAddress("PhiLab", &PhiLab);
    fChain->SetBranchAddress("ThetaLab", &ThetaLab);
    fChain->SetBranchAddress("vxh", &vxh);
    fChain->SetBranchAddress("vyh", &vyh);
    fChain->SetBranchAddress("vzh", &vzh);
    fChain->SetBranchAddress("Sector", &Sector);
    fChain->SetBranchAddress("Px", &Px);
    fChain->SetBranchAddress("Py", &Py);
    fChain->SetBranchAddress("Pz", &Pz);
    fChain->SetBranchAddress("P", &P);
    fChain->SetBranchAddress("Betta", &Betta);
    fChain->SetBranchAddress("Mass2", &Mass2);
    fChain->SetBranchAddress("Etot", &Etot);
    fChain->SetBranchAddress("Ein", &Ein);
    fChain->SetBranchAddress("Eout", &Eout);
    fChain->SetBranchAddress("XEC", &XEC);
    fChain->SetBranchAddress("YEC", &YEC);
    fChain->SetBranchAddress("ZEC", &ZEC);
    fChain->SetBranchAddress("pid", &pid);
    fChain->SetBranchAddress("T4", &T4);
    fChain->SetBranchAddress("Xf", &Xf);
    fChain->SetBranchAddress("deltaZ", &deltaZ);
    fChain->SetBranchAddress("StatDC", &StatDC);
    fChain->SetBranchAddress("DCStatus", &DCStatus);
    fChain->SetBranchAddress("StatEC", &StatEC);
    fChain->SetBranchAddress("ECStatus", &ECStatus);
    fChain->SetBranchAddress("TimeEC", &TimeEC);
    fChain->SetBranchAddress("PathEC", &PathEC);
    fChain->SetBranchAddress("Chi2EC", &Chi2EC);
    fChain->SetBranchAddress("StatSC", &StatSC);
    fChain->SetBranchAddress("SCStatus", &SCStatus);
    fChain->SetBranchAddress("TimeSC", &TimeSC);
    fChain->SetBranchAddress("PathSC", &PathSC);
    fChain->SetBranchAddress("StatCC", &StatCC);
    fChain->SetBranchAddress("CCStatus", &CCStatus);
    fChain->SetBranchAddress("Nphe", &Nphe);
    fChain->SetBranchAddress("Chi2CC", &Chi2CC);
    fChain->SetBranchAddress("Status", &Status);
    fChain->SetBranchAddress("NRowsDC", &NRowsDC);
    fChain->SetBranchAddress("NRowsEC", &NRowsEC);
    fChain->SetBranchAddress("NRowsSC", &NRowsSC);
    fChain->SetBranchAddress("NRowsCC", &NRowsCC);
    fChain->SetBranchAddress("evnt", &evnt);
    if (!_isData) {
        fChain->SetBranchAddress("mc_Q2", &mc_Q2);
        fChain->SetBranchAddress("mc_W", &mc_W);
        fChain->SetBranchAddress("mc_Nu", &mc_Nu);
        fChain->SetBranchAddress("mc_Xb", &mc_Xb);
        fChain->SetBranchAddress("mc_Yb", &mc_Yb);
        fChain->SetBranchAddress("mc_vxe", &mc_vxe);
        fChain->SetBranchAddress("mc_vye", &mc_vye);
        fChain->SetBranchAddress("mc_vze", &mc_vze);
        fChain->SetBranchAddress("mc_SectorEl", &mc_SectorEl);
        fChain->SetBranchAddress("mc_TargType", &mc_TargType);
        fChain->SetBranchAddress("mc_Pex", &mc_Pex);
        fChain->SetBranchAddress("mc_Pey", &mc_Pey);
        fChain->SetBranchAddress("mc_Pez", &mc_Pez);
        fChain->SetBranchAddress("mc_Pe", &mc_Pe);
        fChain->SetBranchAddress("mc_BettaEl", &mc_BettaEl);
        fChain->SetBranchAddress("mc_ThetaLabEl", &mc_ThetaLabEl);
        fChain->SetBranchAddress("mc_PhiLabEl", &mc_PhiLabEl);
        fChain->SetBranchAddress("mc_Eh", &mc_Eh);
        fChain->SetBranchAddress("mc_Zh", &mc_Zh);
        fChain->SetBranchAddress("mc_ThetaPQ", &mc_ThetaPQ);
        fChain->SetBranchAddress("mc_Pt2", &mc_Pt2);
        fChain->SetBranchAddress("mc_Pl2", &mc_Pl2);
        fChain->SetBranchAddress("mc_PhiPQ", &mc_PhiPQ);
        fChain->SetBranchAddress("mc_Mx2", &mc_Mx2);
        fChain->SetBranchAddress("mc_T", &mc_T);
        fChain->SetBranchAddress("mc_ThetaLab", &mc_ThetaLab);
        fChain->SetBranchAddress("mc_PhiLab", &mc_PhiLab);
        fChain->SetBranchAddress("mc_vxh", &mc_vxh);
        fChain->SetBranchAddress("mc_vyh", &mc_vyh);
        fChain->SetBranchAddress("mc_vzh", &mc_vzh);
        fChain->SetBranchAddress("mc_Sector", &mc_Sector);
        fChain->SetBranchAddress("mc_Px", &mc_Px);
        fChain->SetBranchAddress("mc_Py", &mc_Py);
        fChain->SetBranchAddress("mc_Pz", &mc_Pz);
        fChain->SetBranchAddress("mc_P", &mc_P);
        fChain->SetBranchAddress("mc_Betta", &mc_Betta);
        fChain->SetBranchAddress("mc_Mass2", &mc_Mass2);
        fChain->SetBranchAddress("mc_pid", &mc_pid);
        fChain->SetBranchAddress("mc_Xf", &mc_Xf);
        fChain->SetBranchAddress("mc_deltaZ", &mc_deltaZ);
    }
    Notify();
}

Bool_t Acceptance::Notify() {
    // The Notify() function is called when a new file is opened. This
    // can be either for a new TTree in a TChain or when when a new TTree
    // is started when using PROOF. It is normally not necessary to make changes
    // to the generated code, but the routine can be extended by the
    // user if needed. The return value is currently not used.

    return kTRUE;
}

void Acceptance::Show(Long64_t entry) {
    // Print contents of entry.
    // If entry is not specified, print current entry
    if (!fChain)
        return;
    fChain->Show(entry);
}

//////////////////////////////////////////////////////////////////////////////////////////
//  Generated (MC) events selection
//////////////////////////////////////////////////////////////////////////////////////////
// TODO: REMEMBER TO CHANGE < TO <= . USING < JUST TO RECOVER WHAT WAS OBTAINED BEFORE!
Bool_t Acceptance::GoodElectron_MC(Long64_t entry) {
    std::string ref_var2 = (_limitsMap.count("Nu"))? "Nu" : "Xb";
    double mc_var2 = (_limitsMap.count("Nu"))? mc_Nu : mc_Xb;

    return (
        (mc_TargType == _cut_TargType) && // Interaction with correct target
        (mc_Yb < 0.85) && (mc_W > 2) && // Yb: Limit of P resolution; W: Avoid resonance
        (_minimum["Q2"] < mc_Q2) && (mc_Q2 < _maximum["Q2"]) && // Q2 limits
        (_minimum[ref_var2] < mc_var2) && (mc_var2 < _maximum[ref_var2]) // Nu/Xb
    );
}

Bool_t Acceptance::GoodPiPlus_MC(Long64_t entry, int ivec) {
    // Directly return false if an extra cut is under use and is not fulfilled
    if (cutIsUsed("Xf") && !pass_Xf(mc_Xf->at(ivec)))
        return false;
    if (cutIsUsed("XT") && !pass_Xf_TFR(mc_Xf->at(ivec)))
        return false;
    if (cutIsUsed("DS") && !pass_DeltaSect0(mc_SectorEl, mc_Sector->at(ivec)))
        return false;
    if (cutIsUsed("BS") && !pass_rmBadSect(mc_SectorEl, mc_Sector->at(ivec)))
        return false;
    // Note: Fiducial cuts and MirrorMatching are not applied in generated data

    return (
        (mc_pid->at(ivec) == 211) && // Is a pion+
        (_minimum["Zh"] < mc_Zh->at(ivec)) &&
            (mc_Zh->at(ivec) < _maximum["Zh"]) && // Zh limits
        (_minimum["Pt2"] < mc_Pt2->at(ivec)) &&
            (mc_Pt2->at(ivec) < _maximum["Pt2"]) && // Pt2 limits
        (_minimum["PhiPQ"] < mc_PhiPQ->at(ivec)) &&
            (mc_PhiPQ->at(ivec) < _maximum["PhiPQ"]) // PhiPQ limits
    );
}

//////////////////////////////////////////////////////////////////////////////////////////
//  Data and reconstructed events seletion
//////////////////////////////////////////////////////////////////////////////////////////

Bool_t Acceptance::GoodElectron(Long64_t entry) {
    std::string ref_var2 = (_limitsMap.count("Nu"))? "Nu" : "Xb";
    double var2 = (_limitsMap.count("Nu"))? Nu : Xb;

    return (
        (TargType == _cut_TargType) && // Interaction with correct target
        (Yb < 0.85) && (W > 2) && // Yb: Limit of P resolution; W: Avoid resonance
        (-1.4 < vyec) && (vyec < 1.4) && // Restrict vertex region
        (_minimum["Q2"] < Q2) && (Q2 < _maximum["Q2"]) && // Q2 limits
        (_minimum[ref_var2] < var2) && (var2 < _maximum[ref_var2]) // Nu/Xb limits
    );
}

Bool_t Acceptance::GoodPiPlus(Long64_t entry, int ivec) {
    // Directly return false if an extra cut is under use and is not fulfilled
    if (cutIsUsed("Xf") && !pass_Xf(Xf->at(ivec)))
        return false;
    if (cutIsUsed("XT") && !pass_Xf_TFR(Xf->at(ivec)))
        return false;
    if (cutIsUsed("DS") && !pass_DeltaSect0(SectorEl, Sector->at(ivec)))
        return false;
    if (cutIsUsed("BS") && !pass_rmBadSect(SectorEl, Sector->at(ivec)))
        return false;
    if (cutIsUsed("PF") && !pass_PiFiducial(Sector->at(ivec), P->at(ivec),
                                            ThetaLab->at(ivec), PhiLab->at(ivec)))
        return false;
    if (cutIsUsed("MM") && !pass_MirrorMatch(P->at(ivec), Nphe->at(ivec)))
        return false;
    if (cutIsUsed("M2") && !pass_MirrorMatch2(P->at(ivec), Nphe->at(ivec)))
        return false;
    if (cutIsUsed("Pe") && !pass_rmNpheElH(NpheEl, Nphe->at(ivec))) // TODO: Change name to TL: The Line
        return false;

    return (
        (pid->at(ivec) == 211) && // Is a pion+
        (_minimum["Zh"] < Zh->at(ivec)) &&
            (Zh->at(ivec) < _maximum["Zh"]) && // Zh limits
        (_minimum["Pt2"] < Pt2->at(ivec)) &&
            (Pt2->at(ivec) < _maximum["Pt2"]) && // Pt2 limits
        (_minimum["PhiPQ"] < PhiPQ->at(ivec)) &&
            (PhiPQ->at(ivec) < _maximum["PhiPQ"]) // PhiPQ limits
    );
}

Int_t Acceptance::Cut(Long64_t entry) {
    // This function may be called from Loop.
    // returns  1 if entry is accepted.
    // returns -1 otherwise.
    return 1;
}
#endif // #ifdef Acceptance_cxx
