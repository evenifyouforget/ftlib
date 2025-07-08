#include "fcsim.h"

//a simple 3pc solve for mind the gap
ft_design_spec make_the_design() {
    ft_design_spec result;
    result.build = {90.0, 109.0, 404.0, 166.0};
    result.goal = {562.8, 123.4, 159.10000000000002, 135.70000000000002};
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(0), 65535, 94.75, 228.35, 412.0, 92.0, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(0), 65535, 528.8, 229.4, 254.0, 90.0, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(1), 65535, -101.3, 231.75, 100.0, 100.0, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(1), 65535, 662.1, 279.1, 186.8, 186.8, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(1), 65535, 27.75, 27.749999999999996, 122.6, 122.6, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(0), 65535, 640.1500000000001, 35.8, 42.3, 68.60000000000001, 2.050224006112992, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(1), 65535, 444.1, 268.8, 100.0, 100.0, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(1), 65535, 158.4, 316.8, 192.8, 192.8, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(1), 65535, 521.45, 305.5500000000001, 143.0, 143.0, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(5), 0, 268.54999999999995, 42.050000000000004, 26.0, 26.0, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(7), 1, 139.05, 155.45, 40.0, 40.0, 0.0, 65535, 65535});
    result.blocks.push_back({static_cast<fcsim_piece_type::type>(9), 2, 203.79999999999998, 98.75, 172.13311709255711, 4.0, 2.4223800985162875, 0, 1});
    return result;
}