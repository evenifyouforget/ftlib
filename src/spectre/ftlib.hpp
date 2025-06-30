#ifndef FTLIB_HPP_
#define FTLIB_HPP_

#include <string>

#ifdef __cplusplus
extern "C" {
#endif
#include "softfloat.h"
#include "ftmath.h"
#ifdef __cplusplus
}
#endif

std::string ft_math_hash();

double _as_double(uint64_t i);
uint64_t _as_int(double f);

#endif
