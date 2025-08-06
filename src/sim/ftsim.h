#ifndef FTSIM_H
#define FTSIM_H

#include "box2d/Include/Box2D.h"
#include <cstdint>
#include <memory>
#include <vector>

struct ft_rect {
    double x, y;
    double w, h;
};

struct ft_piece_type {
    enum type : uint8_t {
        STATIC_RECT,
        STATIC_CIRC,
        DYNAMIC_RECT,
        DYNAMIC_CIRC,
        GP_RECT,
        GP_CIRC,
        UPW,
        CW,
        CCW,
        WATER,
        WOOD,
        SIZE,
    };
};

bool ft_is_goal_object(ft_piece_type::type type);
bool ft_is_circle(ft_piece_type::type type); // any circle
bool ft_is_wheel(ft_piece_type::type type);  // only circles which can be moved by the player
bool ft_is_player_movable(ft_piece_type::type type);
bool ft_is_player_deletable(ft_piece_type::type type);

const uint16_t FT_NO_ID = std::numeric_limits<uint16_t>::max();
const uint16_t FT_NO_JOINT = std::numeric_limits<uint16_t>::max();
const uint16_t FT_NO_JOINT_STACK = std::numeric_limits<uint16_t>::max();

struct ft_block_spec {
    ft_piece_type::type type;
    uint16_t id;
    double x, y;
    double w, h;
    double angle;
    // TODO: refactor to use int64_t ? or even better, its own type with safety
    uint16_t joints[2];
};

// a "design spec": a pretty direct translation of design xml
struct ft_design_spec {
    std::vector<ft_block_spec> blocks;
    ft_rect build;
    ft_rect goal;
};

// a design which can be created from a spec, intended to be possible to edit and easier to simulate
struct ft_design;

const size_t FT_MAX_JOINTS = 5;

// a single level or design object in a design
struct ft_block {
    uint16_t block_idx;
    ft_piece_type::type type;
    double x, y;
    double w, h;
    double angle;
    uint16_t joint_stack_idxs[FT_MAX_JOINTS]; // indexes into design.joints which contain this
                                              // block's joint stacks
    uint16_t
        joint_idxs[FT_MAX_JOINTS]; // indexes into this js.joints which contains this block's joints

    b2Body* body; // not managed by us
};

ft_block to_block(ft_block_spec bdef);

struct ft_joint_type {
    enum type : int8_t {
        CCW = -1,
        UPW = 0,
        CW = 1,
    };
};

ft_joint_type::type joint_type(ft_piece_type::type block_type);

// a joint jointing this block with the previous block in the joint stack
struct ft_joint {
    uint16_t block_idx;       // index into design.design_blocks
    uint16_t joint_stack_idx; // index into design.joints which contains this joint's stack
    uint16_t joint_idx;       // index into this js.joints which contains this joint

    b2Joint* joint; // not managed by us
};

// a "joint stack", which joints any number of blocks together at the same point
struct ft_joint_stack {
    uint16_t joint_stack_idx; // index into design.joints which contains this joint's stack
    std::vector<ft_joint> joints;
    double x;
    double y;
};

struct ft_design {
    std::vector<ft_block> level_blocks;  // blocks which can't be moved by the player
    std::vector<ft_block> design_blocks; // blocks which can be moved by the player. index into
                                         // design_blocks = block idx = block id
    std::vector<ft_joint_stack> joint_stacks;
    ft_rect build;
    ft_rect goal;
};

// make the design from the spec
ft_design ft_create_design(const ft_design_spec& spec);

const double ARENA_WIDTH = 2000;
const double ARENA_HEIGHT = 1450;
const double TIME_STEP = 0.03333333333333333;
const int32_t ITERATIONS = 10;

// the state of the simulation. contains box2d stuff and the design.
struct ft_sim_state {
    b2World* world;
    ft_design design;
    int tick = 0;
    ~ft_sim_state();
};

struct ft_sim_settings {};

// make a ft_sim_state from a spec and settings
ft_sim_state ft_create_sim(const ft_design& design, const ft_sim_settings& settings);

// step the sim state forward 1 tick
void ft_step_sim(ft_sim_state& handle, const ft_sim_settings& settings);

// check if a block is within an area
bool ft_in_area(const ft_block& block, const ft_rect& area);

// check if a design has solved (if all the gps are within the goal)
bool ft_is_solved(const ft_sim_state& sim, const ft_design_spec& spec);

// design editing
void ft_splice_joint_stack(ft_design& design, uint16_t js_idx, uint16_t joint_idx);

#endif
