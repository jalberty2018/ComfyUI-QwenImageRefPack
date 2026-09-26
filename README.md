# Qwen Image References Manager

An image-only ComfyUI reference manager for MiniMax H3 I2VA and FL2VA workflows. It accepts up to two uploaded images, applies crop, rotation, and horizontal mirroring, and emits two `IMAGE` sockets (`First image` and `Last image`). Empty sockets return `None`.

This pack deliberately does not generate prompts and has no video or audio support. Use `First image` for I2VA. For FL2VA, also connect `Last image` to the last-frame input. The prompt is supplied separately.

## Install

Install from ComfyUI Manager by searching for **Qwen Image References Manager**, or clone it directly:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Hearmeman24/ComfyUI-QwenImageRefPack.git
```

Restart ComfyUI after installation.

## Use

Add **Qwen Image References Manager** from the **Qwen Image** category. Click the upload tile in the black canvas and choose up to two images. Images fill the compact 2×1 reference grid in socket order. Double-click an image tile, or use its edit control, to crop, rotate, or mirror it.

`max_reference_edge` limits the emitted image's longest edge. Set it to `0` to disable downscaling.

Older workflows with more than two references must have the extra images removed before running.

## Development

```bash
pytest -q
node --check web/qwen_image_refpack.js
```

## Local input node

Add **Qwen Image References Manager (Local Input)** from **Qwen Image**. Click the add tile to browse images already in the ComfyUI server’s `input` directory, including subfolders. Filter by filename and choose the first image, then optionally the last image. No upload is needed. This node shares the two outputs, crop, rotation, mirroring, and `max_reference_edge` setting of the upload node. Delete a selected image to choose a replacement.

## Ten-image nodes

The existing two-image nodes remain available. Two additional nodes restore the
original 5 x 2 image grid:

- **Qwen Image References Manager (10 Images)**: upload up to ten images.
- **Qwen Image References Manager (Local Input, 10 Images)**: select up to ten images from the local ComfyUI server's `input` directory, including subfolders.

Both expose `image_1` through `image_10` in selection order; empty outputs return
`None`. Crop, rotation, mirroring and `max_reference_edge` work on each image.
Restart ComfyUI and refresh the browser, then find these nodes under **Qwen Image**.
