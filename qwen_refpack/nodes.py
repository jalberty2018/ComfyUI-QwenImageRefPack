"""Qwen Image reference manager: image inputs only, no prompt generation."""
from __future__ import annotations
import hashlib
import os
from . import media, refs, scaling

DEFAULT_MAX_REFERENCE_EDGE = 2048

def _signature(reference_set: refs.ReferenceSet, input_dir: str) -> str:
    digest = hashlib.sha256()
    for ref in reference_set.references:
        path = refs.reference_path(input_dir, ref.file)
        try:
            stat = os.stat(path)
            digest.update(
                f"{ref.file}:{stat.st_mtime_ns}:{stat.st_size}:{ref.to_dict()}".encode()
            )
        except OSError:
            digest.update(f"{ref.file}:missing".encode())
    return digest.hexdigest()

class QwenImageReferencePack:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}, "optional": {
            "references_json": ("STRING", {"multiline": True, "dynamicPrompts": False, "default": "", "tooltip": "Reference list written by the image manager. Do not hand-edit."}),
            "max_reference_edge": ("INT", {"default": DEFAULT_MAX_REFERENCE_EDGE, "min": 0, "max": 8192, "step": 64, "tooltip": "Downscale references whose long edge exceeds this. 0 disables the cap."}),
        }}

    MAX_IMAGES = 10
    RETURN_TYPES = ("IMAGE",) * 10
    RETURN_NAMES = tuple(f"image_{i}" for i in range(1, 11))
    FUNCTION = "build"
    CATEGORY = "Qwen Image"

    @classmethod
    def IS_CHANGED(cls, references_json="", max_reference_edge=DEFAULT_MAX_REFERENCE_EDGE, **kwargs):
        import folder_paths
        reference_set = refs.ReferenceSet.from_json(references_json, max_images=cls.MAX_IMAGES)
        return _signature(reference_set, folder_paths.get_input_directory()) + f"|{max_reference_edge}"

    def build(self, references_json="", max_reference_edge=DEFAULT_MAX_REFERENCE_EDGE, **kwargs):
        import folder_paths
        input_dir = folder_paths.get_input_directory()
        reference_set = refs.ReferenceSet.from_json(references_json, max_images=self.MAX_IMAGES)
        missing = reference_set.missing_files(input_dir)
        if missing: raise ValueError("reference file(s) not found in the ComfyUI input directory: " + ", ".join(missing))
        outputs = [None] * self.MAX_IMAGES
        for index, reference in enumerate(reference_set.references):
            outputs[index] = media.load_image(str(refs.reference_path(input_dir, reference.file)), crop=reference.crop, max_edge=max_reference_edge, rotation=reference.rotation, mirror=reference.mirror)
        return tuple(outputs)

class QwenImageFirstLastReferencePack(QwenImageReferencePack):
    """Fork-specific first/last-frame upload manager."""

    MAX_IMAGES = 2
    RETURN_TYPES = ("IMAGE", "IMAGE", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("First image", "Last image", "first_width", "first_height", "last_width", "last_height")

    @classmethod
    def INPUT_TYPES(cls):
        # Keep references first for positional workflow serialization.
        inputs = super().INPUT_TYPES()
        inputs["optional"].pop("max_reference_edge")
        inputs["optional"].update({
            "megapixels": ("FLOAT", {"default": 1.05, "min": 0.0, "max": 16.0, "step": 0.01,
                "tooltip": "Target megapixels per image. 0 disables megapixel scaling."}),
            "multiple_of": ("INT", {"default": 16, "min": 1, "max": 128, "step": 1}),
            "resize_mode": (scaling.RESIZE_MODES, {"default": "crop"}),
            "upscale_method": (scaling.UPSCALE_METHODS, {"default": "lanczos"}),
            "width": ("INT", {"default": 0, "min": 0, "max": 16384,
                "tooltip": "Set both width and height above 0 to override megapixels for both images."}),
            "height": ("INT", {"default": 0, "min": 0, "max": 16384,
                "tooltip": "Set both width and height above 0 to override megapixels for both images."}),
        })
        return inputs

    @classmethod
    def IS_CHANGED(cls, references_json="", megapixels=1.05, multiple_of=16,
                   resize_mode="crop", upscale_method="lanczos", width=0, height=0, **kwargs):
        signature = super().IS_CHANGED(references_json, max_reference_edge=0)
        return signature + repr((megapixels, multiple_of, resize_mode, upscale_method, width, height))

    def build(self, references_json="", megapixels=1.05, multiple_of=16,
              resize_mode="crop", upscale_method="lanczos", width=0, height=0, **kwargs):
        images = super().build(references_json, max_reference_edge=0)
        outputs, dimensions = [], []
        for image in images:
            if image is None:
                outputs.append(None)
                dimensions.extend((0, 0))
            else:
                image, w, h = scaling.scale_image(image, megapixels, multiple_of,
                                                resize_mode, upscale_method, width, height)
                outputs.append(image)
                dimensions.extend((w, h))
        return tuple(outputs + dimensions)


class QwenImageLocalReferencePack(QwenImageFirstLastReferencePack):
    """Fork-specific first/last-frame manager using ComfyUI/input."""


class QwenImageLocalReferencePack10(QwenImageReferencePack):
    """Fork-specific ten-image manager using ComfyUI/input."""


# Preserve workflows saved with the first ten-image fork release.
QwenImageReferencePack10 = QwenImageReferencePack

NODE_CLASS_MAPPINGS = {
    "QwenImageReferencePack": QwenImageReferencePack,
    "QwenImageFirstLastReferencePack": QwenImageFirstLastReferencePack,
    "QwenImageLocalReferencePack": QwenImageLocalReferencePack,
    "QwenImageLocalReferencePack10": QwenImageLocalReferencePack10,
    "QwenImageReferencePack10": QwenImageReferencePack10,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageReferencePack": "Qwen Image References Manager",
    "QwenImageFirstLastReferencePack": "Qwen Image References Manager (First/Last)",
    "QwenImageLocalReferencePack": "Qwen Image References Manager (Local Input, First/Last)",
    "QwenImageLocalReferencePack10": "Qwen Image References Manager (Local Input, 10 Images)",
    "QwenImageReferencePack10": "Qwen Image References Manager (10 Images, Legacy Fork ID)",
}
