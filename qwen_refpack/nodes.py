"""Qwen Image reference manager: image inputs only, no prompt generation."""
from __future__ import annotations
import hashlib
import os
from . import media, refs

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

    RETURN_TYPES = refs.output_types()
    RETURN_NAMES = refs.output_names()
    FUNCTION = "build"
    CATEGORY = "Qwen Image"

    @classmethod
    def IS_CHANGED(cls, references_json="", max_reference_edge=DEFAULT_MAX_REFERENCE_EDGE, **kwargs):
        import folder_paths
        reference_set = refs.ReferenceSet.from_json(references_json)
        return _signature(reference_set, folder_paths.get_input_directory()) + f"|{max_reference_edge}"

    def build(self, references_json="", max_reference_edge=DEFAULT_MAX_REFERENCE_EDGE, **kwargs):
        import folder_paths
        input_dir = folder_paths.get_input_directory()
        reference_set = refs.ReferenceSet.from_json(references_json)
        missing = reference_set.missing_files(input_dir)
        if missing: raise ValueError("reference file(s) not found in the ComfyUI input directory: " + ", ".join(missing))
        outputs = refs.empty_outputs()
        for index, reference in enumerate(reference_set.references):
            outputs[index] = media.load_image(str(refs.reference_path(input_dir, reference.file)), crop=reference.crop, max_edge=max_reference_edge, rotation=reference.rotation, mirror=reference.mirror)
        return tuple(outputs)

NODE_CLASS_MAPPINGS = {"QwenImageReferencePack": QwenImageReferencePack}
NODE_DISPLAY_NAME_MAPPINGS = {"QwenImageReferencePack": "Qwen Image References Manager"}
