#include "register_types.h"

#include "backend_adapter.hpp"
#include "render.h"

void initialize_ftlib_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }
    ClassDB::register_class<FTRender>();
    ClassDB::register_class<FTBackend>();
}

void uninitialize_ftlib_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }
    // Nothing to do here in this example.
}
