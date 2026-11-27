# CAD project

Parametric parts are modeled in [SolidCraft](https://github.com/tangency-labs/solidcraft). The design `parts/<name>/<name>.sc` is the source. STEP and PNG are exports. Do not commit STL files.

Drive SolidCraft through the `solidcraft` MCP server, or `solidcraft-cli` for batch runs and re-exports. Do not use other CAD kernels or generate parts from scripts outside SolidCraft. Command shapes, plane axes and known traps: `skill_reference {"skill":"solidcraft-modeling"}`.

Reply in the user's language. A German request gets a German answer.

## Make a part

Do this when the user describes a part or asks to change one. Create the folder and export without asking. Proceed on stated assumptions. Ask only when a missing main dimension makes the body impossible, such as an unknown length.

1. Name the part by what it is: English kebab-case, ASCII, two to four words (`flat-ring`, `servo-bracket`). A purpose the user gave wins. Dimensions stay in parameters, so a size change keeps the folder. A second similar part gets its own purpose name.
2. For a change, open the existing `.sc` and edit its parameters or features. Do not rebuild it from nothing.
3. Work the numbers out first: parameters, expected volume and bounding box. Then build following the design rules below.
4. Check the geometry. A file that saves can still be the wrong part:
   - one body per part, closed, no feature errors;
   - bounding box matches the named dimensions;
   - volume matches the estimate. A volume that did not change means a cut missed or a join did not touch;
   - `check_parameters` with 2 or 3 changed main parameters gives no errors and a plausible part;
   - print check: no flat overhang above the bed with a span over 5 mm, large bed contact face;
   - for a mating or holding part, overlap with a stand-in of the other part is 0.
5. Save and export all three files into `parts/<name>/`, each under the folder name:
   - `file.save_as` for `.sc`;
   - `export` for `.step`;
   - `screenshot {"view":"iso","source":"model","grid":false,"axes":false,"width":900,"height":650,"path":...}` for `.png`.

   Exports do not follow the design by themselves. Redo all of them after every change.
6. Refresh the README parts table: `python3 update_readme.py`. CI does the same on push.
7. Report the paths, named dimensions, checked size and volume, print orientation and every assumption, in the user's language.

Done when design and exports are saved, the checks hold, and the user has those facts.

If the MCP refuses a project path, the server was started without `--allow-path` for this repository. Use the project `opencode.json` entry, or export with the CLI:

```sh
solidcraft-cli run --in parts/<name>/<name>.sc --out parts/<name>/<name>.step
solidcraft-cli snapshot parts/<name>/<name>.sc --out parts/<name>/<name>.png --view iso --no-grid --no-axes --width 900 --height 650
```

## Design rules

- Millimeters, unless the user says otherwise.
- Every main dimension is a named parameter (snake_case, English); derived values are parameter expressions. A comment on the parameter explains a value that is not obvious, such as a spec tolerance. Counts are unitless parameters.
- Feature fields and sketch points use those parameters. Every sketch ends at dof 0.
- Features and sketches have unique English names.
- Set the design property `description` to one line saying what the part is. The README table shows it. State the print orientation in the custom property `io.github.cads.print`, as `document.metadata.set {"key":"io.github.cads.print","value":{"orientation":"..."}}`.
- Prefer primitives (box, cylinder, hole, fillet, shell, pattern, mirror); sketch when the profile is not a box or circle. Fillet and chamfer late.
- Edge and face picks are plain points. Check the face count after a fillet or chamfer.
- The part must be 3D-printable (FDM by default). Pick a print orientation with the largest flat face on the bed. Avoid overhangs steeper than 45 degrees, bridges over 5 mm (a wide window in a vertical wall needs a pointed or 45 degree chamfered head), walls under 1.2 mm and unsupported features. Mating parts get 0.3 mm clearance per side.
- One fused body. Several bodies only for an assembly the user asked for.
- Model the features the user named.

A named thread is a hole. An unqualified "M3 hole" uses the clearance diameter. Say which column you used.

| Thread | Clearance | Tap drill |
| --- | --- | --- |
| M2 | 2.4 | 1.6 |
| M3 | 3.4 | 2.5 |
| M4 | 4.5 | 3.3 |
| M5 | 5.5 | 4.2 |
| M6 | 6.6 | 5.0 |
| M8 | 9.0 | 6.8 |

A requested STL is exported beside the STEP and kept out of git. A requested 2D profile is exported with `sketch.export_dxf` or `sketch.export_svg` beside the design.
