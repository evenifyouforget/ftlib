#include "register_types.h"

#include "core/object/class_db.h"
#include "summator.h"
#include "render.h"

void initialize_ftlib_module(ModuleInitializationLevel p_level) {
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
		return;
	}
	ClassDB::register_class<Summator>();
    ClassDB::register_class<FTRender>();
}

void uninitialize_ftlib_module(ModuleInitializationLevel p_level) {
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
		return;
	}
   // Nothing to do here in this example.
}