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

struct ftb_slot {
    ft_design_spec spec;
    std::shared_ptr<ft_sim_state> sim;
    ft_sim_settings settings;
};

// Doesn't actually contain any data. Every FTBackend instance will access the same shared slots.
class FTBackend : public RefCounted {
    GDCLASS(FTBackend, RefCounted)

protected:
    static void _bind_methods();

public:
    FTBackend();
    ~FTBackend();

    int get_num_slots();
    void clear_slot(int);
    void set_blocks(int, PackedInt64Array, PackedDoubleArray, PackedDoubleArray, PackedDoubleArray, PackedDoubleArray, PackedDoubleArray, PackedInt64Array, PackedInt64Array);
    void set_build(int, PackedDoubleArray);
    void set_goal(int, PackedDoubleArray);
    void start_sim(int);
    void step_sim(int);
    bool check_solved(int);
    PackedDoubleArray get_slice(int, int);
    String math_hash();
    String dtostr(double);
    double strtod(String);
    int get_assert_flags();
};
