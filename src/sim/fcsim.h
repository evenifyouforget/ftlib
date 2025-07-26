#ifndef FCSIM_H_
#define FCSIM_H_

#include <cstdint>
#include <memory>
#include <vector>
#include "box2d/Include/Box2D.h"

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

const uint16_t FCSIM_NO_ID = 65535;
const uint16_t FCSIM_NO_JOINT = 65535;

inline bool type_is_player(int t) {
	return t >= fcsim_piece_type::GP_RECT;
}

struct fcsim_block_def {
	fcsim_piece_type::type type;
	uint16_t id;
	double x, y;
	double w, h;
	double angle;
	// TODO: refactor to use int64_t ? or even better, its own type with safety
	uint16_t joints[2];
};

struct fcsim_rect {
	double x, y;
	double w, h;
};

struct ft_design_spec {
	std::vector<fcsim_block_def> blocks;
	fcsim_rect build;
	fcsim_rect goal;
};

#define ARENA_WIDTH	2000
#define ARENA_HEIGHT	1450
#define TIME_STEP	0.03333333333333333
#define ITERATIONS	10

struct block;

#define JOINT_PIN  0
#define JOINT_CW   1
#define JOINT_CCW -1

// single body's jointable point
struct joint {
	double x, y;
	int type;
	bool generated;
	block* block1;
	block* block2;
	joint* next;
};

// list of "joints" that are joined together to form 1 joint-ish ("joint stack")
struct joint_collection {
	double x, y;
	block* top_block;
	joint* joints_head;
	joint* joints_tail;
};

// linked list node for list of joint stacks which this body is a member of
struct joint_collection_list {
	joint_collection* jc;
	joint_collection_list* next;
};

struct block {
	fcsim_block_def bdef;
	b2Body* body; // not managed by us
	joint_collection_list* jcs_head;
	joint_collection_list* jcs_tail;
};

struct ft_sim_state {
	b2World* world;
	std::vector<block> blocks;
	int tick = 0;
	~ft_sim_state();
};

struct ft_sim_settings {

};

std::shared_ptr<ft_sim_state> fcsim_new(std::shared_ptr<ft_sim_state> handle, const ft_design_spec& arena, const ft_sim_settings&);

void fcsim_step(std::shared_ptr<ft_sim_state> handle, const ft_sim_settings&);

template <typename T> void add_unique(std::vector<T>& vec, const T& el) {
	for (size_t i = 0; i < vec.size(); ++i) {
		if (vec[i] == el) { return; }
	}
	vec.push_back(el);
}

template <typename T> void delete_all(std::vector<T*>& vec) {
	for (size_t i = 0; i < vec.size(); ++i) {
		delete vec[i];
	}
}

bool fcsim_in_area(const fcsim_block_def& bdef, const fcsim_rect& area);

bool fcsim_is_solved(const std::shared_ptr<ft_sim_state> sim, const ft_design_spec& spec);

#endif
