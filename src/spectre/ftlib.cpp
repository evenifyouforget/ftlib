#include <cmath>
#include "ftlib.hpp"
#include "gstr_adapter.hpp"

#ifdef USE_SYSTEM_MATH
double ft_sqrt(double x) {
  return std::sqrt(x);
}
double ft_sin(double x) {
  return std::sin(x);
}
double ft_cos(double x) {
  return std::cos(x);
}
double ft_atan2(double y, double x) {
  return std::atan2(y, x);
}
#else
#ifdef S794
double ft_sin(double x) {
  return s794_sin(x);
}
double ft_cos(double x) {
  return s794_cos(x);
}
#else
double ft_sin(double x) {
  return ftref_sin(x);
}
double ft_cos(double x) {
  return ftref_cos(x);
}
#endif
#ifdef USE_FPATAN
double ft_atan2(double y, double x) {
  return fpatan(y, x);
}
#else
double ft_atan2(double y, double x) {
  return ftref_atan2(y, x);
}
#endif
#endif

#ifdef HARDFLOAT_TOGGLE

double ft_add(double x, double y) { return x + y; }
double ft_sub(double x, double y) { return x - y; }
double ft_mul(double x, double y) { return x * y; }
double ft_div(double x, double y) { return x / y; }
double ft_rem(double x, double y) { return std::remainder(x, y); }

#else

union ccdouble {
  double f;
  float64_t i;
};

double ft_add(double x, double y) {
  ccdouble ccx; ccx.f = x;
  ccdouble ccy; ccy.f = y;
  ccdouble ccr; ccr.i = f64_add(ccx.i, ccy.i);
  return ccr.f;
}

double ft_sub(double x, double y) {
  ccdouble ccx; ccx.f = x;
  ccdouble ccy; ccy.f = y;
  ccdouble ccr; ccr.i = f64_sub(ccx.i, ccy.i);
  return ccr.f;
}

double ft_mul(double x, double y) {
  ccdouble ccx; ccx.f = x;
  ccdouble ccy; ccy.f = y;
  ccdouble ccr; ccr.i = f64_mul(ccx.i, ccy.i);
  return ccr.f;
}

double ft_div(double x, double y) {
  ccdouble ccx; ccx.f = x;
  ccdouble ccy; ccy.f = y;
  ccdouble ccr; ccr.i = f64_div(ccx.i, ccy.i);
  return ccr.f;
}

double ft_rem(double x, double y) {
  ccdouble ccx; ccx.f = x;
  ccdouble ccy; ccy.f = y;
  ccdouble ccr; ccr.i = f64_rem(ccx.i, ccy.i);
  return ccr.f;
}

#endif

union if64_t {
  uint64_t i;
  double f;
};

double _as_double(uint64_t i) {
  if64_t r;
  r.i = i;
  return r.f;
}

uint64_t _as_int(double f) {
  if (std::isnan(f)) {
    return 0x7ff8000000000000;
  }
  if64_t r;
  r.f = f;
  return r.i;
}

static inline uint64_t rotl(const uint64_t x, int k) {
  return (x << k) | (x >> (64 - k));
}

static uint64_t _xs_s[2];

void xs_reset() {
  _xs_s[0] = 0x461111;
  _xs_s[1] = 0xd1133c;
}

uint64_t xs_next() {
  const uint64_t s0 = _xs_s[0];
  uint64_t s1 = _xs_s[1];
  const uint64_t result = s0 + s1;

  s1 ^= s0;
  _xs_s[0] = rotl(s0, 24) ^ s1 ^ (s1 << 16); // a, b
  _xs_s[1] = rotl(s1, 37); // c

  return result;
}

void hash_combine(uint64_t& h, const uint64_t& v) {
  h *= 0x3750c1;
  h ^= h >> 19;
  h += 0xa1941e;
  h ^= v;
}

void hash_combine(uint64_t& h, const std::string& v) {
  hash_combine(h, v.size());
  for (auto it = v.begin(); it != v.end(); ++it) {
    hash_combine(h, *it);
  }
}

void hash_flush(std::string& result, uint64_t x) {
  for (int i = 0; i < 3; ++i) {
    char c = x & 0x1f;
    if (c < 10) { c += '0'; } else { c += 'A' - 10; }
    x >>= 5;
    result += c;
  }
  result += '.';
}

void check_dtostrtod(uint64_t& h, double v) {
  double u = ft_strtod(ft_dtostr(v));
  if (std::isnan(v) || u == v) { return; }
  h++;
}

const uint64_t M54S = 0x803fffffffffffff;
const uint64_t F1 = 0x3ff0000000000000;
const uint64_t A1 = -1;
const uint64_t MH_ITERATIONS = 10000000;

std::string ft_math_hash() {
  std::string result;
  // test add, sub
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t ui = xs_next();
      uint64_t vi = xs_next();
      double u = _as_double(ui);
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_add(u, v)));
      hash_combine(h, _as_int(ft_sub(u, v)));
      u = _as_double(ui & M54S);
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_add(u, v)));
      hash_combine(h, _as_int(ft_sub(u, v)));
      u = _as_double((ui & M54S) ^ F1);
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_add(u, v)));
      hash_combine(h, _as_int(ft_sub(u, v)));
      u = _as_double((ui & M54S) ^ A1);
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_add(u, v)));
      hash_combine(h, _as_int(ft_sub(u, v)));
    }
    hash_flush(result, h);
  }
  // test mul
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t ui = xs_next();
      uint64_t vi = xs_next();
      double u = _as_double(ui);
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_mul(u, v)));
      u = _as_double(ui & M54S);
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_mul(u, v)));
      u = _as_double((ui & M54S) ^ F1);
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_mul(u, v)));
      u = _as_double((ui & M54S) ^ A1);
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_mul(u, v)));
    }
    hash_flush(result, h);
  }
  // test div
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t ui = xs_next();
      uint64_t vi = xs_next();
      double u = _as_double(ui);
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_div(u, v)));
      u = _as_double(ui & M54S);
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_div(u, v)));
      u = _as_double((ui & M54S) ^ F1);
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_div(u, v)));
      u = _as_double((ui & M54S) ^ A1);
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_div(u, v)));
    }
    hash_flush(result, h);
  }
  // test rem
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t ui = xs_next();
      uint64_t vi = xs_next();
      double u = _as_double(ui);
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_rem(u, v)));
      u = _as_double(ui & M54S);
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_rem(u, v)));
      u = _as_double((ui & M54S) ^ F1);
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_rem(u, v)));
      u = _as_double((ui & M54S) ^ A1);
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_rem(u, v)));
    }
    hash_flush(result, h);
  }
  // test sqrt
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t vi = xs_next();
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_sqrt(v)));
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_sqrt(v)));
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_sqrt(v)));
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_sqrt(v)));
    }
    hash_flush(result, h);
  }
  // test sin+cos
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t vi = xs_next();
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_sin(v)));
      hash_combine(h, _as_int(ft_cos(v)));
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_sin(v)));
      hash_combine(h, _as_int(ft_cos(v)));
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_sin(v)));
      hash_combine(h, _as_int(ft_cos(v)));
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_sin(v)));
      hash_combine(h, _as_int(ft_cos(v)));
    }
    hash_flush(result, h);
  }
  // test sin
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t vi = xs_next();
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_sin(v)));
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_sin(v)));
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_sin(v)));
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_sin(v)));
    }
    hash_flush(result, h);
  }
  // test cos
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t vi = xs_next();
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_cos(v)));
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_cos(v)));
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_cos(v)));
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_cos(v)));
    }
    hash_flush(result, h);
  }
  // test atan2
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t ui = xs_next();
      uint64_t vi = xs_next();
      double u = _as_double(ui);
      double v = _as_double(vi);
      hash_combine(h, _as_int(ft_atan2(u, v)));
      u = _as_double(ui & M54S);
      v = _as_double(vi & M54S);
      hash_combine(h, _as_int(ft_atan2(u, v)));
      u = _as_double((ui & M54S) ^ F1);
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, _as_int(ft_atan2(u, v)));
      u = _as_double((ui & M54S) ^ A1);
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, _as_int(ft_atan2(u, v)));
    }
    hash_flush(result, h);
  }
  // test dtostr
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t vi = xs_next();
      double v = _as_double(vi);
      hash_combine(h, ft_dtostr(v));
      v = _as_double(vi & M54S);
      hash_combine(h, ft_dtostr(v));
      v = _as_double((vi & M54S) ^ F1);
      hash_combine(h, ft_dtostr(v));
      v = _as_double((vi & M54S) ^ A1);
      hash_combine(h, ft_dtostr(v));
    }
    hash_flush(result, h);
  }
  // test dtostr, strtod
  {
    xs_reset();
    uint64_t h = 0;
    for (int i = 0; i < MH_ITERATIONS; ++i) {
      uint64_t vi = xs_next();
      double v = _as_double(vi);
      check_dtostrtod(h, v);
      v = _as_double(vi & M54S);
      check_dtostrtod(h, v);
      v = _as_double((vi & M54S) ^ F1);
      check_dtostrtod(h, v);
      v = _as_double((vi & M54S) ^ A1);
      check_dtostrtod(h, v);
    }
    hash_flush(result, h);
  }
  result.pop_back();
  return result;
}
