# ftlib

## Notice: Under Construction

ftlib is currently going through a major reorganization (as of 2025-06).
Many files and directory structures may change.
The library is useless on its own, and to make it playable as a game (in other words, to provide a frontend), we intend to integrate it directly into Godot 4 as a Godot module, however the exact details are still being worked on.

## About licenses

ftlib takes parts from box2d, glib, openlibm, and SoftFloat3e.
Also Godot, if integrated.
We include their license files, if you want to inspect them.

We are forced to use a LGPL license for the combined overall project, since glib is LGPL.
(or at least, I don't feel legally safe to use MIT)

## What can you do with ftlib?

* Run (simulate) designs
* Modify designs
* Check your spectre

## What functionality does ftlib not include? (yet)

* Test
* Convert designs between formats
* Enforce game rules like valid joint connections and goal check
* Loading and saving designs to the main server using the HTTP API
* Browse levels and designs on the main server using the HTTP API
* Use a graphical interface to actually "play" the game
* The entire rest of the game

## What is the mission of Flying Triangles and ftlib?

"To provide a modern client for Fantastic Contraption that can completely replace the original client."

This implies reproducing all the game logic and game features, or at least the ones players care about.
If we don't do it exactly correct, it may be a flaw that prevents the adoption of this new client.

## Where is Flying Triangles and ftlib now?

* Behind fcsim (my fork)
* Mostly done on the simulation side, but far from overall feature parity with FC

## What does this build?

It builds Godot, with ftlib as a Godot module.

We need ftlib under `godot/modules/` to include it as a Godot module, but we don't want to fork Godot directly or make excessive assumptions about the Godot git structure that will end up baked into our architecture, so we include Godot as a submodule, don't modify it directly, and instead copy Godot to a build directory, and copy in ftlib to that copy of Godot, and then build Godot.