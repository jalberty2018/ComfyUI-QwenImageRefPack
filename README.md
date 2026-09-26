# Qwen Image References Manager

Image-only reference nodes with crop, rotation, horizontal mirroring and optional
downscaling. The original upstream node retains its name, ID, inputs and ten
`IMAGE` outputs, so original workflows load without changing their node IDs.

## Nodes

| Display name | Node ID | Outputs | Source |
| --- | --- | --- | --- |
| Qwen Image References Manager | `QwenImageReferencePack` | `image_1` through `image_10` | Upload |
| Qwen Image References Manager (First/Last) | `QwenImageFirstLastReferencePack` | `First image`, `Last image` | Upload |
| Qwen Image References Manager (Local Input, First/Last) | `QwenImageLocalReferencePack` | `First image`, `Last image` | Local input |
| Qwen Image References Manager (Local Input, 10 Images) | `QwenImageLocalReferencePack10` | `image_1` through `image_10` | Local input |

`QwenImageReferencePack10` is retained as a compatibility alias for the previous
fork release, displayed as **Qwen Image References Manager (10 Images, Legacy Fork ID)**.
For new ten-image upload nodes, use **Qwen Image References Manager**.

Earlier fork versions reused the upstream ID for a two-image upload node.
Those saved nodes now load as the original ten-image node: their first two
connections retain the same output indices, and eight more outputs are available.
To keep the compact two-image layout, replace them with **Qwen Image References
Manager (First/Last)** and reconnect the first/last outputs.

## Install

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jalberty2018/ComfyUI-QwenImageRefPack.git
```

Restart ComfyUI and refresh the browser after installing or updating.

## Use

Find the nodes under **Qwen Image**. Click the add tile to upload images, or to
browse the ComfyUI server's local `input` directory (including subfolders) in a
Local Input node. Local selection supports filename filtering and needs no upload.
Images fill the grid in output order: 5 x 2 for ten images, 2 x 1 for first/last.
Empty outputs return `None`.

Double-click a tile or use its edit control to crop, rotate or mirror it.
`max_reference_edge` limits the longest edge; set it to `0` to disable downscaling.
These nodes do not generate prompts and have no video or audio support.

## Development

```bash
pytest -q --confcutdir=tests
node --check web/qwen_image_refpack.js
```
