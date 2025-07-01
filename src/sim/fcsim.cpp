#include <stdio.h>

#include "fcsim.h"
#include "ftmath.h"

ft_sim_state::~ft_sim_state() {
	std::vector<joint_collection_list*> uj2;
	std::vector<joint_collection*> uj1;
	std::vector<joint*> uj0;
	// clean up joints
	for (int i = 0; i < block_cnt; i++) {
		block* b = &(blocks[i]);
		for (joint_collection_list* l = b->jcs_head; l; l = l->next) {
			add_unique(uj2, l);
			add_unique(uj1, l->jc);
			for (joint* j = l->jc->joints_head; j; j = j->next) {
				add_unique(uj0, j);
			}
		}
	}
	delete_all(uj2);
	delete_all(uj1);
	delete_all(uj0);
	// clean up world data
	world->CleanBodyList();
	delete world;
	delete blocks;
}

class collision_filter : public b2CollisionFilter {
	bool ShouldCollide(b2Shape* s1, b2Shape* s2)
	{
		if (!b2_defaultFilter.ShouldCollide(s1, s2))
			return false;

		block* b1 = (block*)s1->GetUserData();
		block* b2 = (block*)s2->GetUserData();

		joint_collection_list* j1, * j2;
		for (j1 = b1->jcs_head; j1; j1 = j1->next) {
			for (j2 = b2->jcs_head; j2; j2 = j2->next) {
				if (j1->jc == j2->jc)
					return false;
			}
		}

		return true;
	}
};

static collision_filter fcsim_collision_filter;



struct block_physics {
	int circle;
	double density;
	double friction;
	double restitution;
	int categoryBits;
	int maskBits;
	double linearDamping;
	double angularDamping;
};

static struct block_physics block_physics_tbl[] = {
	/* c dens fric rest   cB   mB   linD angD */
	{  0, 0.0, 0.7, 0.0,  -1,  -1,   0.0, 0.0 }, /* STAT_RECT */
	{  1, 0.0, 0.7, 0.0,  -1,  -1,   0.0, 0.0 }, /* STAT_CIRCLE */
	{  0, 1.0, 0.7, 0.2,  -1,  -1,   0.0, 0.0 }, /* DYN_RECT */
	{  1, 1.0, 0.7, 0.2,  -1,  -1,   0.0, 0.0 }, /* DYN_CIRCLE */
	{  0, 1.0, 0.7, 0.2,   1, -17,   0.0, 0.0 }, /* GOAL_RECT */
	{  1, 1.0, 0.7, 0.2,   1, -17,   0.0, 0.0 }, /* GOAL_CIRCLE */
	{  1, 1.0, 0.7, 0.2,   1, -17,   0.0, 0.0 }, /* WHEEL */
	{  1, 1.0, 0.7, 0.2,   1, -17,   0.0, 0.0 }, /* CW_WHEEL */
	{  1, 1.0, 0.7, 0.2,   1, -17,   0.0, 0.0 }, /* CCW_WHEEL */
	{  0, 1.0, 0.7, 0.2,  16, -18, 0.009, 0.2 }, /* ROD */
	{  0, 1.0, 0.7, 0.2, 256, -17, 0.009, 0.2 }, /* SOLID_ROD */
};

static void generate_body(b2World* world, block* b)
{
	fcsim_block_def bdef = b->bdef;
	block_physics phys = block_physics_tbl[bdef.type];
	b2BoxDef box_def;
	b2CircleDef circle_def;
	b2ShapeDef* shape_def;
	b2BodyDef body_def;

	if (phys.circle) {
		circle_def.radius = ft_mul(bdef.w, 0.5);
		shape_def = &circle_def;
	} else {
		box_def.extents.Set(ft_mul(bdef.w, 0.5), ft_mul(bdef.h, 0.5));
		shape_def = &box_def;
	}
	shape_def->density = phys.density;
	shape_def->friction = phys.friction;
	shape_def->restitution = phys.restitution;
	shape_def->categoryBits = phys.categoryBits;
	shape_def->maskBits = phys.maskBits;
	shape_def->userData = b;
	body_def.position.Set(bdef.x, bdef.y);
	body_def.rotation = bdef.angle;
	body_def.linearDamping = phys.linearDamping;
	body_def.angularDamping = phys.angularDamping;
	body_def.AddShape(shape_def);
	b->body = world->CreateBody(&body_def);
}

static void generate_joint(b2World* world, joint* j)
{
	if (j->generated)
		return;
	j->generated = true;

	b2RevoluteJointDef joint_def;
	joint_def.body1 = j->block1->body;
	joint_def.body2 = j->block2->body;
	joint_def.anchorPoint.Set(j->x, j->y);
	joint_def.collideConnected = true;
	if (j->type != JOINT_PIN) {
		joint_def.motorTorque = 50000000;
		joint_def.motorSpeed = -5 * j->type;
		joint_def.enableMotor = true;
	}
	world->CreateJoint(&joint_def);
}


static bool is_goal_object(uint16_t type)
{
	switch (type) {
	case FCSIM_GP_RECT:
	case FCSIM_GP_CIRC:
		return true;
	}
	return false;
}

static bool is_wheel(block* b)
{
	switch (b->bdef.type) {
	case FCSIM_GP_CIRC:
	case FCSIM_UPW:
	case FCSIM_CW:
	case FCSIM_CCW:
		return true;
	}
	return false;
}

static bool is_player(fcsim_block_def& bdef)
{
	switch (bdef.type) {
	case FCSIM_STATIC_RECT:
	case FCSIM_STATIC_CIRC:
	case FCSIM_DYNAMIC_RECT:
	case FCSIM_DYNAMIC_CIRC:
		return false;
	}
	return true;
}



static block* find_block_by_id(std::shared_ptr<ft_sim_state> handle, int id)
{
	for (int i = 0; i < handle->block_cnt; i++) {
		if (handle->blocks[i].bdef.id == id)
			return &handle->blocks[i];
	}
	return NULL;
}

static double distance(double x1, double y1, double x2, double y2)
{
	double dx = ft_sub(x2, x1);
	double dy = ft_sub(y2, y1);

	return ft_sqrt(ft_add(ft_mul(dx, dx), ft_mul(dy, dy)));
}

static joint_collection* get_closest_jc(std::shared_ptr<ft_sim_state> handle, double x, double y, fcsim_block_def bdef)
{
	//double best_dist = 10000000.0;
	double best_dist = 10.0;
	joint_collection* res = NULL;

	for (int i = 0; i < 2; i++) {
		if (bdef.joints[i] == FCSIM_NO_JOINT)break;
		block* b = find_block_by_id(handle, bdef.joints[i]);
		if (!b)
			continue;
		for (joint_collection_list* j = b->jcs_head; j; j = j->next) {
			double dist = distance(x, y, j->jc->x, j->jc->y);
			if (dist < best_dist) {
				best_dist = dist;
				res = j->jc;
			}
		}
	}

	return res;
}

void get_rod_endpoints(fcsim_block_def bdef, double* x0, double* y0, double* x1, double* y1)
{
	double cw = ft_mul(ft_cos(bdef.angle), ft_div(bdef.w, 2));
	double sw = ft_mul(ft_sin(bdef.angle), ft_div(bdef.w, 2));

	*x0 = ft_sub(bdef.x, cw);
	*y0 = ft_sub(bdef.y, sw);
	*x1 = ft_add(bdef.x, cw);
	*y1 = ft_add(bdef.y, sw);
}

int share_block(std::shared_ptr<ft_sim_state> handle, joint_collection* jc0, joint_collection* jc1)
{
	for (int i = 0; i < handle->block_cnt; i++) {
		bool f0 = false, f1 = false;
		for (joint_collection_list* j = handle->blocks[i].jcs_head; j; j = j->next) {
			if (j->jc == jc0) f0 = true;
			if (j->jc == jc1) f1 = true;
		}
		if (f0 && f1) return true;
	}
	return false;
}

static int joint_type(int block_type)
{
	switch (block_type) {
	case FCSIM_CW:  return JOINT_CW;
	case FCSIM_CCW: return JOINT_CCW;
	}
	return JOINT_PIN;
}

static joint_collection_list* create_joint(block* b, double x, double y)
{
	joint_collection* jc = new joint_collection;
	jc->x = x;
	jc->y = y;
	jc->top_block = b;
	jc->joints_head = NULL;
	jc->joints_tail = NULL;

	joint_collection_list* jcl = new joint_collection_list;
	jcl->jc = jc;
	jcl->next = NULL;

	if (b->jcs_tail) {
		b->jcs_tail->next = jcl;
		b->jcs_tail = jcl;
	} else {
		b->jcs_head = jcl;
		b->jcs_tail = jcl;
	}

	return jcl;
}

static int joint_type(block* b)
{
	switch (b->bdef.type) {
	case FCSIM_CW:  return JOINT_CW;
	case FCSIM_CCW: return JOINT_CCW;
	}
	return JOINT_PIN;
}

static bool is_singular_wheel_center(joint_collection* jc)
{
	if (jc->joints_head)
		return false;

	if (!is_wheel(jc->top_block))
		return false;

	return jc->x == jc->top_block->bdef.x &&
		jc->y == jc->top_block->bdef.y;
}

static int get_joint_type(block* b, joint_collection* jc)
{
	block* top = jc->top_block;
	int type;

	if (is_singular_wheel_center(jc))
		type = joint_type(jc->top_block);
	else
		type = joint_type(b);

	if (is_wheel(b))
		type = -type;

	return type;
}

static joint_collection_list* jcl_swap(joint_collection_list* jcl)
{
	joint_collection_list* new_jcl = jcl->next;

	if (!new_jcl)
		return jcl;

	jcl->next = new_jcl->next;
	new_jcl->next = jcl;

	return new_jcl;
}

static void replace_joint(block* b, joint_collection_list* jcl, joint_collection* jc)
{
	delete jcl->jc;
	jcl->jc = jc;

	if (b->jcs_head == jcl) {
		b->jcs_head = jcl_swap(b->jcs_head);
	} else {
		for (joint_collection_list* l = b->jcs_head; l; l = l->next) {
			if (l->next == jcl) {
				l->next = jcl_swap(l->next);
				break;
			}
		}
	}

	joint* j = new joint;
	j->x = jc->x;
	j->y = jc->y;
	j->type = get_joint_type(b, jc);
	j->generated = false;
	j->block1 = jc->top_block;
	j->block2 = b;
	j->next = NULL;

	jc->top_block = b;
	if (jc->joints_tail) {
		jc->joints_tail->next = j;
		jc->joints_tail = j;
	} else {
		jc->joints_head = j;
		jc->joints_tail = j;
	}
}

static void create_rod_joints(block* b, std::shared_ptr<ft_sim_state> handle)
{
	fcsim_block_def bdef = b->bdef;
	double x0, y0, x1, y1;

	get_rod_endpoints(bdef, &x0, &y0, &x1, &y1);
	joint_collection* jc0 = get_closest_jc(handle, x0, y0, bdef);
	joint_collection* jc1 = get_closest_jc(handle, x1, y1, bdef);

	if (jc0 && jc1 && share_block(handle, jc0, jc1))
		jc1 = NULL;

	if (jc0) {
		x0 = jc0->x;
		y0 = jc0->y;
	}

	if (jc1) {
		x1 = jc1->x;
		y1 = jc1->y;
	}

	bdef.angle = ft_atan2(ft_sub(y1, y0), ft_sub(x1, x0));
	bdef.w = distance(x0, y0, x1, y1);
	bdef.x = ft_add(x0, ft_div(ft_sub(x1, x0), 2.0));
	bdef.y = ft_add(y0, ft_div(ft_sub(y1, y0), 2.0));

	joint_collection_list* jcl0 = create_joint(b, x0, y0);
	joint_collection_list* jcl1 = create_joint(b, x1, y1);

	if (jc0)
		replace_joint(b, jcl0, jc0);

	if (jc1)
		replace_joint(b, jcl1, jc1);
}



static void create_wheel_joints(block* b, std::shared_ptr<ft_sim_state> handle)
{
	fcsim_block_def bdef = b->bdef;
	double x = bdef.x;
	double y = bdef.y;
	double r = ft_div(bdef.w, 2);

	joint_collection* jc = get_closest_jc(handle, x, y, bdef);
	if (jc) {
		x = bdef.x = jc->x;
		y = bdef.y = jc->y;
	}

	double a[4] = {
		0.0,
		3.141592653589793 / 2,
		3.141592653589793,
		4.71238898038469,
	};

	joint_collection_list* jcl = create_joint(b, bdef.x, bdef.y);
	for (int i = 0; i < 4; i++) {
		create_joint(b, ft_add(x, ft_mul(ft_cos(ft_add(bdef.angle, a[i])), r)),
			ft_add(y, ft_mul(ft_sin(ft_add(bdef.angle, a[i])), r)));
	}

	if (jc)
		replace_joint(b, jcl, jc);
}

static void create_goal_rect_joints(block* b)
{
	fcsim_block_def bdef = b->bdef;
	double x = bdef.x;
	double y = bdef.y;
	double w_half = ft_div(bdef.w, 2);
	double h_half = ft_div(bdef.h, 2);

	double x0 = ft_mul(ft_cos(bdef.angle), w_half);
	double y0 = ft_mul(ft_sin(bdef.angle), w_half);
	double x1 = ft_mul(ft_sin(bdef.angle), h_half);
	double y1 = ft_mul(-ft_cos(bdef.angle), h_half);

	create_joint(b, x, y);
	create_joint(b, ft_add(ft_add(x, x0), x1), ft_add(ft_add(y, y0), y1));
	create_joint(b, ft_add(ft_sub(x, x0), x1), ft_add(ft_sub(y, y0), y1));
	create_joint(b, ft_sub(ft_add(x, x0), x1), ft_sub(ft_add(y, y0), y1));
	create_joint(b, ft_sub(ft_sub(x, x0), x1), ft_sub(ft_sub(y, y0), y1));
}

static void create_joints(block* b, std::shared_ptr<ft_sim_state> handle)
{
	switch (b->bdef.type) {
	case FCSIM_GP_RECT:
		create_goal_rect_joints(b);
		return;
	case FCSIM_GP_CIRC:
	case FCSIM_UPW:
	case FCSIM_CW:
	case FCSIM_CCW:
		create_wheel_joints(b, handle);
		return;
	case FCSIM_WATER:
	case FCSIM_WOOD:
		create_rod_joints(b, handle);
		return;
	}
}

void add_block(std::shared_ptr<ft_sim_state> handle, fcsim_block_def bdef)
{
	block* block = &handle->blocks[handle->block_cnt++];

	memset(block, 0, sizeof(*block));

	/* TODO: deal with this somewhere else */
	/*
	if (bdef.type == FCSIM_STATIC_CIRC || bdef.type == FCSIM_DYNAMIC_CIRC) {
		bdef.w = ft_mul(bdef.w, 2);
		bdef.h = ft_mul(bdef.h, 2);
	}
	if (bdef.type == FCSIM_DYNAMIC_CIRC) {
		bdef.angle = 0;
	}
	*/
	block->bdef = bdef;

	create_joints(block, handle);
}

std::shared_ptr<ft_sim_state> fcsim_new(std::shared_ptr<ft_sim_state> handle, ft_design_spec& arena, const ft_sim_settings&)
{
	if (!handle) {
		handle = std::make_shared<ft_sim_state>();
	}

	b2Vec2 gravity(0, 300);
	b2AABB aabb;
	aabb.minVertex.Set(-ARENA_WIDTH, -ARENA_HEIGHT);
	aabb.maxVertex.Set(ARENA_WIDTH, ARENA_HEIGHT);
	handle->world = new b2World(aabb, gravity, true);
	handle->world->SetFilter(&fcsim_collision_filter);

	handle->blocks = new block[arena.blocks.size()];
	handle->block_cnt = 0;

	for (int i = 0; i < arena.blocks.size(); i++) {
		if (is_player(arena.blocks[i]))
			add_block(handle, arena.blocks[i]);
	}

	for (int i = 0; i < arena.blocks.size(); i++) {
		if (!is_player(arena.blocks[i]))
			add_block(handle, arena.blocks[i]);
	}

	for (int i = 0; i < handle->block_cnt; i++)
		generate_body(handle->world, &handle->blocks[i]);

	for (int i = 0; i < handle->block_cnt; i++) {
		block* b = &handle->blocks[i];
		for (joint_collection_list* l = b->jcs_head; l; l = l->next) {
			for (joint* j = l->jc->joints_head; j; j = j->next)
				generate_joint(handle->world, j);
		}
	}

	return handle;
}

void fcsim_step(std::shared_ptr<ft_sim_state> handle, const ft_sim_settings&)
{
	handle->world->Step(TIME_STEP, ITERATIONS);

	// joint breaking
	b2Joint* joint = handle->world->GetJointList();
	while (joint) {
		b2Joint* next = joint->GetNext();
		b2Vec2 a1 = joint->GetAnchor1();
		b2Vec2 a2 = joint->GetAnchor2();
		b2Vec2 d = a1 - a2;
		if (fabs(d.x) + fabs(d.y) > 50.0)
			handle->world->DestroyJoint(joint);
		joint = next;
	}

	for (int i = 0; i < handle->block_cnt; i++) {
		block* b = &handle->blocks[i];
		b2Vec2 pos = b->body->GetOriginPosition();
		double angle = b->body->GetRotation()._v;

		b->bdef.x = pos.x._v;
		b->bdef.y = pos.y._v;
		b->bdef.angle = angle;
	}
	handle->tick++;
}

#define CHECK_CORNER(valx, valy) {double xx = valx; double yy = valy; if(xx < area_xa || xx > area_xb || yy < area_ya || yy > area_yb)return false;}

bool fcsim_in_area(const fcsim_block_def& bdef, const fcsim_rect& area) {
	bool is_circle = block_physics_tbl[bdef.type].circle;
	double bex = ft_mul(bdef.w, 0.5);
	double bey = ft_mul(bdef.h, 0.5);
	double area_ex = ft_mul(area.w, 0.5);
	double area_ey = ft_mul(area.h, 0.5);
	double area_xa = ft_sub(area.x, area_ex);
	double area_xb = ft_add(area.x, area_ex);
	double area_ya = ft_sub(area.y, area_ey);
	double area_yb = ft_add(area.y, area_ey);
	if (is_circle) {
		return ft_sub(bdef.x, bex) >= area_xa && ft_add(bdef.x, bex) <= area_xb && ft_sub(bdef.y, bey) >= area_ya & ft_add(bdef.y, bey) <= area_yb;
	}
	double x = bdef.x;
	double y = bdef.y;
	double x0 = ft_mul(ft_cos(bdef.angle), bex);
	double y0 = ft_mul(ft_sin(bdef.angle), bex);
	double x1 = ft_mul(ft_sin(bdef.angle), bey);
	double y1 = ft_mul(-ft_cos(bdef.angle), bey);
	CHECK_CORNER(ft_add(ft_add(x, x0), x1), ft_add(ft_add(y, y0), y1));
	CHECK_CORNER(ft_add(ft_sub(x, x0), x1), ft_add(ft_sub(y, y0), y1));
	CHECK_CORNER(ft_sub(ft_add(x, x0), x1), ft_sub(ft_add(y, y0), y1));
	CHECK_CORNER(ft_sub(ft_sub(x, x0), x1), ft_sub(ft_sub(y, y0), y1));
	return true;
}

bool fcsim_is_solved(std::shared_ptr<ft_sim_state> sim, const ft_design_spec& spec) {
	bool goal_exist = false;
	for (int i = 0; i < sim->block_cnt; ++i) {
		fcsim_block_def& bdef = sim->blocks[i].bdef;
		if (!is_goal_object(bdef.type))continue;
		goal_exist = true;
		if (!fcsim_in_area(bdef, spec.goal))return false;
	}
	return goal_exist;
}
