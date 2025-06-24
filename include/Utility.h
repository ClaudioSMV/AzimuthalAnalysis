#ifndef Utility_h
#define Utility_h
#include <TH1.h>
#include <THnSparse.h>

#include "Cuts.h"
#include <cmath>    // for std::isnan
#include <iomanip>  // for std::fixed and std::setprecision
#include <iostream>
#include <stdlib.h>
#include <sys/stat.h>
#include <vector>
#include <unordered_map>
#include <fstream>
#include <sstream>
#include <string>

//////////////////////////////////////////////////////////////////////////////////////////
//  Files, folders, and names format
//////////////////////////////////////////////////////////////////////////////////////////

bool check_Existence(const std::string& name) { // Also works with folders!
    struct stat buffer;
    return (stat (name.c_str(), &buffer) == 0);
}

void create_Dir(std::string path) {
    int i = system(Form("mkdir -p %s",path.c_str()));
    return;
}

std::string formatCutsInName(std::vector<std::string> cuts, bool use_correction = false) {
    std::string finalName = "";
    for (const std::string& cut : cuts) {
        if (!use_correction &&
            (std::find(cutsOrder_CORR.begin(), cutsOrder_CORR.end(), cut)
                != cutsOrder_CORR.end()))
            continue;
        finalName += "_" + cuts_LUT[cut].folderName;
    }

    return finalName;
}

//////////////////////////////////////////////////////////////////////////////////////////
//  Histograms
//////////////////////////////////////////////////////////////////////////////////////////

void set_AxesBinning(THnSparse *histogram, const std::vector<std::vector<double>> ordered_limits,
    const std::vector<bool> *is_irregular) {
    int index = 0;
    for (const auto& bins : ordered_limits) {
        if (is_irregular->at(index))
            histogram->GetAxis(index)->Set((bins.size() - 1), bins.data());
        index++;
    }
}

template <class T>
std::vector<T> map_to_vector_in_order(const std::unordered_map<std::string, T>& input_map,
    const std::vector<std::string>& reference) {
    std::vector<T> output;
    for (const std::string& variable : reference)
        output.push_back(input_map.at(variable));
    return output;
}

THnSparse* create_THnSparse(TString name, const std::vector<std::vector<double>> ordered_limits,
    const std::vector<double> ordered_mins, const std::vector<double> ordered_maxs,
    const std::vector<bool> *is_irregular, TString title = "") {
    if (!title)
        title = name;
    if (!is_irregular)
        is_irregular = new std::vector<bool>(ordered_mins.size(), true);
    std::vector<int> n_bins;
    for (const auto& bins : ordered_limits)
        n_bins.push_back(bins.size() - 1);
    THnSparse* histogram =
        new THnSparseD(name, title, 5, n_bins.data(), ordered_mins.data(), ordered_maxs.data());
    set_AxesBinning(histogram, ordered_limits, is_irregular);
	histogram->Sumw2();

    return histogram;
}

pair<double, double> get_Value(std::vector<double> bin_vector, THnSparse *acceptance) {
    int bin = acceptance->GetBin(bin_vector.data());
    double value = acceptance->GetBinContent(bin);
    pair<double, double> value_error;
    if (value != 0) {
        value_error.first = value;
        value_error.second = acceptance->GetBinError(bin);
    }
    else {
        value_error.first = NAN;
        value_error.second = 0;
    }

    return value_error;
}

void correct_Histogram(std::vector<double> bin_vector, THnSparse *acceptance,
    THnSparse *histogram, bool full_error, bool quality) {
    pair<double, double> acceptance_pair = get_Value(bin_vector, acceptance);
    if (std::isnan(acceptance_pair.first) && (acceptance_pair.second == 0))
        return;

    double acceptance_value = acceptance_pair.first;
    double acceptance_error = acceptance_pair.second;

    if (quality && ((acceptance_error / acceptance_value) > 0.1))
        return;

    int bin = histogram->GetBin(bin_vector.data());
    double new_value = histogram->GetBinContent(bin) + 1. / acceptance_value;
    histogram->SetBinContent(bin, new_value);

    double new_error;
    if (full_error) {
        new_error = TMath::Sqrt(new_value / acceptance_value *
            (1 + new_value * acceptance_error * acceptance_error / acceptance_value));
    }
    else { // This assumes no correlation in event by event
        acceptance_error = TMath::Sqrt(1.0 + acceptance_error * acceptance_error /
            (acceptance_value * acceptance_value)) / acceptance_value;
        double old_error = histogram->GetBinError(bin);
        new_error = TMath::Sqrt(old_error * old_error +
            acceptance_error * acceptance_error);
    }
    histogram->SetBinError(bin, new_error);
}

//////////////////////////////////////////////////////////////////////////////////////////
//  Print messages
//////////////////////////////////////////////////////////////////////////////////////////

void print_BinsFilled(THnSparse *hSparse) {
    double fraction_filled = hSparse->GetSparseFractionBins();
    long totalBins_NoEdges = 1;
    long totalBins_WithEdges = 1;
    for (int i = 0; i < 5; i++) {
        totalBins_NoEdges *= hSparse->GetAxis(i)->GetNbins();
        totalBins_WithEdges *= hSparse->GetAxis(i)->GetNbins() + 2;
    }
    int n_filled = fraction_filled * totalBins_WithEdges;
    double percentage = 100. * n_filled / totalBins_NoEdges;
    std::cout << Form("THnSparse name: %s", hSparse->GetName()) << std::endl;
    std::cout << Form("\tFilled bins: %i (%.4f %%)", n_filled, percentage) << std::endl;
}

std::unordered_map<std::string, unsigned int> create_MapCounter() {
    std::unordered_map<std::string, unsigned int> counter;
    counter.insert({"Total_entries", 0});
    // counter.insert({"Total Generated electrons (MC)", 0});
        counter.insert({"Gen_GoodElectron", 0});
        counter.insert({"Gen_GoodElectronNOT", 0});
            counter.insert({"Gen_WrongTargType", 0});
            counter.insert({"Gen_OutDISRange", 0});
    // counter.insert({"Total Reconstructed electrons", 0});
        counter.insert({"Reco_GoodElectron", 0});
        counter.insert({"Reco_GoodElectronNOT", 0});
            counter.insert({"Reco_WrongTargType", 0});
            counter.insert({"Reco_OutVertexY", 0});
            counter.insert({"Reco_OutDISRange", 0});
    counter.insert({"Total_MatchElectrons", 0});
    counter.insert({"Total_DifferentVectorSize", 0});

    // counter.insert({"Total Generated Pi+ (MC)", 0});
    counter.insert({"Gen_Pi+Single", 0});
    counter.insert({"Gen_Pi+Two", 0});
    counter.insert({"Gen_Pi+Three+", 0});
        counter.insert({"Gen_GoodPiPlus", 0});
        counter.insert({"Gen_GoodPiPlusNOT", 0});
    // counter.insert({"Total Reconstructed Pi+", 0});
    counter.insert({"Reco_Pi+Single", 0});
    counter.insert({"Reco_Pi+Two", 0});
    counter.insert({"Reco_Pi+Three+", 0});
        counter.insert({"Reco_GoodPiPlus", 0});
        counter.insert({"Reco_GoodPiPlusNOT", 0});
    counter.insert({"Total_MatchPiPlus", 0});

    return counter;
}

//////////////////////////////////////////////////////////////////////////////////////////
//  Copy Bins info from C++ maps to Python dictionary (.py file)
//////////////////////////////////////////////////////////////////////////////////////////

// Converts a C++ vector<int> to a Python-style list string
std::string vector_to_python_list(const std::vector<double>& vec) {
    std::ostringstream oss;
    oss << "[";
    oss << std::fixed << std::setprecision(3);
    for (size_t i = 0; i < vec.size(); ++i) {
        oss << vec[i];
        if (i != vec.size() - 1) oss << ", ";
    }
    oss << "]";
    return oss.str();
}

// Converts a C++ unordered_map<string, vector<int>> to a Python-style dict string
std::string map_to_python_dict(const std::unordered_map<std::string, std::vector<double>>& m) {
    std::ostringstream oss;
    oss << "{";
    size_t count = 0;
    std::vector<std::string> ordered_variables = {"Q2", "Nu", "Xb", "Zh", "Pt2", "PhiPQ"};
    for (const auto& variable : ordered_variables) {
        if (!m.count(variable))
            continue;
        oss << "\"" << variable << "\": " << vector_to_python_list(m.at(variable));
        if (++count != m.size())
            oss << ", ";
    }
    oss << "}";
    return oss.str();
}

// Converts the full list of maps to a Python-style list of dicts
std::string to_python_literal(const std::vector<std::unordered_map<std::string, std::vector<double>>>& data) {
    std::ostringstream oss;
    oss << "List_of_binning = [\n";
    for (size_t i = 0; i < data.size(); ++i) {
        oss << "    # B" << i << "\n";
        oss << "    " << map_to_python_dict(data[i]);
        if (i != data.size() - 1) oss << ",";
        oss << "\n";
    }
    oss << "]\n";
    return oss.str();
}

// Writes the Python file only if the content has changed
void write_python_file(const std::vector<std::unordered_map<std::string, std::vector<double>>>& data) {
    std::string new_content = to_python_literal(data);

    std::ofstream out_file("../macros/Bins_testing.py");
    if (!out_file) {
        std::cerr << "Error: could not open file for writing.\n";
        return;
    }

    out_file << new_content;
    std::cout << "Python file updated.\n";
}

#endif // #ifdef Utility_h
