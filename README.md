# Qwen Image References Manager

An image-only ComfyUI reference manager for Qwen Image 2.1. It accepts up to ten uploaded images, applies crop, rotation, and horizontal mirroring, and emits ten `IMAGE` sockets (`image_1` through `image_10`). Empty sockets return `None`.

This pack deliberately does not generate prompts and has no video or audio support. The prompt remains the responsibility of the Qwen workflow's text encoder.

## Install

Install from ComfyUI Manager by searching for **Qwen Image References Manager**, or clone it directly:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Hearmeman24/ComfyUI-QwenImageRefPack.git
```

Restart ComfyUI after installation.

## Use

Add **Qwen Image References Manager** from the **Qwen Image** category. Click the upload tile in the black canvas and choose up to ten images. Images fill the compact 5×2 reference grid in socket order. Double-click an image tile, or use its edit control, to crop, rotate, or mirror it.

`max_reference_edge` limits the emitted image's longest edge. Set it to `0` to disable downscaling.

## Development

```bash
pytest -q
node --check web/qwen_image_refpack.js
```
