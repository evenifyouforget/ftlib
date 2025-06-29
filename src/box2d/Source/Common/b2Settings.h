/*
* Copyright (c) 2006-2007 Erin Catto http://www.gphysics.com
*
* This software is provided 'as-is', without any express or implied
* warranty.  In no event will the authors be held liable for any damages
* arising from the use of this software.
* Permission is granted to anyone to use this software for any purpose,
* including commercial applications, and to alter it and redistribute it
* freely, subject to the following restrictions:
* 1. The origin of this software must not be misrepresented; you must not
* claim that you wrote the original software. If you use this software
* in a product, an acknowledgment in the product documentation would be
* appreciated but is not required.
* 2. Altered source versions must be plainly marked as such, and must not be
* misrepresented as being the original software.
* 3. This notice may not be removed or altered from any source distribution.
*/

#ifndef B2_SETTINGS_H
#define B2_SETTINGS_H

#include <cassert>
#include <cmath>
#include "ftmath.h"

bool& get_assert_flag();
bool& get_assertmem_flag();

void b2logmsg(const char*);
#define _b2AssertLogOnce(A, b, msg) if(!(A)) {if(!b()){b()=true;b2logmsg(msg);}}

#define NOT_USED(x) x
//#define b2Assert(A) assert((A))
#define b2Assert(A) _b2AssertLogOnce(A, get_assert_flag, "other error: " #A "\n")
#define b2AssertMemory(A) _b2AssertLogOnce(A, get_assertmem_flag, "memory error: " #A "\n")

typedef signed char	int8;
typedef signed short int16;
typedef signed int int32;
typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;

struct float64 {
  double _v;
  float64(): _v{0.0} {};
  float64(double v): _v{v} {};
  inline float64& operator=(double v) {_v=v;return *this;}
};

inline float64 operator+(const float64& lhs, const float64& rhs) {return {ft_add(lhs._v, rhs._v)};}
inline float64 operator-(const float64& lhs, const float64& rhs) {return {ft_sub(lhs._v, rhs._v)};}
inline float64 operator*(const float64& lhs, const float64& rhs) {return {ft_mul(lhs._v, rhs._v)};}
inline float64 operator/(const float64& lhs, const float64& rhs) {return {ft_div(lhs._v, rhs._v)};}
inline float64 operator-(const float64&lhs) {return {-lhs._v};}
inline void operator+=(float64& lhs, const float64&rhs) {lhs = lhs + rhs;}
inline void operator-=(float64& lhs, const float64&rhs) {lhs = lhs - rhs;}
inline void operator*=(float64& lhs, const float64&rhs) {lhs = lhs * rhs;}
inline void operator/=(float64& lhs, const float64&rhs) {lhs = lhs / rhs;}
#define _MAKE_CMP(op) inline bool operator op(const float64& lhs, const float64& rhs) {return lhs._v op rhs._v;}
_MAKE_CMP(==)
_MAKE_CMP(!=)
_MAKE_CMP(<)
_MAKE_CMP(<=)
_MAKE_CMP(>)
_MAKE_CMP(>=)
#define _MAKE_UMAP(op, redir) inline float64 op(const float64& lhs) {return {redir(lhs._v)};}
_MAKE_UMAP(sqrt, ft_sqrt)
_MAKE_UMAP(fabs, fabs)

const float64 b2_pi = 3.141592653589793;

// Define your unit system here. The default system is
// meters-kilograms-seconds. For the tuning to work well,
// your dynamic objects should be bigger than a pebble and smaller
// than a house.
const float64 b2_lengthUnitsPerMeter = 30.0;
const float64 b2_massUnitsPerKilogram = 1.0;
const float64 b2_timeUnitsPerSecond = 1.0;

// Use this for pixels:
//const float64 b2_lengthUnitsPerMeter = 50.0;



// Global tuning constants based on MKS units.

// Collision
const int32 b2_maxManifoldPoints = 2;
const int32 b2_maxShapesPerBody = 64;
const int32 b2_maxPolyVertices = 8;
const int32 b2_maxProxies = 4096;				// this must be a power of two
const int32 b2_maxPairs = 32768;	// this must be a power of two

// Dynamics
const float64 b2_linearSlop = 0.15;
const float64 b2_angularSlop = 0.03490658503988659;
const float64 b2_velocityThreshold = 30.0;
const float64 b2_maxLinearCorrection = 6.0;
const float64 b2_maxAngularCorrection = 0.13962634015954636;
const float64 b2_contactBaumgarte = 0.2;

// Sleep
const float64 b2_timeToSleep = 0.5;
const float64 b2_linearSleepTolerance = 0.3;
const float64 b2_angularSleepTolerance = 0.011111111111111112;


// Memory Allocation
extern int32 b2_byteCount;
void* b2Alloc(int32 size);
void b2Free(void* mem);

#endif
