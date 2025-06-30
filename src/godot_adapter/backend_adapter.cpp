#include "backend_adapter.hpp"

ftb_slot _ftb_global_slots[FTBACKEND_SLOTS];

String to_gd(std::string s) {
  return String(s.c_str());
}

std::string from_gd(String s) {
  std::string result;
  for(int i = 0; i < s.length(); ++i) {
    result += char(s[i]);
  }
  return result;
}

void FTBackend::_bind_methods() {
  ClassDB::bind_method(D_METHOD("get_num_slots"), &FTBackend::get_num_slots);
  ClassDB::bind_method(D_METHOD("clear_slot", "index"), &FTBackend::clear_slot);
  ClassDB::bind_method(D_METHOD("set_blocks", "index", "type", "x", "y", "w", "h", "r", "j1", "j2"), &FTBackend::set_blocks);
  ClassDB::bind_method(D_METHOD("set_build", "index", "rect"), &FTBackend::set_build);
  ClassDB::bind_method(D_METHOD("set_goal", "index", "rect"), &FTBackend::set_goal);
  ClassDB::bind_method(D_METHOD("start_sim", "index"), &FTBackend::start_sim);
  ClassDB::bind_method(D_METHOD("step_sim", "index"), &FTBackend::step_sim);
  ClassDB::bind_method(D_METHOD("check_solved", "index"), &FTBackend::check_solved);
  ClassDB::bind_method(D_METHOD("get_slice", "index", "xywhr_index"), &FTBackend::get_slice);
  ClassDB::bind_method(D_METHOD("math_hash"), &FTBackend::math_hash);
  ClassDB::bind_method(D_METHOD("dtostr", "value"), &FTBackend::dtostr);
  ClassDB::bind_method(D_METHOD("strtod", "value"), &FTBackend::strtod);
  ClassDB::bind_method(D_METHOD("get_assert_flags"), &FTBackend::get_assert_flags);
}

FTBackend::FTBackend() {
    // Initialize any variables here.
}

FTBackend::~FTBackend() {
    // Add your cleanup here.
}

int FTBackend::get_num_slots() {
  return FTBACKEND_SLOTS;
}

void FTBackend::clear_slot(int si) {
  _ftb_global_slots[si] = ftb_slot();
}

void FTBackend::set_blocks(int si, PackedInt64Array t, PackedDoubleArray x, PackedDoubleArray y, PackedDoubleArray w, PackedDoubleArray h, PackedDoubleArray r, PackedInt64Array j1, PackedInt64Array j2) {
  auto& spec = _ftb_global_slots[si].spec;
  spec.blocks = std::vector<fcsim_block_def>();
  int j = 0;
  for(int i = 0; i < t.size(); ++i) {
    fcsim_block_def bdef = {static_cast<uint8_t>(t[i]), FCSIM_NO_JOINT, x[i], y[i], w[i], h[i], r[i], static_cast<uint16_t>(j1[i]), static_cast<uint16_t>(j2[i])};
    if(type_is_player(bdef.type)) {
      bdef.id = j;
      ++j;
    }
    spec.blocks.push_back(bdef);
  }
}

void FTBackend::set_build(int si, PackedDoubleArray xywh) {
  auto& spec = _ftb_global_slots[si].spec;
  spec.build = {xywh[0], xywh[1], xywh[2], xywh[3]};
}

void FTBackend::set_goal(int si, PackedDoubleArray xywh) {
  auto& spec = _ftb_global_slots[si].spec;
  spec.goal = {xywh[0], xywh[1], xywh[2], xywh[3]};
}

void FTBackend::start_sim(int si) {
  _ftb_global_slots[si].sim = nullptr;
  _ftb_global_slots[si].sim = fcsim_new(nullptr, _ftb_global_slots[si].spec, _ftb_global_slots[si].settings);
}

void FTBackend::step_sim(int si) {
  fcsim_step(_ftb_global_slots[si].sim, _ftb_global_slots[si].settings);
}

bool FTBackend::check_solved(int si) {
  return fcsim_is_solved(_ftb_global_slots[si].sim, _ftb_global_slots[si].spec);
}

PackedDoubleArray FTBackend::get_slice(int si, int pi) {
  PackedDoubleArray result;
  auto& sim = _ftb_global_slots[si].sim;
  for(int i = 0; i < sim->block_cnt; ++i) {
    fcsim_block_def& bdef = sim->blocks[i].bdef;
    result.push_back(pi==0?bdef.x:pi==1?bdef.y:pi==2?bdef.w:pi==3?bdef.h:bdef.angle);
  }
  return result;
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
  if(get_assert_flag()) { result |= 1; }
  if(get_assertmem_flag()) { result |= 2; }
  return result;
}
