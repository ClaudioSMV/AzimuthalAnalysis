#ifndef Utility_h
#define Utility_h
#include <TH1.h>
#include <THnSparse.h>

#include <iostream>
#include <stdlib.h>
#include <sys/stat.h>
#include <vector>
#include <map>
#include <fstream>

// Files and folders
bool FileExists(const std::string& name) // Also works with folders
{
  struct stat buffer;
  return (stat (name.c_str(), &buffer) == 0);
}

void CreateDir(std::string path)
{
    int i = system(Form("mkdir -p %s",path.c_str()));
    return;
}

std::string cutExtension(std::string str_list, std::string dict_name[][2])
{
    std::string this_name = "";
    for(int i=0; i<20; i++)
    {
        if((str_list.find(dict_name[i][0]))!=std::string::npos && (dict_name[i][0] != ""))
        {
            this_name+="_"+dict_name[i][1];
        }
    }
    return this_name;
}

// Branches and leaves
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

void UpdateDISLimits(std::vector<std::vector<double>> &the_limits, std::vector<std::vector<double>> this_binning)
{
    int i_var = 0;
    for (auto &var_binning : this_binning)
    {
        if (the_limits[0][i_var] != var_binning.front())
        {
            the_limits[0][i_var] = var_binning.front();
        }
        if (the_limits[1][i_var] != var_binning.back())
        {
            the_limits[1][i_var] = var_binning.back();
        }

        i_var++;
    }
}

// Histograms
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

void CorrectBin(std::vector<double> this_bin, THnSparse *histAcc, THnSparse *histCorr, bool useFErr, bool useAccQlt)
{
    int binAcc = histAcc->GetBin(&this_bin[0]);
    double valueAcc = histAcc->GetBinContent(binAcc);

    if (valueAcc != 0)
    {
        double acc_error  = histAcc->GetBinError(binAcc);

        // Skip bad behaved acc values
        if (useAccQlt && ((acc_error/valueAcc)>0.1)) return;

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

// Printout messages
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

// Copy Binning from .C to .py
void SaveBinningFilePy()
{
    std::string vars[5] = {"Q","N","Z","P","I"}; // Q2, Nu, Zh, Pt2, PhiPQ
    ofstream MyWriteFile("../macros/Bins.py", std::ofstream::trunc);

    // Create a text string, which is used to output the text file
    std::string myText;
    // Read from the text file
    ifstream MyReadFile("Binning.h", std::ifstream::in);

    // Format:
    // // // B 0
    // // std::vector<std::vector<double>> Bin_Origin = {{1.00, 1.30, 1.80, 4.10}, // 3   -> Total = 9,000
    // //                                                {2.20, 3.20, 3.70, 4.20}, // 3 ...
    // //                                                {-180.00, -171.00, -162.00, -153.00, -144.00,
    // //                                                  -90.00,  -81.00,  -72.00,  -63.00,  -54.00,
    // //                                                   90.00,   99.00,  108.00,  117.00,  126.00}}; // 40 bins

    bool in_new_bin = false;
    int var_count = 0;
    bool write_bin = false;
    bool init_line = false, end_line = false;
    bool using_Xb = false;
    std::string list_line = "";
    std::vector<std::string> bin_list;

    // Use a while loop together with the getline() function to read the file line by line
    while (getline (MyReadFile, myText))
    {
        // Gets: // B 0
        if (myText.find("// B") != string::npos)
        {
            in_new_bin = true;
            var_count = 0;
            if (myText.find("Xb") != string::npos) using_Xb = true;
            else using_Xb = false;

            // Writes: "# // B 0"
            list_line+= "#" + myText + "\n";
            continue;
        }

        // Gets: std::vector<std::vector<double>> Bin_Origin = {{1.00, 1.30, 1.80, 4.10}, ...
        if (in_new_bin && myText.find("or<std::vector<double>> Bin_") != string::npos)
        {
            write_bin = true;
            in_new_bin = false;

            std::string bin_name = "";
            // Gets "Bin_Origin" (37 is the position of the "B")
            bin_name.append(myText, 37, myText.find('=')-37-1);

            // Writes: "Bin_Origin = {"
            list_line.append(bin_name);
            list_line.append(" = {");

            // Adds name of the bin to the final list
            bin_list.push_back(bin_name);
        }

        if (write_bin)
        {
            if (myText.find("{") != string::npos)
            {
                init_line = true;
            }
            if (myText.find("}") != string::npos)
            {
                end_line = true;
            }
            if (myText.find("};") != string::npos)
            {
                write_bin = false;
            }

            // Gets "  {2.20, 3.20, 3.70, 4.20}, // 3 ..."
            if (init_line && end_line)
            {
                int pos_open = myText.find_last_of("{")+1;

                // Writes: "'N': [2.20, 3.20, 3.70, 4.20]"
                std::string this_var = vars[var_count];
                if (using_Xb && var_count==1) this_var = "X";
                list_line+= "\'" + this_var + "\': [";
                list_line.append(myText, pos_open, myText.find("}")-pos_open);
                list_line.append("],\n");

                init_line = false;
                var_count++;
                end_line = false;
            }
            // Gets "  {-180.00, -171.00, -162.00, -153.00, -144.00,"
            else if (init_line)
            {
                int pos_elem = myText.find_last_of("{") +1;

                // Writes: "'I': [-180.00, -171.00, -162.00, -153.00, -144.00,"
                std::string this_var = vars[var_count];
                if (using_Xb && var_count==1) this_var = "X";
                list_line+= "\'" + this_var + "\': [";
                list_line.append(myText, pos_elem, myText.find_last_of(",")-pos_elem+1);

                init_line = false;
                var_count++;
            }
            // Gets "  (...), 108.00,  117.00,  126.00}}; // 40 bins"
            else if (end_line)
            {
                int pos_elem_in = myText.find(",") -7;

                // Writes: "'I': [-180.00, -171.00, ...,  108.00,  117.00,  126.00]"
                list_line.append(myText, pos_elem_in, myText.find("}")-pos_elem_in);
                list_line.append("],\n");

                end_line = false;
            }
            // Gets "  (...), -81.00, -72.00, -63.00, -54.00,"
            else
            {
                int pos_elem_in = myText.find(",") -7;

                // Writes: "'I': [-180.00, -171.00, ...,  -81.00, -72.00, -63.00, -54.00,"
                list_line.append(myText, pos_elem_in, myText.find_last_of(",")-pos_elem_in+1);
            }

            if (!write_bin)
            {
                list_line.append("}\n\n");
                MyWriteFile << list_line;
                list_line = "";
            }
        }
    }

    // Writes "Bin_List = [Bin_Origin, Bin_SplitZ, ..., Bin_OddPhi]"
    list_line = "Bin_List = [";
    for (auto &str : bin_list)
    {
        list_line+= str + ", ";
    }
    list_line.pop_back();
    list_line.pop_back();
    list_line+= "]\n\n";
    MyWriteFile << list_line;

    // Close the file
    MyReadFile.close();
    MyWriteFile.close();
}

#endif // #ifdef Utility_h
