#ifndef Style_h
#define Style_h

#include <iostream>
#include <map>

void PrintSummaryTable(std::map<std::string, unsigned int> &list, int total, std::string title)
{
    std::cout << "-------------------------------------------------------" << std::endl;
    std::cout << "||  " << title << std::endl;
    std::cout << "-------------------------------------------------------" << std::endl;
    for (auto elem : list)
    {
        printf("%-30s: %10u (%6.2f%%)\n", elem.first.c_str(), elem.second, (float)elem.second/total*100);
    }
    std::cout << "-------------------------------------------------------" << std::endl;
}

#endif // #ifdef Style_h
