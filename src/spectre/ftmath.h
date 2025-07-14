#ifndef FTMATH_H_
#define FTMATH_H_

#ifdef __cplusplus
extern "C" {
#endif

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

int _fcsim_strtod(const char *str, int len, double *res);

#ifdef __cplusplus
}
#endif

#endif
