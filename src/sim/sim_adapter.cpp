#include "sim_adapter.hpp"

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
    ClassDB::bind_method(D_METHOD("dtostr", "value"), &FTBackend::dtostr);
    ClassDB::bind_method(D_METHOD("strtod", "value"), &FTBackend::strtod);
    ClassDB::bind_method(D_METHOD("get_assert_flags"), &FTBackend::get_assert_flags);
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

void FTDesign::_bind_methods() {
    ClassDB::bind_method(D_METHOD("set_blocks", "type", "x", "y", "w", "h", "r", "j1", "j2"), &FTDesign::set_blocks);
    ClassDB::bind_method(D_METHOD("set_build", "x", "y", "w", "h"), &FTDesign::set_build);
    ClassDB::bind_method(D_METHOD("set_goal", "x", "y", "w", "h"), &FTDesign::set_goal);
    ClassDB::bind_method(D_METHOD("start_sim"), &FTDesign::start_sim);
    ClassDB::bind_method(D_METHOD("step_sim"), &FTDesign::step_sim);
    ClassDB::bind_method(D_METHOD("check_solved"), &FTDesign::check_solved);
    ClassDB::bind_method(D_METHOD("get_slice"), &FTDesign::get_slice);
}

void FTDesign::set_blocks(const PackedByteArray t, const PackedFloat64Array x, const PackedFloat64Array y, 
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

PackedDoubleArray FTDesign::get_slice(int pi) const {
    PackedDoubleArray result;
    for (int i = 0; i < sim->block_cnt; ++i) {
        fcsim_block_def& bdef = sim->blocks[i].bdef;
        result.push_back(pi == 0 ? bdef.x : pi == 1 ? bdef.y : pi == 2 ? bdef.w : pi == 3 ? bdef.h : bdef.angle);
    }
    return result;
}