#ifndef FTMATH_H_
#define FTMATH_H_

#ifdef __cplusplus
extern "C" {
#endif

#ifdef USE_FPATAN
// use fpatan x86 instruction
// see fpatan.s
double fpatan(double y, double x);
#endif

double ftref_atan2(double, double);
double ftref_sin(double);
double ftref_cos(double);
double s794_sin(double);
double s794_cos(double);
double true_sin(double);
double true_cos(double);

double ft_add(double, double);
double ft_sub(double, double);
double ft_mul(double, double);
double ft_div(double, double);
double ft_rem(double, double);
double ft_sqrt(double);
double ft_sin(double);
double ft_cos(double);
double ft_atan2(double, double);

long double extra_sinl(long double x);
long double extra_cosl(long double x);

#ifdef __cplusplus
}
#endif

#endif
