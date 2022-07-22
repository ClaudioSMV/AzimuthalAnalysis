#ifndef Utility_h
#define Utility_h
#include <TH1.h>
#include <THnSparse.h>

#include <iostream>
#include <vector>

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

template<class T, typename... Args> std::vector<T*> CreateQ2NuHistList(int NQ2, int NNu, std::string name, Args... args)
{
    std::vector<T*> Vector_tmp;
    T* hist_tmp;
    for (int iQ2=0; iQ2<NQ2; iQ2++)
    {
        for (int iNu=0; iNu<NNu; iNu++)
        {
            hist_tmp = new T(Form("%s_Q%iN%i",name.c_str(),iQ2,iNu), Form("%s_Q%iN%i",name.c_str(),iQ2,iNu), args...);
            Vector_tmp.push_back(hist_tmp);
        }
    }
    return Vector_tmp;
}

void SetVariableSize(THnSparse *hist, Int_t nbins[], Double_t Q2_limits[], Double_t Nu_limits[],
					Double_t Zh_limits[], Double_t Pt2_limits[], Double_t PhiPQ_limits[])
{
	hist->GetAxis(0)->Set(nbins[0], Q2_limits);
	hist->GetAxis(1)->Set(nbins[1], Nu_limits);
	hist->GetAxis(2)->Set(nbins[2], Zh_limits);
	hist->GetAxis(3)->Set(nbins[3], Pt2_limits);
	hist->GetAxis(4)->Set(nbins[4], PhiPQ_limits);
}

#endif // #ifdef Utility_h
