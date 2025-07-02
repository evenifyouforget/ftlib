#include "register_types.h"

#include "sim_adapter.hpp"
#include "render.h"

void initialize_ftlib_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }
    ClassDB::register_class<FTRender>();

    ClassDB::register_class<FTBlock>();
    ClassDB::register_class<FTBackend>();
    ClassDB::register_class<FTDesign>();
}

void uninitialize_ftlib_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }
    // Nothing to do here in this example.
}
