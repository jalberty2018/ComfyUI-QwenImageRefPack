# Qwen Image References Manager

Image-only reference nodes with crop, rotation, horizontal mirroring and optional
downscaling. The original upstream node retains its name, ID, inputs and ten
`IMAGE` outputs, so original workflows load without changing their node IDs.

## Nodes

| Display name | Node ID | Outputs | Source |
| --- | --- | --- | --- |
| Qwen Image References Manager | `QwenImageReferencePack` | `image_1` through `image_10` | Upload |
| Qwen Image References Manager (First/Last) | `QwenImageFirstLastReferencePack` | `First image`, `Last image`, `first_width`, `first_height`, `last_width`, `last_height` | Upload |
| Qwen Image References Manager (Local Input, First/Last) | `QwenImageLocalReferencePack` | `First image`, `Last image`, `first_width`, `first_height`, `last_width`, `last_height` | Local input |
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
The ten-image nodes retain `max_reference_edge` (0 disables downscaling).

### First/Last scaling

Both First/Last variants use the calculations from
[Scale Image to Total Pixels Adv](https://github.com/BigStationW/ComfyUi-Scale-Image-to-Total-Pixels-Advanced).
The scaler is integrated; installing that separate custom node is unnecessary.

- `megapixels`: target pixel count per image (default 1.05); 0 keeps the source size before multiple alignment.
- `multiple_of`: round each target dimension down to this multiple (default 16; the selected multiple is also the minimum output dimension).
- `resize_mode`: `stretch`, centered `crop` (default), or black `pad`.
- `upscale_method`: `nearest-exact`, `bilinear`, `area`, `bicubic`, or `lanczos` (default).
- `width` and `height`: optional fixed target dimensions. Set both above 0 to override megapixels; these dimensions are also aligned to `multiple_of`. Zero means automatic. Fields can be converted to connected inputs in ComfyUI.

The same settings apply independently to both images, after orientation and the
editor crop. Without a fixed width/height pair, each image keeps its own aspect
ratio before alignment. Outputs 0 and 1 remain First image and Last image;
four appended INT outputs report the actual scaled dimensions:
`first_width`, `first_height`, `last_width`, `last_height`.
An absent image returns `None` with width/height 0.

Old First/Last workflows retain their images and connections when opened in the
browser, and receive the new scaling defaults instead of the old edge limit.
Review the scaling settings and save the workflow after updating. Saved API
prompts should replace `max_reference_edge` with the new settings.
These nodes do not generate prompts and have no video or audio support.

## Development

```bash
pytest -q --confcutdir=tests
node --check web/qwen_image_refpack.js
```
