# C19 exterior refinement

This self-contained Blender script applies the reviewed C19 exterior changes to an untouched C18 source scene. It requires Blender 5.2.2 with its bundled NumPy.

- Refines the door shoulder and physically seats the exterior handles.
- Fits the grille, front bumper and headlamp details while retaining component topology.
- Rolls the tail downward and inward; seats both mesh outlets and curved chrome lips.
- Corrects the rear-glass/frame crescent and uses restrained neutral-black exterior materials.
- Retains all 967 original component identities, rest transforms and native explosion/return actions.

Run:

    blender -b SOURCE_C18.blend --python apply_c19_exterior.py -- --output OUTPUT_C19.blend

Do not run on an already-patched C19 scene. The C18 source is the input; this file is not a replacement for a Blender model.

The generated C19 GLB delivered separately is 70,039,044 bytes with SHA-256 `833bfcab9e61864b0dad57560b781700146508e313099e107ac9d771f33601ca`. Its 967 nodes, 726 original cabin components, 21 embedded images and 160-frame native motion passed independent preservation and decode checks. The exact browser Draco decoder also decoded all geometry successfully. This is not proof of live browser/mobile rendering performance.

Current limitations: the output is a review candidate, with a disclosed hood-ornament camera-projection tradeoff; reference-photo lighting is approximate. Final whole-car acceptance remains separate from structural tests. No user reference photographs or private service credentials are included here.
