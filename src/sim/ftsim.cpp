#include "ftsim.h"
#include "ftmath.h"
#include <stdio.h>
#include <unordered_set>

bool ft_is_goal_object(ft_piece_type::type type) {
    switch (type) {
    case ft_piece_type::GP_RECT:
    case ft_piece_type::GP_CIRC:
        return true;
    default:
        return false;
    }
}

bool ft_is_circle(ft_piece_type::type type) {
    switch (type) {
    case ft_piece_type::STATIC_CIRC:
    case ft_piece_type::DYNAMIC_CIRC:
    case ft_piece_type::GP_CIRC:
    case ft_piece_type::UPW:
    case ft_piece_type::CW:
    case ft_piece_type::CCW:
        return true;
    default:
        return false;
    }
}

bool ft_is_wheel(ft_piece_type::type type) {
    switch (type) {
    case ft_piece_type::GP_CIRC:
    case ft_piece_type::UPW:
    case ft_piece_type::CW:
    case ft_piece_type::CCW:
        return true;
    default:
        return false;
    }
}

bool ft_is_player_movable(ft_piece_type::type type) {
    switch (type) {
    case ft_piece_type::GP_RECT:
    case ft_piece_type::GP_CIRC:
    case ft_piece_type::UPW:
    case ft_piece_type::CW:
    case ft_piece_type::CCW:
    case ft_piece_type::WATER:
    case ft_piece_type::WOOD:
        return true;
    default:
        return false;
    }
}

bool ft_is_player_deletable(ft_piece_type::type type) {
    switch (type) {
    case ft_piece_type::UPW:
    case ft_piece_type::CW:
    case ft_piece_type::CCW:
    case ft_piece_type::WATER:
    case ft_piece_type::WOOD:
        return true;
    default:
        return false;
    }
}

ft_block to_block(ft_block_def bdef, ft_design* design) {
    return ft_block{
        .block_idx = bdef.id,
        .type = bdef.type,
        .x = bdef.x,
        .y = bdef.y,
        .w = bdef.w,
        .h = bdef.h,
        .angle = bdef.angle,
        // joints initialized later
        .joint_stack_idxs = {FT_NO_JOINT_STACK, FT_NO_JOINT_STACK, FT_NO_JOINT_STACK,
                             FT_NO_JOINT_STACK, FT_NO_JOINT_STACK},
        .joint_idxs = {FT_NO_JOINT, FT_NO_JOINT, FT_NO_JOINT, FT_NO_JOINT, FT_NO_JOINT},
        .design = design,
    };
}

ft_joint_type::type joint_type(ft_piece_type::type block_type) {
    switch (block_type) {
    case ft_piece_type::CW:
        return ft_joint_type::CW;
    case ft_piece_type::CCW:
        return ft_joint_type::CCW;
    default:
        return ft_joint_type::UPW;
    }
}

static double distance(double x1, double y1, double x2, double y2) {
    double dx = ft_sub(x2, x1);
    double dy = ft_sub(y2, y1);

    return ft_sqrt(ft_add(ft_mul(dx, dx), ft_mul(dy, dy)));
}

static void get_rod_endpoints(ft_block_def bdef, double* x0, double* y0, double* x1, double* y1) {
    double cw = ft_mul(ft_cos(bdef.angle), ft_div(bdef.w, 2));
    double sw = ft_mul(ft_sin(bdef.angle), ft_div(bdef.w, 2));

    *x0 = ft_sub(bdef.x, cw);
    *y0 = ft_sub(bdef.y, sw);
    *x1 = ft_add(bdef.x, cw);
    *y1 = ft_add(bdef.y, sw);
}

// gets the index of the closest joint stack to (x, y) which contains a block which bdef is jointed
// to
// WORKS EVEN BEFORE create_joints IS CALLED!!!
static uint16_t get_closest_joint_stack_idx(const ft_design& design, double x, double y,
                                            ft_block_def bdef) {
    // double best_dist = 10000000.0;
    double best_dist = 10.0;
    uint16_t res = FT_NO_JOINT_STACK;

    // TODO: make efficient
    for (size_t i = 0; i < 2; i++) {
        if (bdef.joints[i] == FT_NO_JOINT)
            break;
        // TODO: check if block id is valid?
        for (uint16_t j = 0; j < design.joint_stacks.size(); j++) {
            const ft_joint_stack& js = design.joint_stacks[j];
            for (uint16_t k = 0; k < js.joints.size(); k++) {
                const ft_joint& joint = js.joints[k];
                if (joint.block_idx == bdef.joints[i]) {
                    goto found_block;
                }
            }

            continue;
        found_block:

            double dist = distance(x, y, js.x, js.y);
            if (dist < best_dist) {
                best_dist = dist;
                res = j;
            }
        }
    }

    return res;
}

// much faster, but ONLY WORKS AFTER BLOCK JOINTS HAVE BEEN POPULATED
static uint16_t get_closest_joint_stack_idx_efficient(const ft_design& design, double x, double y,
                                                      ft_block_def bdef) {
    const ft_block& block = design.level_blocks[bdef.id];

    // double best_dist = 10000000.0;
    double best_dist = 10.0;
    uint16_t res = FT_NO_JOINT_STACK;

    // TODO: make efficient
    for (size_t j = 0; j < FT_MAX_JOINTS; j++) {
        uint16_t js_idx = block.joint_stack_idxs[j];
        if (js_idx == FT_NO_JOINT_STACK)
            break;

        const ft_joint_stack& js = design.joint_stacks[js_idx];
        double dist = distance(x, y, js.x, js.y);
        if (dist < best_dist) {
            best_dist = dist;
            res = j;
        }
    }

    return res;
}

// if the two joint stacks contain the same block
static bool share_block(const ft_joint_stack& js1, const ft_joint_stack& js2) {
    if (&js1 == &js2)
        return true;

    std::unordered_set<uint16_t> js1_block_idxs;
    for (const auto& joint : js1.joints) {
        js1_block_idxs.insert(joint.block_idx);
    }
    for (const auto& joint : js2.joints) {
        if (js1_block_idxs.find(joint.block_idx) != js1_block_idxs.end()) {
            return true;
        }
    }

    return false;
}

// if js_idx == design.joints.size(), a new joint stack is added
// js_x and js_y are optional, only relevant if js_idx == design.joints.size()
static void create_joint(ft_design& design, ft_block_def bdef, size_t js_idx, double js_x = 0.,
                         double js_y = 0.) {
    uint16_t joint_stack_idx = static_cast<uint16_t>(js_idx);
    if (js_idx == design.joint_stacks.size()) {
        design.joint_stacks.emplace_back(ft_joint_stack{
            .joint_stack_idx = joint_stack_idx,
            .x = js_x,
            .y = js_y,
        });
    }
    uint16_t joint_idx = design.joint_stacks[js_idx].joints.size();

    design.joint_stacks[js_idx].joints.emplace_back(ft_joint{
        .block_idx = bdef.id,
        .joint_stack_idx = joint_stack_idx,
        .joint_idx = joint_idx, // not size - 1 because its not added yet
    });

    ft_block& block = design.design_blocks[bdef.id];
    for (size_t i = 0; i < FT_MAX_JOINTS; i++) {
        if (block.joint_stack_idxs[i] != FT_NO_JOINT_STACK)
            continue;
        block.joint_stack_idxs[i] = joint_stack_idx;
        block.joint_idxs[i] = joint_idx;
        break;
    }
}

static void create_rod_joints(ft_design& design, ft_block_def bdef) {
    double x0, y0, x1, y1;
    get_rod_endpoints(bdef, &x0, &y0, &x1, &y1);

    size_t js0_idx = get_closest_joint_stack_idx(design, x0, y0, bdef);
    size_t js1_idx = get_closest_joint_stack_idx(design, x1, y1, bdef);

    // make sure you can't joint both ends of a rod to the same point
    if (js0_idx != FT_NO_JOINT_STACK && js1_idx != FT_NO_JOINT_STACK &&
        share_block(design.joint_stacks[js0_idx], design.joint_stacks[js1_idx])) {
        js1_idx = FT_NO_JOINT_STACK;
    }

    if (js0_idx != FT_NO_JOINT_STACK) {
        x0 = design.joint_stacks[js0_idx].x;
        y0 = design.joint_stacks[js0_idx].y;
    }

    if (js1_idx != FT_NO_JOINT_STACK) {
        x1 = design.joint_stacks[js1_idx].x;
        y1 = design.joint_stacks[js1_idx].y;
    }

    if (js0_idx != FT_NO_JOINT_STACK) {
        create_joint(design, bdef, js0_idx);
    } else {
        create_joint(design, bdef, design.joint_stacks.size(), x0, y0);
    }

    if (js1_idx != FT_NO_JOINT_STACK) {
        create_joint(design, bdef, js1_idx);
    } else {
        create_joint(design, bdef, design.joint_stacks.size(), x1, y1);
    }
}

static void create_wheel_joints(ft_design& design, ft_block_def bdef) {
    double x = bdef.x;
    double y = bdef.y;
    double r = ft_div(bdef.w, 2);

    size_t js_idx = get_closest_joint_stack_idx(design, x, y, bdef);
    if (js_idx != FT_NO_JOINT_STACK) {
        x = design.joint_stacks[js_idx].x;
        y = design.joint_stacks[js_idx].y;
    }

    const double a[4] = {
        0.0,
        3.141592653589793 / 2,
        3.141592653589793,
        4.71238898038469,
    };

    for (size_t i = 0; i < 4; i++) {
        double jx = ft_add(x, ft_mul(ft_cos(ft_add(bdef.angle, a[i])), r));
        double jy = ft_add(y, ft_mul(ft_sin(ft_add(bdef.angle, a[i])), r));
        create_joint(design, bdef, design.joint_stacks.size(), jx, jy);
    }

    if (js_idx != FT_NO_JOINT_STACK) {
        create_joint(design, bdef, js_idx);
    } else {
        create_joint(design, bdef, design.joint_stacks.size(), x, y);
    }
}

static void create_goal_rect_joints(ft_design& design, ft_block_def bdef) {
    double x = bdef.x;
    double y = bdef.y;
    double w_half = ft_div(bdef.w, 2);
    double h_half = ft_div(bdef.h, 2);

    double x0 = ft_mul(ft_cos(bdef.angle), w_half);
    double y0 = ft_mul(ft_sin(bdef.angle), w_half);
    double x1 = ft_mul(ft_sin(bdef.angle), h_half);
    double y1 = ft_mul(-ft_cos(bdef.angle), h_half);

    create_joint(design, bdef, design.joint_stacks.size(), x, y);

    double xjs[4] = {ft_add(ft_add(x, x0), x1), ft_add(ft_sub(x, x0), x1),
                     ft_sub(ft_add(x, x0), x1), ft_sub(ft_sub(x, x0), x1)};
    double yjs[4] = {ft_add(ft_add(y, y0), y1), ft_add(ft_sub(y, y0), y1),
                     ft_sub(ft_add(y, y0), y1), ft_sub(ft_sub(y, y0), y1)};
    for (size_t i = 0; i < 4; i++) {
        create_joint(design, bdef, design.joint_stacks.size(), xjs[i], yjs[i]);
    }
}

static void create_joints(ft_design& design, ft_block_def bdef) {
    switch (bdef.type) {
    case ft_piece_type::GP_RECT:
        create_goal_rect_joints(design, bdef);
        return;
    case ft_piece_type::GP_CIRC:
    case ft_piece_type::UPW:
    case ft_piece_type::CW:
    case ft_piece_type::CCW:
        create_wheel_joints(design, bdef);
        return;
    case ft_piece_type::WATER:
    case ft_piece_type::WOOD:
        create_rod_joints(design, bdef);
        return;
    default:
        return;
    }
}

void ft_create_design(ft_design* design, const ft_design_spec& spec) {
    for (size_t i = 0; i < spec.blocks.size(); i++) {
        ft_block ftb = to_block(spec.blocks[i], design);

        if (ft_is_player_movable(spec.blocks[i].type)) {
            design->design_blocks.push_back(ftb);
        } else {
            design->level_blocks.push_back(ftb);
        }
    }

    for (size_t i = 0; i < spec.blocks.size(); i++) {
        create_joints(*design, spec.blocks[i]);
    }

    design->build = spec.build;
    design->goal = spec.goal;
}

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

static block_physics block_physics_tbl[] = {
    /* c dens fric rest   cB   mB   linD angD */
    {0, 0.0, 0.7, 0.0, -1, -1, 0.0, 0.0},     /* STAT_RECT */
    {1, 0.0, 0.7, 0.0, -1, -1, 0.0, 0.0},     /* STAT_CIRCLE */
    {0, 1.0, 0.7, 0.2, -1, -1, 0.0, 0.0},     /* DYN_RECT */
    {1, 1.0, 0.7, 0.2, -1, -1, 0.0, 0.0},     /* DYN_CIRCLE */
    {0, 1.0, 0.7, 0.2, 1, -17, 0.0, 0.0},     /* GOAL_RECT */
    {1, 1.0, 0.7, 0.2, 1, -17, 0.0, 0.0},     /* GOAL_CIRCLE */
    {1, 1.0, 0.7, 0.2, 1, -17, 0.0, 0.0},     /* WHEEL */
    {1, 1.0, 0.7, 0.2, 1, -17, 0.0, 0.0},     /* CW_WHEEL */
    {1, 1.0, 0.7, 0.2, 1, -17, 0.0, 0.0},     /* CCW_WHEEL */
    {0, 1.0, 0.7, 0.2, 16, -18, 0.009, 0.2},  /* ROD */
    {0, 1.0, 0.7, 0.2, 256, -17, 0.009, 0.2}, /* SOLID_ROD */
};

void generate_body(b2World* world, ft_block& block) {
    if (block.body != nullptr) {
        return;
    }

    block_physics phys = block_physics_tbl[block.type];

    b2BoxDef box_def;
    b2CircleDef circle_def;
    b2ShapeDef* shape_def;
    b2BodyDef body_def;

    if (phys.circle) {
        circle_def.radius = ft_mul(block.w, 0.5);
        shape_def = &circle_def;
    } else {
        box_def.extents.Set(ft_mul(block.w, 0.5), ft_mul(block.h, 0.5));
        shape_def = &box_def;
    }

    shape_def->density = phys.density;
    shape_def->friction = phys.friction;
    shape_def->restitution = phys.restitution;
    shape_def->categoryBits = phys.categoryBits;
    shape_def->maskBits = phys.maskBits;
    shape_def->userData = &block;

    body_def.position.Set(block.x, block.y);
    body_def.rotation = block.angle;
    body_def.linearDamping = phys.linearDamping;
    body_def.angularDamping = phys.angularDamping;
    body_def.AddShape(shape_def);
    block.body = world->CreateBody(&body_def);
}

// only generate joints from the 2nd joint onwards in a joint stack!!!
void generate_joint(
    b2World* world, ft_design& design, ft_joint_stack& js,
    ft_joint& joint) { // TODO: make sure this is the correct joint ordering behavior
    if (joint.joint != nullptr) {
        return;
    }

    if (joint.joint_idx == 0) {
        return;
    }

    const ft_block& block1 =
        design.design_blocks[design.joint_stacks[joint.joint_stack_idx]
                                 .joints[joint.joint_idx - 1]
                                 .block_idx]; // the block just before this in the stack
    const ft_block& block2 = design.design_blocks[joint.block_idx];

    b2RevoluteJointDef joint_def;
    joint_def.body1 = block1.body;
    joint_def.body2 = block2.body;
    joint_def.anchorPoint.Set(js.x, js.y);
    joint_def.collideConnected = true;

    ft_joint_type::type jt = ft_joint_type::UPW;
    ft_joint_type::type jt1 = joint_type(block1.type);
    if (jt1 != ft_joint_type::UPW) {
        jt = jt1;
    } else {
        // negative because block1 and block2 are jointed in the opposite order as in the first case
        jt = static_cast<ft_joint_type::type>(-joint_type(block2.type));
    }

    if (jt != ft_joint_type::UPW) {
        joint_def.motorTorque = 50000000;
        joint_def.motorSpeed = -5 * jt;
        joint_def.enableMotor = true;
    }
    world->CreateJoint(&joint_def);
}

ft_sim_state::~ft_sim_state() {
    world->CleanBodyList();
    delete world;
}

class collision_filter : public b2CollisionFilter {
    bool ShouldCollide(b2Shape* s1, b2Shape* s2) {
        if (!b2_defaultFilter.ShouldCollide(s1, s2))
            return false;

        ft_block* b1 = static_cast<ft_block*>(s1->GetUserData());
        ft_block* b2 = static_cast<ft_block*>(s2->GetUserData());

        for (uint16_t js_idx1 : b1->joint_stack_idxs) {
            if (js_idx1 == FT_NO_JOINT_STACK)
                goto checked_for_intersection;

            for (uint16_t js_idx2 : b2->joint_stack_idxs) {
                if (js_idx2 == FT_NO_JOINT_STACK)
                    goto checked_for_intersection;

                if (js_idx1 == js_idx2)
                    return false;
            }
        }

    checked_for_intersection:
        return true;
    }
};

static collision_filter ft_collision_filter;

std::shared_ptr<ft_sim_state> ft_create_sim(std::shared_ptr<ft_sim_state> handle,
                                            const ft_design_spec& spec,
                                            const ft_sim_settings& settings) {
    if (!handle) {
        handle = std::make_shared<ft_sim_state>();
    }

    b2Vec2 gravity(0, 300);
    b2AABB aabb;
    aabb.minVertex.Set(-ARENA_WIDTH, -ARENA_HEIGHT);
    aabb.maxVertex.Set(ARENA_WIDTH, ARENA_HEIGHT);
    handle->world = new b2World(aabb, gravity, true);
    handle->world->SetFilter(&ft_collision_filter);

    ft_create_design(&handle->design, spec);

    for (auto& block : handle->design.level_blocks)
        generate_body(handle->world, block);

    for (auto& block : handle->design.design_blocks)
        generate_body(handle->world, block);

    for (auto& js : handle->design.joint_stacks) {
        // start from 1 because a js of size 1 generates nothing
        for (size_t i = 0; i < js.joints.size(); i++) {
            ft_joint& joint = js.joints[i];
            generate_joint(handle->world, handle->design, js, joint);
        }
    }

    return handle;
}

void ft_step_sim(std::shared_ptr<ft_sim_state> handle, const ft_sim_settings& settings) {
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

    for (auto& block : handle->design.level_blocks) {
        b2Vec2 pos = block.body->GetOriginPosition();
        float64 angle = block.body->GetRotation();

        block.x = pos.x._v;
        block.y = pos.y._v;
        block.angle = angle._v;
    }

    for (auto& block : handle->design.design_blocks) {
        b2Vec2 pos = block.body->GetOriginPosition();
        float64 angle = block.body->GetRotation();

        block.x = pos.x._v;
        block.y = pos.y._v;
        block.angle = angle._v;
    }

    handle->tick++;
}

bool ft_in_area(const ft_block& block, const ft_rect& area) {
    bool is_circle = block_physics_tbl[block.type].circle;
    double bex = ft_mul(block.w, 0.5);
    double bey = ft_mul(block.h, 0.5);
    double area_ex = ft_mul(area.w, 0.5);
    double area_ey = ft_mul(area.h, 0.5);
    double area_xa = ft_sub(area.x, area_ex);
    double area_xb = ft_add(area.x, area_ex);
    double area_ya = ft_sub(area.y, area_ey);
    double area_yb = ft_add(area.y, area_ey);
    if (is_circle) {
        return ft_sub(block.x, bex) >= area_xa && ft_add(block.x, bex) <= area_xb &&
               ft_sub(block.y, bey) >= area_ya && ft_add(block.y, bey) <= area_yb;
    }
    double x = block.x;
    double y = block.y;
    double x0 = ft_mul(ft_cos(block.angle), bex);
    double y0 = ft_mul(ft_sin(block.angle), bex);
    double x1 = ft_mul(ft_sin(block.angle), bey);
    double y1 = ft_mul(-ft_cos(block.angle), bey);

#define ft_in_area_CHECK_CORNER(valx, valy)                                                        \
    {                                                                                              \
        double xx = valx;                                                                          \
        double yy = valy;                                                                          \
        if (xx < area_xa || xx > area_xb || yy < area_ya || yy > area_yb)                          \
            return false;                                                                          \
    }
    ft_in_area_CHECK_CORNER(ft_add(ft_add(x, x0), x1), ft_add(ft_add(y, y0), y1));
    ft_in_area_CHECK_CORNER(ft_add(ft_sub(x, x0), x1), ft_add(ft_sub(y, y0), y1));
    ft_in_area_CHECK_CORNER(ft_sub(ft_add(x, x0), x1), ft_sub(ft_add(y, y0), y1));
    ft_in_area_CHECK_CORNER(ft_sub(ft_sub(x, x0), x1), ft_sub(ft_sub(y, y0), y1));
#undef ft_in_area_CHECK_CORNER

    return true;
}

bool ft_is_solved(const std::shared_ptr<ft_sim_state> sim, const ft_design_spec& spec) {
    bool goal_exist = false;
    for (auto& block : sim->design.design_blocks) {
        if (!ft_is_goal_object(block.type))
            continue;
        goal_exist = true;
        if (!ft_in_area(block, spec.goal))
            return false;
    }
    return goal_exist;
}