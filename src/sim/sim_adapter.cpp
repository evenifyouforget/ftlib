#include "sim_adapter.hpp"

void FTBlock::_bind_methods() {
    ClassDB::bind_static_method("FTBlock", D_METHOD("init", "type", "id", "x", "y", "w", "h", "angle", "j1", "j2"), &FTBlock::init);
    ClassDB::bind_method(D_METHOD("set_type", "type"), &FTBlock::set_type);
    ClassDB::bind_method(D_METHOD("get_type"), &FTBlock::get_type);
    ClassDB::bind_method(D_METHOD("set_id", "id"), &FTBlock::set_id);
    ClassDB::bind_method(D_METHOD("get_id"), &FTBlock::get_id);
    ClassDB::bind_method(D_METHOD("set_x", "x"), &FTBlock::set_x);
    ClassDB::bind_method(D_METHOD("get_x"), &FTBlock::get_x);
    ClassDB::bind_method(D_METHOD("set_y", "y"), &FTBlock::set_y);
    ClassDB::bind_method(D_METHOD("get_y"), &FTBlock::get_y);
    ClassDB::bind_method(D_METHOD("set_w", "w"), &FTBlock::set_w);
    ClassDB::bind_method(D_METHOD("get_w"), &FTBlock::get_w);
    ClassDB::bind_method(D_METHOD("set_h", "h"), &FTBlock::set_h);
    ClassDB::bind_method(D_METHOD("get_h"), &FTBlock::get_h);
    ClassDB::bind_method(D_METHOD("set_angle", "angle"), &FTBlock::set_angle);
    ClassDB::bind_method(D_METHOD("get_angle"), &FTBlock::get_angle);
    ClassDB::bind_method(D_METHOD("set_joint_1", "joint"), &FTBlock::set_joint_1);
    ClassDB::bind_method(D_METHOD("get_joint_1"), &FTBlock::get_joint_1);
    ClassDB::bind_method(D_METHOD("set_joint_2", "joint"), &FTBlock::set_joint_2);
    ClassDB::bind_method(D_METHOD("get_joint_2"), &FTBlock::get_joint_2);

    ADD_PROPERTY(PropertyInfo(Variant::INT, "type"), "set_type", "get_type");
    ADD_PROPERTY(PropertyInfo(Variant::INT, "id"), "set_id", "get_id");
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "x"), "set_x", "get_x");
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "y"), "set_y", "get_y");
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "w"), "set_w", "get_w");
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "h"), "set_h", "get_h");
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "angle"), "set_angle", "get_angle");
    ADD_PROPERTY(PropertyInfo(Variant::INT, "joint_1"), "set_joint_1", "get_joint_1");
    ADD_PROPERTY(PropertyInfo(Variant::INT, "joint_2"), "set_joint_2", "get_joint_2");
}

Ref<FTBlock> FTBlock::init(uint16_t type, uint16_t id, double x, double y, double w, double h, double angle, uint16_t j1, uint16_t j2) {
    Ref<FTBlock> block;
    block.instantiate();
    fcsim_block_def bdef{type, id, x, y, w, h, angle, {j1, j2}};
    block->bdef = bdef;
    return block;
}

void FTBlock::set_type(uint16_t type) {
    bdef.type = type;
}

uint16_t FTBlock::get_type() const {
    return bdef.type;
}

void FTBlock::set_id(uint16_t id) {
    bdef.id = id;
}

uint16_t FTBlock::get_id() const {
    return bdef.id;
}

void FTBlock::set_x(double x) {
    bdef.x = x;
}

double FTBlock::get_x() const {
    return bdef.x;
}

void FTBlock::set_y(double y) {
    bdef.y = y;
}

double FTBlock::get_y() const {
    return bdef.y;
}

void FTBlock::set_w(double w) {
    bdef.w = w;
}

double FTBlock::get_w() const {
    return bdef.w;
}

void FTBlock::set_h(double h) {
    bdef.h = h;
}

double FTBlock::get_h() const {
    return bdef.h;
}

void FTBlock::set_angle(double angle) {
    bdef.angle = angle;
}

double FTBlock::get_angle() const {
    return bdef.angle;
}

void FTBlock::set_joint_1(uint16_t joint) {
    bdef.joints[0] = joint;
}

uint16_t FTBlock::get_joint_1() const {
    return bdef.joints[0];
}

void FTBlock::set_joint_2(uint16_t joint) {
    bdef.joints[1] = joint;
}

uint16_t FTBlock::get_joint_2() const {
    return bdef.joints[1];
}

String to_gd(std::string s) {
    return String(s.c_str());
}

std::string from_gd(String s) {
    std::string result;
    for (int i = 0; i < s.length(); ++i) {
        result += char(s[i]);
    }
    return result;
}

void FTBackend::_bind_methods() {
    ClassDB::bind_static_method("FTBackend", D_METHOD("math_hash"), &FTBackend::math_hash);
    ClassDB::bind_static_method("FTBackend", D_METHOD("dtostr", "value"), &FTBackend::dtostr);
    ClassDB::bind_static_method("FTBackend", D_METHOD("strtod", "value"), &FTBackend::strtod);
    ClassDB::bind_static_method("FTBackend", D_METHOD("get_assert_flags"), &FTBackend::get_assert_flags);
    ClassDB::bind_static_method("FTBackend", D_METHOD("type_is_player", "type"), &FTBackend::type_is_player);
}

String FTBackend::math_hash() {
    return to_gd(ft_math_hash());
}

String FTBackend::dtostr(double v) {
    return to_gd(ft_dtostr(v));
}

double FTBackend::strtod(String s) {
    return ft_strtod_elsenan(from_gd(s));
}

int FTBackend::get_assert_flags() {
    int result = 0;
    if (get_assert_flag()) { result |= 1; }
    if (get_assertmem_flag()) { result |= 2; }
    return result;
}

bool FTBackend::type_is_player(uint16_t type) {
    return ::type_is_player(static_cast<int>(type));
}

void FTDesign::_bind_methods() {
    ClassDB::bind_method(D_METHOD("set_blocks", "blocks"), &FTDesign::set_blocks);
    ClassDB::bind_method(D_METHOD("set_blocks_packed", "type", "x", "y", "w", "h", "r", "j1", "j2"), &FTDesign::set_blocks_packed);
    ClassDB::bind_method(D_METHOD("set_build", "x", "y", "w", "h"), &FTDesign::set_build);
    ClassDB::bind_method(D_METHOD("set_goal", "x", "y", "w", "h"), &FTDesign::set_goal);
    ClassDB::bind_method(D_METHOD("start_sim"), &FTDesign::start_sim);
    ClassDB::bind_method(D_METHOD("step_sim"), &FTDesign::step_sim);
    ClassDB::bind_method(D_METHOD("check_solved"), &FTDesign::check_solved);
    ClassDB::bind_method(D_METHOD("get_blocks"), &FTDesign::get_blocks);
    ClassDB::bind_method(D_METHOD("get_slice"), &FTDesign::get_slice);
}

void FTDesign::set_blocks(const TypedArray<FTBlock> blocks) {
    spec.blocks = std::vector<fcsim_block_def>();
    for (int i = 0; i < blocks.size(); ++i) {
        Ref<FTBlock> block = blocks[i];
        fcsim_block_def bdef = block->bdef;
        spec.blocks.push_back(bdef);
    }
}

void FTDesign::set_blocks_packed(const PackedByteArray t, const PackedFloat64Array x, const PackedFloat64Array y, 
    const PackedFloat64Array w, const PackedFloat64Array h, const PackedFloat64Array r, const PackedInt32Array j1, const PackedInt32Array j2) {
    spec.blocks = std::vector<fcsim_block_def>();
    int j = 0;
    for (int i = 0; i < t.size(); ++i) {
        fcsim_block_def bdef = { static_cast<uint8_t>(t[i]), FCSIM_NO_JOINT, x[i], y[i], w[i], h[i], r[i], static_cast<uint16_t>(j1[i]), static_cast<uint16_t>(j2[i]) };
        if (type_is_player(bdef.type)) {
            bdef.id = j;
            ++j;
        }
        spec.blocks.push_back(bdef);
    }
}

void FTDesign::set_build(double x, double y, double w, double h) {
    spec.build = { x, y, w, h };
}

void FTDesign::set_goal(double x, double y, double w, double h) {
    spec.goal = { x, y, w, h };
}

void FTDesign::start_sim() {
    sim = nullptr;
    sim = fcsim_new(nullptr, spec, settings);
}

void FTDesign::step_sim() {
    fcsim_step(sim, settings);
}

bool FTDesign::check_solved() const {
    return fcsim_is_solved(sim, spec);
}

PackedFloat64Array FTDesign::get_slice(int pi) const {
    PackedFloat64Array result;
    for (int i = 0; i < sim->block_cnt; ++i) {
        fcsim_block_def& bdef = sim->blocks[i].bdef;
        result.push_back(pi == 0 ? bdef.x : pi == 1 ? bdef.y : pi == 2 ? bdef.w : pi == 3 ? bdef.h : bdef.angle);
    }
    return result;
}

TypedArray<FTBlock> FTDesign::get_blocks() const {
    TypedArray<FTBlock> result;
    for (int i = 0; i < sim->block_cnt; ++i) {
        fcsim_block_def& bdef = sim->blocks[i].bdef;
        Ref<FTBlock> block;
        block.instantiate();
        block->bdef = bdef;
        result.push_back(block);
    }
    return result;
}