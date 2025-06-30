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

It builds Godot, with ftlib as a Godot module using the custom modules feature.

So we can make as few assumptions about Godot's git structure, Godot is included as a submodule.
We don't modify Godot's files directly, at all, instead we use the custom modules feature to include `src/` at the equivalent of `godot/modules/ftlib/`
by copying it to a temporary `build/modules/ftlib/` and specifying to use `build/modules/` as the custom modules directory.

Try `build.py`.

Since we build with Godot directly, all the results go in `godot/bin/` as usual.

# Developer guidelines

For all new code contributed, please try to follow these guidelines.
They are not hard rules, but are likely to result in higher quality code based on our experience.

## Programming language

* Internal/engine code should use C++
* Scripts/meta code should use Python
* Build files should use scons
* Godot in-game files should use GDScript

## C/C++ quirks

* Be aware of our fixed-spectre math functions, and use them where appropriate, especially in game logic which needs to be consistent. You can find the list in `src/spectre/ftmath.h`.
* Make use of STL. We know Godot discourages it, but their reasons don't really apply to our use cases.
* Use `int64_t` for integers unless you have a very good reason to use another type. It avoids overflow errors and it's unlikely to impact performance.
* Assume the compiler is decently smart, and don't prematurely try to make low-level optimizations. We rely on a lot of inlining, including LTO (link time optimization) for maximum performance.
* Avoid macros like `#define`, unless you have a very good reason to use them. Global constants in particular are a terrible reason to use macros. You can use the old-style `extern const`, or the new-style `inline constexpr` (C++17). Do use `enum` types for enums.

## Git etiquette

* Use PRs. Never push to main. (GitHub is configured to block it)
* Use squash or rebase, not merge. Merge makes the git history a mess, and is sometimes erroneous. (GitHub is configured to block it)
* Test every new feature you add, with automated tests if possible. If you make any change at all, check the tests again.
* Document everything, especially if it's not obvious. Your future self and everyone else will thank you.
