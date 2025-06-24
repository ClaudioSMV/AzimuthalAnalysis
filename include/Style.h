#ifndef Style_h
#define Style_h

#include <iostream>
#include <fstream>
#include <unordered_map>
#include <string>


void write_line(std::ofstream& outFile, std::string title, unsigned int n_events,
    unsigned int total = 0) {
    double percentage = (total > 0)? 100. * n_events / total : 0.0;
    std::string line = Form("%-45s: %10u", title.c_str(), n_events);
    if (percentage)
        line += Form(" out of %10u (%6.2f%%)", total, percentage);
    std::cout << line << "\n";
    outFile << line << "\n";
    return;
}

void print_EventSummary(const std::string& filename,
    const std::unordered_map<std::string, unsigned int>& counterMap) {
    std::ofstream outFile(filename);

    if (!outFile.is_open()) {
        std::cerr << "Error opening file: " << filename << "\n";
        return;
    }

    std::cout << "---------------------\n-- General summary --\n---------------------\n\n";
    outFile << "---------------------\n-- General summary --\n---------------------\n\n";
    write_line(outFile, "Total entries", counterMap.at("Total_entries"));

    std::cout << "\n-- Electron information\n-----------------------\n\n";
    outFile << "\n-- Electron information\n-----------------------\n\n";
    write_line(outFile, "Generated accepted Electrons",
        counterMap.at("Gen_GoodElectron"), counterMap.at("Total_entries"));
    write_line(outFile, "Generated rejected Electrons",
        counterMap.at("Gen_GoodElectronNOT"), counterMap.at("Total_entries"));

    write_line(outFile, "        Wrong TargType",
        counterMap.at("Gen_WrongTargType"), counterMap.at("Gen_GoodElectronNOT"));
    write_line(outFile, "        Out of DIS range",
        counterMap.at("Gen_OutDISRange"), counterMap.at("Gen_GoodElectronNOT"));

    write_line(outFile, "Reconstructed accepted Electrons",
        counterMap.at("Reco_GoodElectron"), counterMap.at("Total_entries"));
    write_line(outFile, "Reconstructed rejected Electrons",
        counterMap.at("Reco_GoodElectronNOT"), counterMap.at("Total_entries"));

    write_line(outFile, "        Wrong TargType",
        counterMap.at("Reco_WrongTargType"), counterMap.at("Reco_GoodElectronNOT"));
    write_line(outFile, "        Outside VertexY",
        counterMap.at("Reco_OutVertexY"), counterMap.at("Reco_GoodElectronNOT"));
    write_line(outFile, "        Out of DIS range",
        counterMap.at("Reco_OutDISRange"), counterMap.at("Reco_GoodElectronNOT"));

    write_line(outFile, "Matching Electrons (Gen & Reco)",
        counterMap.at("Total_MatchElectrons"), counterMap.at("Total_entries"));
    write_line(outFile, "Different vector size",
        counterMap.at("Total_DifferentVectorSize"), counterMap.at("Total_entries"));

    std::cout << "\n-- PiPlus information\n---------------------\n\n";
    outFile << "\n-- PiPlus information\n---------------------\n\n";
    write_line(outFile, "Generated accepted Pi+", counterMap.at("Gen_GoodPiPlus"));
    write_line(outFile, "        Single Pi+",
        counterMap.at("Gen_Pi+Single"), counterMap.at("Gen_GoodPiPlus"));
    write_line(outFile, "        Two Pi+",
        counterMap.at("Gen_Pi+Two"), counterMap.at("Gen_GoodPiPlus"));
    write_line(outFile, "        Three or more Pi+",
        counterMap.at("Gen_Pi+Three+"), counterMap.at("Gen_GoodPiPlus"));
    write_line(outFile, "Generated rejected Pi+", counterMap.at("Gen_GoodPiPlusNOT"));

    write_line(outFile, "Reconstructed accepted Pi+", counterMap.at("Reco_GoodPiPlus"));
    write_line(outFile, "        Single Pi+",
        counterMap.at("Reco_Pi+Single"), counterMap.at("Reco_GoodPiPlus"));
    write_line(outFile, "        Two Pi+",
        counterMap.at("Reco_Pi+Two"), counterMap.at("Reco_GoodPiPlus"));
    write_line(outFile, "        Three or more Pi+",
        counterMap.at("Reco_Pi+Three+"), counterMap.at("Reco_GoodPiPlus"));
    write_line(outFile, "Reconstructed rejected Pi+", counterMap.at("Reco_GoodPiPlusNOT"));
    write_line(outFile, "Matching Pi+ (Gen & Reco)", counterMap.at("Total_MatchPiPlus"));

    outFile.close();
}

#endif // #ifdef Style_h
