#include <iostream>

#include "sim/fcsim.h"

int main() {
    fcsim_rect rect{0.5, 0.5, 1.5, 1.5};
    std::cout << rect.x << " " << rect.y << " " << rect.w << " " << rect.h << "\n";
}