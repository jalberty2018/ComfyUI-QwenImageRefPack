import json
import sys
from types import SimpleNamespace

import pytest

from qwen_refpack import nodes
from qwen_refpack.refs import ReferenceError


@pytest.mark.parametrize("node_class", [nodes.QwenImageReferencePack10, nodes.QwenImageLocalReferencePack10])
def test_ten_image_order_and_empty_slots(node_class, tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "folder_paths", SimpleNamespace(get_input_directory=lambda: str(tmp_path)))
    nested = tmp_path / "nested"
    nested.mkdir()
    for i in range(10):
        (nested / f"{i}.png").touch()
    monkeypatch.setattr(nodes.media, "load_image", lambda path, **kwargs: path)
    refs = [{"file": f"nested/{i}.png"} for i in range(10)]
    node = node_class()
    assert node.RETURN_TYPES == ("IMAGE",) * 10
    assert node.RETURN_NAMES == tuple(f"image_{i}" for i in range(1, 11))
    result = node.build(json.dumps(refs))
    assert result == tuple(str(nested / f"{i}.png") for i in range(10))
    assert node.build(json.dumps(refs[:1]))[1:] == (None,) * 9
    assert node.build() == (None,) * 10
    assert node.IS_CHANGED(json.dumps(refs)) != node.IS_CHANGED(json.dumps(refs[:9]))
    with pytest.raises(ReferenceError, match="at most 10"):
        node.build(json.dumps(refs + refs[:1]))
    with pytest.raises(ReferenceError, match="at most 2"):
        nodes.QwenImageReferencePack().build(json.dumps(refs))
