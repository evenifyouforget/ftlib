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

#include "b2Settings.h"
#include <cstdlib>
#include <iostream>
#include <fstream>

int32 b2_byteCount = 0;

// Memory allocators. Modify these to use your own allocator.
void* b2Alloc(int32 size)
{
	size += 4;
	b2_byteCount += size;
	char* bytes = (char*)malloc(size);
	*(int32*)bytes = size;
	return bytes + 4;
}

void b2Free(void* mem)
{
	if (mem == NULL)
	{
		return;
	}

	char* bytes = (char*)mem;
	bytes -= 4;
	int32 size = *(int32*)bytes;
	b2Assert(b2_byteCount >= size);
	b2_byteCount -= size;
	free(bytes);
}

bool _assert_flag = false;
bool _assertmem_flag = false;

bool& get_assert_flag() {
	return _assert_flag;
}
bool& get_assertmem_flag() {
	return _assertmem_flag;
}

void b2logmsg(const char* msg) {
	//I murdered b2err because it was hella annoying
	//TODO: figure out what the errors actually were

	// std::ofstream out;
	// out.open("b2err.txt", std::ios_base::app);
	// out << msg;
	// out.close();
}
