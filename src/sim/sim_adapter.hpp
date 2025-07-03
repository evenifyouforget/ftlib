#include "ftlib.hpp"
#include "fcsim.h"
#include "gstr_adapter.hpp"

#include "core/object/ref_counted.h"
#include "core/variant/typed_array.h"

class FTBlock : public RefCounted {
    GDCLASS(FTBlock, RefCounted)

protected:
    static void _bind_methods();

public:
    fcsim_block_def bdef;

    //TODO: Replace uint16_t with proper enum for piece type. the enum already exists, it's just not bound
    static Ref<FTBlock> init(uint16_t type, uint16_t id, double x, double y, double w, double h, double angle, uint16_t j1, uint16_t j2);

    void set_type(uint16_t type);
    uint16_t get_type() const;

    void set_id(uint16_t id);
    uint16_t get_id() const;

    void set_x(double x);
    double get_x() const;

    void set_y(double y);
    double get_y() const;

    void set_w(double w);
    double get_w() const;

    void set_h(double h);
    double get_h() const;

    void set_angle(double angle);
    double get_angle() const;

    void set_joint_1(uint16_t joint);
    uint16_t get_joint_1() const;

    void set_joint_2(uint16_t joint);
    uint16_t get_joint_2() const;
};

class FTRect : public RefCounted {
    GDCLASS(FTRect, RefCounted)

protected:
    static void _bind_methods();

public:
    fcsim_rect rect;

    static Ref<FTRect> init(double x, double y, double w, double h);

    void set_x(double x);
    double get_x() const;

    void set_y(double y);
    double get_y() const;

    void set_w(double w);
    double get_w() const;

    void set_h(double h);
    double get_h() const;
};

bool& get_assert_flag();
bool& get_assertmem_flag();

String to_gd(std::string);
std::string from_gd(String);

class FTBackend : public RefCounted {
    GDCLASS(FTBackend, RefCounted)

protected:
    static void _bind_methods();

public:
    static String math_hash();
    static String dtostr(double);
    static double strtod(String);
    static int get_assert_flags();
    static bool type_is_player(uint16_t type);
};

class FTDesign : public RefCounted {
    GDCLASS(FTDesign, RefCounted)

protected:
    static void _bind_methods();

private:
    ft_design_spec spec;
    std::shared_ptr<ft_sim_state> sim;
    ft_sim_settings settings;

public:
    void set_blocks(const TypedArray<FTBlock> blocks);
    TypedArray<FTBlock> get_blocks() const;
    void set_blocks_packed(const PackedByteArray t, const PackedFloat64Array x, const PackedFloat64Array y, 
        const PackedFloat64Array w, const PackedFloat64Array h, const PackedFloat64Array r, const PackedInt32Array j1, const PackedInt32Array j2);
    PackedFloat64Array get_slice(int pi) const;
    void set_build(const Ref<FTRect> rect);
    Ref<FTRect> get_build() const;
    void set_goal(const Ref<FTRect> rect);
    Ref<FTRect> get_goal() const;
    void start_sim();
    void step_sim();
    bool check_solved() const;
};
