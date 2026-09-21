import pytest

from qwen_refpack.refs import MAX_IMAGES, ReferenceError, ReferenceSet, output_names


def test_contract_has_ten_image_outputs_only():
    assert MAX_IMAGES == 10
    assert output_names() == tuple(f"image_{i}" for i in range(1, 11))


def test_rejects_video_and_audio_references():
    with pytest.raises(ReferenceError, match="must be images"):
        ReferenceSet.from_obj({"references": [{"kind": "video", "file": "clip.mp4"}]})


def test_rejects_more_than_ten_images():
    with pytest.raises(ReferenceError, match="at most 10"):
        ReferenceSet.from_obj({"references": [{"kind": "image", "file": f"{i}.png"} for i in range(11)]})

