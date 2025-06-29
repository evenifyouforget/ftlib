#include <cmath>
#include "gstrfuncs.h"
#include "gstr_adapter.hpp"

std::string ft_dtostr(double v) {
  if(std::isnan(v)) {
    return "NaN";
  }
  char buf[32];
  g_ascii_dtostr(buf, 32, v);
  return std::string(buf);
}

double ft_strtod(const std::string& v) {
  char** stupid=nullptr;
  return g_ascii_strtod(v.c_str(), stupid);
}

double ft_strtod_elsenan(const std::string& v) {
  double result = ft_strtod(v);
  if(errno) {
    return std::nan("1");
  }
  return result;
}

std::optional<double> ft_strtod_checked(const std::string& v) {
  double x = ft_strtod(v);
  if(errno) {
    return std::nullopt;
  }
  return std::make_optional<double>(x);
}
