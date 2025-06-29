#ifndef _GSTR_ADAPTER_H_
#define _GSTR_ADAPTER_H_

#include <string>
#include <optional>

std::string ft_dtostr(double);
double ft_strtod(const std::string&);
double ft_strtod_elsenan(const std::string&);
std::optional<double> ft_strtod_checked(const std::string&);

#endif
