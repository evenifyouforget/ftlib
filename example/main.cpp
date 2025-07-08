#include <iostream>

#include "sim/fcsim.h"
#include "example_design.h"

// extremely low level (not for human use) program to run a single design, and see if it solves
int main() {
    //get the example design
    ft_design_spec design = make_the_design();

    //create the handle and setings
    std::shared_ptr<ft_sim_state> handle;
    ft_sim_settings settings;

    //initialize the handle
    handle = fcsim_new(handle, design, settings);

    //step the simulation until it solves
    while(!fcsim_is_solved(handle, design)) {
        fcsim_step(handle, settings);
    }

    //behold: a solve
    std::cout << "Design solved at " << handle->tick << " ticks" << std::endl;
    return 0;
}