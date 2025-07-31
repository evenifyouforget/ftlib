#include <iostream>

#include "sim/ftsim.h"
#include "example_design.h"

void print_design(const ft_design& design) {

    printf("LEVEL BLOCKS:\n");
    for(const auto& block : design.level_blocks) {
        printf("\tidx: %d, type: %d, x: %f, y: %f, w: %f, h: %f, angle: %f,"
            " joint_stack_idxs: {%d, %d, %d, %d, %d}, joint_idxs: {%d, %d, %d, %d, %d}\n",
            block.block_idx,
            block.type,
            block.x,
            block.y,
            block.w,
            block.h,
            block.angle,
            block.joint_stack_idxs[0], block.joint_stack_idxs[1], block.joint_stack_idxs[2], block.joint_stack_idxs[3], block.joint_stack_idxs[4], 
            block.joint_idxs[0], block.joint_idxs[1], block.joint_idxs[2], block.joint_idxs[3], block.joint_idxs[4]);
    }
    
    printf("DESIGN BLOCKS:\n");
    for(const auto& block : design.design_blocks) {
        printf("\tidx: %d, type: %d, x: %f, y: %f, w: %f, h: %f, angle: %f,"
            " joint_stack_idxs: {%d, %d, %d, %d, %d}, joint_idxs: {%d, %d, %d, %d, %d}\n",
            block.block_idx,
            block.type,
            block.x,
            block.y,
            block.w,
            block.h,
            block.angle,
            block.joint_stack_idxs[0], block.joint_stack_idxs[1], block.joint_stack_idxs[2], block.joint_stack_idxs[3], block.joint_stack_idxs[4], 
            block.joint_idxs[0], block.joint_idxs[1], block.joint_idxs[2], block.joint_idxs[3], block.joint_idxs[4]);
    }

    printf("JOINTS:\n");
    for(size_t i = 0; i < design.joint_stacks.size(); i++) {
        const ft_joint_stack& js = design.joint_stacks[i];
        printf("\tjoint stack: id: %lu, x: %f, y: %f\n", js.joint_stack_idx, js.x, js.y);
        for(const auto& joint : js.joints) {
            printf("\t\tblock_idx: %d, joint_stack_idx: %d, joint_idx: %d\n", joint.block_idx, joint.joint_stack_idx, joint.joint_idx);
        }
    }

    printf("BUILD: x: %f, y: %f, w: %f, h: %f\n",
        design.build.x, design.build.y, design.build.w, design.build.h);
    
    printf("GOAL: x: %f, y: %f, w: %f, h: %f\n",
        design.goal.x, design.goal.y, design.goal.w, design.goal.h);
}

int main() {
    //get the example design
    ft_design_spec spec = make_the_design();

    std::shared_ptr<ft_design> design = ft_create_design(nullptr, spec);

    print_design(*design);

    //create the handle and setings
    std::shared_ptr<ft_sim_state> handle;
    ft_sim_settings settings;

    //initialize the handle
    handle = ft_create_sim(handle, *design, settings);

    //step the simulation until it solves
    while(!ft_is_solved(handle, spec)) {
        ft_step_sim(handle, settings);
    }

    //behold: a solve
    std::cout << "Design solved at " << handle->tick << " ticks" << std::endl;
    return 0;
}