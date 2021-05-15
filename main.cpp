#include <iostream>
#include <stdio.h>

#include "fileSystem.h"

using namespace std;

int main()
{
    const char* path = "vm.dat";
    int check = initialize(path);
    cout<<"check: "<<check<<endl;
    system("pause");
}