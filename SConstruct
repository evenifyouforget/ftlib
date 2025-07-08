import os

env = Environment(CXX='g++', CXXFLAGS='-std=c++17', CPPPATH=['src'], LIBS=[], LIBPATH=[])

env['godot'] = False  # Custom flag for shared SConscript logic

Export('env')
SConscript('src/SCsub')
SConscript('example/SCsub')
SConscript('cli_adapter/SCsub')