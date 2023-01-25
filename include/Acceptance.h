#ifndef Acceptance_h
#define Acceptance_h

#include "Cuts.h"
#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include <iostream>
#include "vector"
#include "string"

class Acceptance
{
private:
    std::string _nameFormatted = "";
    int _targTypeCut = 1;
    std::string _nameTarget;
    std::string _nameSolidTarget = "";
    bool _useFullError = false;
    bool _isData = false;
    bool _isClosureTest = false;
    int _binIndex = -1;
    int _binNdims = 0; // 2: Leptonic, 3: Leptonic+Zh
    int _useNu = true;
    int _useXb = false; // !_useNu
    bool _cutXf = false;
    bool _cutDeltaSector0 = false;
    bool _cutBadSector = false;
    bool _cutPiFiducial = false;
    int _count = 0; // Usefull for debug

public: // Internal values
    void setTargTypeCut(size_t targTypeCut) { _targTypeCut = targTypeCut; }
    std::string getNameTarget() { return _nameTarget; }
    void setFullError() { _useFullError = true; }
    void setDataType() { _isData = true; }
    void setClosureTest() { _isClosureTest = true; }
    void setBinningType(int binning_number) { _binIndex = binning_number; }
    void setBinNdims(int binningNdims) { _binNdims = binningNdims; }

public: // Cuts
    void useCut_Xf() { _cutXf = true; }
    void useCut_DeltaSector0() { _cutDeltaSector0 = true; }
    void useCut_rmBadSector() { _cutBadSector = true; }
    void useCut_PiFiducial() { _cutPiFiducial = true; }

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

    Acceptance(TTree *tree = 0, bool isData = false);
    virtual ~Acceptance();
    virtual void setTargName(std::string name);
    std::string getFoldNameExt();
    virtual void setNameFormat();
    std::string getAccFoldNameExt();
    std::string getAccFileName();
    virtual Int_t Cut(Long64_t entry);
    virtual Bool_t GoodElectron_MC(Long64_t entry, vector<vector<double>> DISLimits);
    virtual Bool_t GoodPiPlus_MC(Long64_t entry, int ivec, vector<vector<double>> DISLimits);
    virtual Bool_t GoodElectron(Long64_t entry, vector<vector<double>> DISLimits);
    virtual Bool_t GoodPiPlus(Long64_t entry, int ivec, vector<vector<double>> DISLimits);
    virtual Int_t GetEntry(Long64_t entry);
    virtual Long64_t LoadTree(Long64_t entry);
    virtual void Init(TTree *tree);
    virtual void ActivateBranches();
    virtual void ActivateCuts(std::string);
    virtual void Loop();
    virtual void Hist2D_KinVars();
    virtual void Hist2D_XfVsYh();
    virtual void Hist2D_ThetaPQ();
    virtual void Hist2D_LabAngles();
    virtual void Hist2D_PQVsLab();
    virtual void Hist2D_PQVsSector();
    virtual void Hist2D_PQVsDeltaSector();
    virtual void Hist2D_VarsVsXb();
    virtual void Correction();
    virtual void ClosureTest();
    virtual Bool_t Notify();
    virtual void Show(Long64_t entry = -1);
};

#endif // #ifndef Acceptance_h

#ifdef Acceptance_cxx
Acceptance::Acceptance(TTree *tree, bool isData) : fChain(0), _nameTarget("D")
{
    // if parameter tree is not specified (or zero), connect the file
    // used to generate this class and read the Tree.
    if (tree == 0)
    {
        TFile *f = (TFile *)gROOT->GetListOfFiles()->FindObject("hsim_D1.root");
        if (!f || !f->IsOpen())
        {
            f = new TFile("hsim_D1.root");
        }
        f->GetObject("ntuple_sim", tree);
    }
    if (isData) setDataType();
    Init(tree);
}

Acceptance::~Acceptance()
{
    if (!fChain)
        return;
    delete fChain->GetCurrentFile();
}

Int_t Acceptance::GetEntry(Long64_t entry)
{
    // Read contents of entry.
    if (!fChain)
        return 0;
    return fChain->GetEntry(entry);
}

Long64_t Acceptance::LoadTree(Long64_t entry)
{
    // Set the environment to read one entry
    if (!fChain)
        return -5;
    Long64_t centry = fChain->LoadTree(entry);
    if (centry < 0)
        return centry;
    if (fChain->GetTreeNumber() != fCurrent)
    {
        fCurrent = fChain->GetTreeNumber();
        Notify();
    }
    return centry;
}

// Set Names

void Acceptance::setTargName(std::string name)
{
    if (name.find("D")!=std::string::npos)
    {
        if (name=="D" || name.find("S")!=std::string::npos) // "S" runs over all solid targets
        {
            _nameTarget = name;
        }
        else
        {
            _nameTarget = "D";
            _nameSolidTarget = name.substr(1); // Substring gets what's after "D"
        }
    }
    else
    {
        // Since "D" is not in the name, it's a solid target!
        setTargTypeCut(2); // Solid
        _nameTarget = name;
    }
}

// Folder and file names

std::string Acceptance::getFoldNameExt() //getNameAccFormat() // Cuts + other selections
{
    // _<extra cuts, ex. Xf>
    std::string this_name = getAccFoldNameExt();
    if (_useFullError)
    {
        this_name+="_FErr";
    }
    return this_name;
}

void Acceptance::setNameFormat()
{
    // <target>_<_binIndex>B<_binNdims> -> If D: DC, DFe, DPb
    _nameFormatted = _nameTarget;
    if (_nameTarget=="D" && _nameSolidTarget!="")
    {
        if (_nameSolidTarget!="All") _nameFormatted+=_nameSolidTarget;
    }
    if (_binIndex>-1)
    {
        _nameFormatted+="_"+std::to_string(_binIndex)+"B";
    }
    if (_binNdims)
    {
        _nameFormatted+=std::to_string(_binNdims);
    }
    std::cout << "Name formatted extension: " << _nameFormatted << std::endl;
}

std::string Acceptance::getAccFoldNameExt() //getNameAccFormat() // Only cuts
{
    // _<extra cuts, ex. Xf>
    std::string this_name = "";
    if (_cutXf)
    {
        this_name+="_Xf";
    }
    if (_cutDeltaSector0)
    {
        this_name+="_DSect0";
    }
    if (_cutBadSector)
    {
        this_name+="_NoBadSec";
    }
    if (_cutPiFiducial)
    {
        this_name+="_PiFid";
    }
    return this_name;
}

std::string Acceptance::getAccFileName()
{
    // <target>_<_binIndex>B
    std::string this_name = _nameTarget;
    if (_binIndex>-1)
    {
        this_name+="_"+std::to_string(_binIndex)+"B";
    }
    return this_name;
}

// Init

void Acceptance::Init(TTree *tree)
{
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
    if (!_isData)
    {
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

Bool_t Acceptance::Notify()
{
    // The Notify() function is called when a new file is opened. This
    // can be either for a new TTree in a TChain or when when a new TTree
    // is started when using PROOF. It is normally not necessary to make changes
    // to the generated code, but the routine can be extended by the
    // user if needed. The return value is currently not used.

    return kTRUE;
}

void Acceptance::Show(Long64_t entry)
{
    // Print contents of entry.
    // If entry is not specified, print current entry
    if (!fChain)
        return;
    fChain->Show(entry);
}

void Acceptance::ActivateCuts(std::string str_cuts)
{
    if (str_cuts.find("Xf")!=std::string::npos)
    {
        useCut_Xf();            std::cout << "Using Xf cut" << std::endl;
    }
    if (str_cuts.find("DS")!=std::string::npos)
    {
        useCut_DeltaSector0();  std::cout << "Using Delta Sector != 0 cut" << std::endl;
    }
    if (str_cuts.find("BS")!=std::string::npos)
    {
        useCut_rmBadSector();   std::cout << "Using rm Bad Sector (5) cut" << std::endl;
    }
    if (str_cuts.find("PF")!=std::string::npos)
    {
        useCut_PiFiducial();    std::cout << "Using Pi+ fiducial cut" << std::endl;
    }
    if (str_cuts.find("FE")!=std::string::npos)
    {
        setFullError();         std::cout << "Using full error calculation" << std::endl;
    }
}

/////////////////////////
//// Generated (MC) Cuts
/////////////////////////

Bool_t Acceptance::GoodElectron_MC(Long64_t entry, vector<vector<double>> this_limit)
{
    // This function may be called from Loop.

    bool pass_DIS = (mc_TargType==_targTypeCut && this_limit[0][0]<mc_Q2 && mc_Q2<this_limit[1][0] && mc_Yb<0.85 && mc_W>2 &&
                     this_limit[0][1]<mc_Nu && mc_Nu<this_limit[1][1]);

    return pass_DIS;
}

Bool_t Acceptance::GoodPiPlus_MC(Long64_t entry, int ivec, vector<vector<double>> this_limit)
{
    // This function may be called from Loop.

    bool pass_DIS = (mc_pid->at(ivec)==211 && this_limit[0][2]<mc_Zh->at(ivec) && mc_Zh->at(ivec)<this_limit[1][2] &&
            this_limit[0][3]<mc_Pt2->at(ivec) && mc_Pt2->at(ivec)<this_limit[1][3] && this_limit[0][4]<mc_PhiPQ->at(ivec) && mc_PhiPQ->at(ivec)<this_limit[1][4]);
    if (_cutXf)
    {
        pass_DIS = pass_DIS && pass_Xf(mc_Xf->at(ivec));
    }
    if (_cutDeltaSector0)
    {
        pass_DIS = pass_DIS && pass_DeltaSect0(mc_SectorEl, mc_Sector->at(ivec));
    }
    if (_cutBadSector)
    {
        pass_DIS = pass_DIS && pass_rmBadSect(mc_SectorEl, mc_Sector->at(ivec));
    }

    // Fiducial cuts are applied in reconstruction only, not generated!
    // if (_cutPiFiducial) pass_DIS = pass_DIS && pass_PiFiducial(mc_Sector->at(ivec), mc_P->at(ivec), mc_ThetaLab->at(ivec), mc_PhiLab->at(ivec));

    return pass_DIS;
}

/////////////////////////
//// Reconstructed Cuts
/////////////////////////

Bool_t Acceptance::GoodElectron(Long64_t entry, vector<vector<double>> this_limit)
{
    // This function may be called from Loop.

    bool pass_DIS = (TargType==_targTypeCut && this_limit[0][0]<Q2 && Q2<this_limit[1][0] && Yb<0.85 && W>2 && -1.4<vyec && vyec<1.4 &&
            this_limit[0][1]<Nu && Nu<this_limit[1][1]);

    return pass_DIS;
}

Bool_t Acceptance::GoodPiPlus(Long64_t entry, int ivec, vector<vector<double>> this_limit)
{
    // This function may be called from Loop.

    bool pass_DIS = (pid->at(ivec)==211 && this_limit[0][2]<Zh->at(ivec) && Zh->at(ivec)<this_limit[1][2] &&
            this_limit[0][3]<Pt2->at(ivec) && Pt2->at(ivec)<this_limit[1][3] && this_limit[0][4]<PhiPQ->at(ivec) && PhiPQ->at(ivec)<this_limit[1][4]);

    if (_cutXf)
    {
        pass_DIS = pass_DIS && pass_Xf(Xf->at(ivec));
    }
    if (_cutDeltaSector0)
    {
        pass_DIS = pass_DIS && pass_DeltaSect0(SectorEl, Sector->at(ivec));
    }
    if (_cutBadSector)
    {
        pass_DIS = pass_DIS && pass_rmBadSect(SectorEl, Sector->at(ivec));
    }
    if (_cutPiFiducial)
    {
        pass_DIS = pass_DIS && pass_PiFiducial(Sector->at(ivec), P->at(ivec), ThetaLab->at(ivec), PhiLab->at(ivec));
    }

    return pass_DIS;
}

Int_t Acceptance::Cut(Long64_t entry)
{
    // This function may be called from Loop.
    // returns  1 if entry is accepted.
    // returns -1 otherwise.
    return 1;
}
#endif // #ifdef Acceptance_cxx
