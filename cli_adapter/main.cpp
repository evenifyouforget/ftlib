#include <iostream>
#include <cstdint>
#include "ftsim.h"

std::istream& operator>>(std::istream& is, ft_block_spec& block) {
    int64_t block_type;
    is >> block_type >> block.id >> block.x >> block.y >> block.w >> block.h >> block.angle >> block.joints[0] >> block.joints[1];
    block.type = static_cast<ft_piece_type::type>(block_type);
    return is;
}

std::istream& operator>>(std::istream& is, ft_rect& rect) {
    return is >> rect.x >> rect.y >> rect.w >> rect.h;
}

std::istream& operator>>(std::istream& is, ft_design_spec& design) {
    int64_t num_blocks;
    is >> num_blocks;
    for(int64_t i = 0; i < num_blocks; ++i) {
        ft_block_spec block;
        is >> block;
        design.blocks.push_back(block);
    }
    is >> design.build >> design.goal;
    return is;
}

// extremely low level (not for human use) program to run a single design, and see if it solves
int main() {
    // read parameters from stdin
    int64_t max_ticks;
    std::cin >> max_ticks;
    // read design data from stdin
    ft_design_spec spec;
    std::cin >> spec;
    ft_design design = ft_create_design(spec);

    // run up to max ticks
    ft_sim_settings settings;
    ft_sim_state handle = ft_create_sim(design, settings);
    
    int64_t solve_tick = -1;
    while(handle.tick != max_ticks) {
        ft_step_sim(handle, settings);
        if(ft_is_solved(handle, spec)) {
            // stop early on solve
            solve_tick = handle.tick;
            break;
        }
    }
    // print result
    std::cout << solve_tick << std::endl << handle.tick << std::endl;
    return 0;
}