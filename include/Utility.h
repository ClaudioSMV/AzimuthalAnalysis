#ifndef Utility_h
#define Utility_h
#include <TH1.h>
#include <THnSparse.h>

#include <iostream>
#include <stdlib.h>
#include <sys/stat.h>
#include <vector>
#include <map>

bool FileExists(const std::string& name) // Also works with folders
{
  struct stat buffer;
  return (stat (name.c_str(), &buffer) == 0);
}

void CreateDir(std::string path)
{
    system(Form("mkdir -p %s",path.c_str()));
}

int VarPosition(double var, std::vector<double> *var_limits)
{
	for (unsigned int ivar=0; ivar<(var_limits->size()-1); ivar++)
    {
		if (var_limits->at(ivar)<=var && var<var_limits->at(ivar+1))
        {
			return ivar;
		}
	}
	return -9999;
}

int VarPosition(double var, double var_limits[], int nlimts)
{
	for (int ivar=0; ivar<nlimts; ivar++)
    {
		if (var_limits[ivar]<=var && var<var_limits[ivar+1])
        {
			return ivar;
		}
	}
	return -9999;
}

// GlobalVarPosition() Gives the position in an ordered vector following ibin = iA + iB*Total_A + iC*Total_B*Total_A + ...
int GlobalVarPosition(std::vector<double> *var_values, std::vector<std::vector<double>> *var_limits)
{
    int global_position = 0, pos_tmp = -1;
    unsigned int nVars = var_values->size();
    double total_size = 1;
    for (unsigned int i=0; i<nVars; i++)
    {
        total_size*=((var_limits->at(i)).size()-1);
    }
    for (unsigned int i=0; i<nVars; i++)
    {
        pos_tmp = VarPosition(var_values->at(i), &(var_limits->at(i)));
        if (pos_tmp!=-9999)
        {
            total_size/=((var_limits->at(i)).size()-1);
            global_position+= pos_tmp*total_size;
        }
        else return -9999;
    }

    return global_position;
}

void SetVariableSize(THnSparse *hist, Int_t nbins[], Double_t Q2_limits[], Double_t Nu_limits[],
					Double_t Zh_limits[], Double_t Pt2_limits[], Double_t PhiPQ_limits[], std::vector<int> *IrregBinBool = NULL)
{
    std::vector<int> v_tmp = {nbins[0], nbins[1], nbins[2], nbins[3], nbins[4]};
    if (!IrregBinBool)
    {
        IrregBinBool = &v_tmp;
    }
	if(IrregBinBool->at(0)) hist->GetAxis(0)->Set(nbins[0], Q2_limits);
	if(IrregBinBool->at(1)) hist->GetAxis(1)->Set(nbins[1], Nu_limits);
	if(IrregBinBool->at(2)) hist->GetAxis(2)->Set(nbins[2], Zh_limits);
	if(IrregBinBool->at(3)) hist->GetAxis(3)->Set(nbins[3], Pt2_limits);
	if(IrregBinBool->at(4)) hist->GetAxis(4)->Set(nbins[4], PhiPQ_limits);
}

THnSparse* CreateFinalHist(TString name, int nbins[], std::vector<int> *reBinBool, std::vector<std::vector<double>> thisBinning, vector<vector<double>> DISLimits)
{
    int nbins_tmp[] = {10,10,10,10,40};
    for (unsigned int b=0; b<(reBinBool->size()); b++)
    {
        if ((reBinBool->at(b))!=0) nbins_tmp[b] = nbins[b];
    }

    THnSparse* hist_tmp = new THnSparseD(name,name, 5,nbins_tmp,&DISLimits[0][0],&DISLimits[1][0]);

    Double_t *Q2_Lmts    = &thisBinning[0][0];
	Double_t *Nu_Lmts    = &thisBinning[1][0];
	Double_t *Zh_Lmts    = &thisBinning[2][0];
	Double_t *Pt2_Lmts   = &thisBinning[3][0];
    Double_t *PhiPQ_Lmts = &thisBinning[4][0];

    SetVariableSize(hist_tmp, nbins, Q2_Lmts, Nu_Lmts, Zh_Lmts, Pt2_Lmts, PhiPQ_Lmts, reBinBool);

	hist_tmp->Sumw2();
    return hist_tmp;
}

void PrintFilledBins(THnSparse *hSparse)
{
    double fracFilled = hSparse->GetSparseFractionBins();

    long nBins_noEdges = 1;
    long nBins_withEdges = 1;

    for (int i=0; i<5; i++)
    {
        nBins_noEdges *= hSparse->GetAxis(i)->GetNbins();
        nBins_withEdges *= hSparse->GetAxis(i)->GetNbins() + 2;
    }

    std::cout << Form("THnSparse name: %s", hSparse->GetName()) << std::endl;
    std::cout << Form("\tFilled bins: %i (%.4f %%)", (int)(fracFilled*nBins_withEdges), 100*fracFilled*nBins_withEdges/nBins_noEdges) << std::endl;
}

pair<double, double> GetCorrectValue(std::vector<double> this_bin, THnSparse *histAcc)
{
    int binAcc = histAcc->GetBin(&this_bin[0]);
    double acc_value = histAcc->GetBinContent(binAcc);
    pair<double, double> this_pair;

    if (acc_value != 0)
    {
        double acc_error  = histAcc->GetBinError(binAcc);
        this_pair.first = acc_value;
        this_pair.second = acc_error;
    }
    return this_pair;
}

void CorrectBin(std::vector<double> this_bin, THnSparse *histAcc, THnSparse *histCorr, bool useFErr)
{
    int binAcc = histAcc->GetBin(&this_bin[0]);
    double valueAcc = histAcc->GetBinContent(binAcc);

    if (valueAcc != 0)
    {
        double acc_error  = histAcc->GetBinError(binAcc);
        int binCorr = histCorr->GetBin(&this_bin[0]);
        double this_content = histCorr->GetBinContent(binCorr) + 1./valueAcc;
        histCorr->SetBinContent(binCorr, this_content);

        // Get error propagation
        if (useFErr)
        {
            double this_error = TMath::Sqrt(this_content / valueAcc * (1 + this_content*acc_error*acc_error/valueAcc));

            histCorr->SetBinError(binCorr, this_error);
        }
        else
        {
            acc_error = TMath::Sqrt(1.0 + acc_error*acc_error/(valueAcc*valueAcc))/valueAcc;
            double old_error = histCorr->GetBinError(binCorr);
            // Assuming no correlation in event by event
            double this_error = TMath::Sqrt(old_error*old_error + acc_error*acc_error);

            histCorr->SetBinError(binCorr, this_error);
        }
    }
}

#endif // #ifdef Utility_h
