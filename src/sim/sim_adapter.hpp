#include "ftlib.hpp"
#include "fcsim.h"
#include "gstr_adapter.hpp"

#include "core/object/ref_counted.h"

#define FTBACKEND_SLOTS 256
#define PackedDoubleArray PackedFloat64Array

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
    void set_blocks(const PackedByteArray t, const PackedFloat64Array x, const PackedFloat64Array y, 
        const PackedFloat64Array w, const PackedFloat64Array h, const PackedFloat64Array r, const PackedInt32Array j1, const PackedInt32Array j2);
    void set_build(double x, double y, double w, double h);
    void set_goal(double x, double y, double w, double h);
    void start_sim();
    void step_sim();
    bool check_solved() const;
    PackedDoubleArray get_slice(int pi) const;
};
