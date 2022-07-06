#ifndef Utility_h
#define Utility_h
#include <TH1.h>

#include <iostream>
#include <vector>

int VarPosition(double var, std::vector<double> *var_limits)
{
	for (int ivar=0; ivar<(var_limits->size()-1); ivar++)
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
    double nVars = var_values->size();
    double total_size = 1;
    for (int i=0; i<nVars; i++)
    {
        total_size*=((var_limits->at(i)).size()-1);
    }
    for (int i=0; i<nVars; i++)
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

std::vector<TH1D*> CreateQ2NuHistList(int NQ2, int NNu, std::string name)
{
    std::vector<TH1D*> Vector_tmp;
    TH1D* hist_tmp;
    for (int iQ2=0; iQ2<NQ2; iQ2++)
    {
        for (int iNu=0; iNu<NNu; iNu++)
        {
            hist_tmp = new TH1D(Form("%s_Q2%iNu%i",name.c_str(),iQ2,iNu), Form("%s_Q2%iNu%i",name.c_str(),iQ2,iNu), 180, -180., 180.);
            Vector_tmp.push_back(hist_tmp);
        }
    }
    return Vector_tmp;
}

#endif // #ifdef Utility_h
