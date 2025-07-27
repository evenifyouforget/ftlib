#include <iostream>

#include "sim/fcsim.h"
#include "example_design.h"

void print_design(const ft_design_spec& spec) {
    ft_design design;
    create_design(&design, spec);

    printf("LEVEL BLOCKS:\n");
    for(const auto& block : design.level_blocks) {
        printf("\ttype: %d, x: %f, y: %f, w: %f, h: %f, angle: %f\n",
            block.type,
            block.x,
            block.y,
            block.w,
            block.h,
            block.angle);
    }
    
    printf("DESIGN BLOCKS:\n");
    for(size_t i = 0; i < design.design_blocks.size(); i++) {
        const auto& block = design.design_blocks[i];
        printf("\tid: %lu, type: %d, x: %f, y: %f, w: %f, h: %f, angle: %f\n",
            i,
            block.type,
            block.x,
            block.y,
            block.w,
            block.h,
            block.angle);
    }

    printf("JOINTS:\n");
    for(size_t i = 0; i < design.joints.size(); i++) {
        const ft_joint_stack& js = design.joints[i];
        printf("\tjoint stack: id: %lu, x: %f, y: %f\n", i, js.x, js.y);
        for(const auto& joint : js.joints) {
            printf("\t\tblock_idx: %d, joint_stack_idx: %d, joint_idx: %d\n", joint.block_idx, joint.joint_stack_idx, joint.joint_idx);
        }
    }

    printf("BUILD: x: %f, y: %f, w: %f, h: %f\n",
        spec.build.x, spec.build.y, spec.build.w, spec.build.h);
    
    printf("GOAL: x: %f, y: %f, w: %f, h: %f\n",
        spec.goal.x, spec.goal.y, spec.goal.w, spec.goal.h);
}

int main() {
    //get the example design
    ft_design_spec design = make_the_design();

    print_design(design);

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