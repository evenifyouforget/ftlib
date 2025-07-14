#include <iostream>
#include "ftlib.hpp"

int main() {
    // input: string
    // output: double (interpreting bytes as u64)
    std::string s;
    while(std::cin >> s) {
        std::cout << _as_int(fcsim_strtod(s)) << std::endl;
    }
    return 0;
}