#ifndef Style_h
#define Style_h

#include <iostream>
#include <map>

void PrintSummaryTable(std::map<std::string, unsigned int> &list, std::string title, int total=0)
{
    std::cout << "----------------------------------------------------------------------" << std::endl;
    std::cout << "||  " << title << std::endl;
    std::cout << "----------------------------------------------------------------------" << std::endl;
    for (auto elem : list)
    {
        if (total!=0)   printf("%-30s: %10u out of %10i (%6.2f%%)\n", elem.first.c_str(), elem.second, total, (float)elem.second/total*100);
        else            printf("%-30s: %10u\n", elem.first.c_str(), elem.second);
    }
    std::cout << "----------------------------------------------------------------------" << std::endl;
}

#endif // #ifdef Style_h
