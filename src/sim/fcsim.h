#ifndef FCSIM_H_
#define FCSIM_H_

#include <cstdint>
#include <memory>
#include <vector>
#include "box2d/Include/Box2D.h"

struct fcsim_rect {
	double x, y;
	double w, h;
};

//intentionally in the same order as the render enum, so they can be converted back and forth, and the render bindings can be used for this
struct fcsim_piece_type {
	enum type : uint16_t {
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

bool is_goal_object(fcsim_piece_type::type type);
bool is_circle(fcsim_piece_type::type type); //any circle
bool is_wheel(fcsim_piece_type::type type); //only circles which can be moved by the player
bool is_player_movable(fcsim_piece_type::type type);
bool is_player_deletable(fcsim_piece_type::type type);

const uint16_t FCSIM_NO_ID = std::numeric_limits<uint16_t>::max();
const uint16_t FCSIM_NO_JOINT = std::numeric_limits<uint16_t>::max();
const uint16_t FCSIM_NO_JOINT_STACK = std::numeric_limits<uint16_t>::max();

struct fcsim_block_def {
	fcsim_piece_type::type type;
	uint16_t id;
	double x, y;
	double w, h;
	double angle;
	// TODO: refactor to use int64_t ? or even better, its own type with safety
	uint16_t joints[2];
};

//a "design spec": a pretty direct translation of design xml
struct ft_design_spec {
	std::vector<fcsim_block_def> blocks;
	fcsim_rect build;
	fcsim_rect goal;
};

// a design which can be created from a spec, intended to be possible to edit and easier to simulate
struct ft_design;

//a single level or design object in a design
struct ft_block {
	uint16_t block_idx;
	fcsim_piece_type::type type;
	double x, y;
	double w, h;
	double angle;
	uint16_t joint_stack_idxs[5]; //indexes into design.joints which contain this block's joint stacks
	uint16_t joint_idxs[5]; //indexes into this js.joints which contains this block's joints
	ft_design* design; //the design this block is part of

	b2Body* body; // not managed by us
};

ft_block to_block(fcsim_block_def bdef, ft_design* design);

struct fcsim_joint_type {
	enum type : int8_t {
		CCW = -1,
		UPW = 0,
		CW = 1,
	};
};

fcsim_joint_type::type joint_type(fcsim_piece_type::type block_type);

//a joint jointing this block with the previous block in the joint stack
struct ft_joint {
	uint16_t block_idx; //index into design.design_blocks
	uint16_t joint_stack_idx; //index into design.joints which contains this joint's stack
	uint16_t joint_idx; //index into this js.joints which contains this joint
	ft_design* design; //the design this joint is part of

	b2Joint* joint; // not managed by us
};

//a "joint stack", which joints any number of blocks together at the same point
struct ft_joint_stack {
	uint16_t joint_stack_idx; //index into design.joints which contains this joint's stack
	std::vector<ft_joint> joints;
	double x;
	double y;

	ft_design* design; //the design this joint stack is part of
};

struct ft_design {
	std::vector<ft_block> level_blocks; //blocks which can't be moved by the player
	std::vector<ft_block> design_blocks; //blocks which can be moved by the player. index into design_blocks = block idx = block id
	std::vector<ft_joint_stack> joints;
	fcsim_rect build;
	fcsim_rect goal;
};

//make the design from the spec
void create_design(ft_design* design, const ft_design_spec& spec);

const double ARENA_WIDTH = 2000;
const double ARENA_HEIGHT = 1450;
const double TIME_STEP = 0.03333333333333333;
const int32_t ITERATIONS = 10;

//the state of the simulation. contains box2d stuff and the design.
struct ft_sim_state {
	b2World* world;
	ft_design design;
	int tick = 0;
	~ft_sim_state();
};

struct ft_sim_settings {

};

//make a ft_sim_state from a spec and settings
std::shared_ptr<ft_sim_state> fcsim_new(std::shared_ptr<ft_sim_state> handle, const ft_design_spec& spec, const ft_sim_settings& settings);

//step the sim state forward 1 tick
void fcsim_step(std::shared_ptr<ft_sim_state> handle, const ft_sim_settings& settings);

//check if a block is within an area
bool fcsim_in_area(const ft_block& block, const fcsim_rect& area);

//check if a design has solved (if all the gps are within the goal)
bool fcsim_is_solved(const std::shared_ptr<ft_sim_state> sim, const ft_design_spec& spec);

#endif
