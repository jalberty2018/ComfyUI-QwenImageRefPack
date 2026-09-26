from pathlib import Path

SOURCE = (Path(__file__).parents[1] / "web" / "qwen_image_refpack.js").read_text(encoding="utf-8")

def test_frontend_uses_fixed_image_canvas_and_two_slots():
    assert 'const KINDS = ["image"]' in SOURCE
    assert "const CAPS = { image: 2 }" in SOURCE
    assert "const GRID_COLUMNS = tenImages ? 5 : 2" in SOURCE
    assert "const GRID_ROWS = tenImages ? 2 : 1" in SOURCE
    assert "width: 420" in SOURCE
    assert "bottomPad: 14" in SOURCE
    assert 'document.createElement("canvas")' in SOURCE
    assert "drawAddSquare" in SOURCE
    assert "openEditModal" in SOURCE

def test_frontend_does_not_expose_prompt_video_or_audio_controls():
    custom_block = SOURCE.split("function buildCustomBlock(node)", 1)[1].split("// Config (reference pack)", 1)[0]
    registration = SOURCE.split("app.registerExtension({", 1)[1]
    assert '"video", "Video"' not in custom_block
    assert '"audio", "Audio"' not in custom_block
    assert "mmrp-uploads" not in custom_block
    assert "Save config" not in custom_block
    assert "Load config" not in custom_block
    assert "Local LLM" not in custom_block
    assert "Director" not in custom_block
    assert "directionInput" not in custom_block
    assert 'widgetByName(node, "prompt_provider")' not in registration
    assert "installDirectorRunHook" not in registration


def test_upstream_and_fork_frontend_registration():
    assert 'tenImages ? "QwenImageReferencePack" : "QwenImageFirstLastReferencePack"' in SOURCE
    assert 'tenImages ? "QwenImageLocalReferencePack10" : "QwenImageLocalReferencePack"' in SOURCE
    assert 'if (tenImages) supportedNames.push("QwenImageReferencePack10")' in SOURCE
    assert 'while (this.outputs?.length > names.length)' in SOURCE


def test_old_first_last_workflow_migrates_widgets_and_keeps_links():
    import json
    import shutil
    import subprocess
    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is needed for workflow migration test")
    body = SOURCE.split("node.onConfigure = function (info) {", 1)[1].split("\n            };", 1)[0]
    script = r'''const assert = require("node:assert/strict");
const tenImages = false;
const origOnConfigure = null;
const nodeData = {
  output_name: ["First image", "Last image", "first_width", "first_height", "last_width", "last_height"],
  output: ["IMAGE", "IMAGE", "INT", "INT", "INT", "INT"]
};
const widgetByName = (node, name) => node.widgets.find(w => w.name === name);
const setWidget = (node, name, value) => { widgetByName(node, name).value = value; };
const stopPreview = () => {};
const parseRefsValue = w => JSON.parse(w.value);
const fixedSize = () => [420, 600];
const renderNodeBody = () => {};
const target = {
  widgets: ["references_json", "megapixels", "multiple_of", "resize_mode", "upscale_method", "width", "height"].map(name => ({name, value: 2048})),
  outputs: [{name: "First image", type: "IMAGE", links: [101]}, {name: "Last image", type: "IMAGE", links: [102]}],
  addOutput(name, type) { this.outputs.push({name, type}); },
  removeOutput(index) { this.outputs.splice(index, 1); },
  setSize() {}
};
const configure = function(info) { BODY };
configure.call(target, {widgets_values: ['[{"file":"original.png"}]', 2048]});
assert.equal(widgetByName(target, "megapixels").value, 1.05);
assert.equal(widgetByName(target, "multiple_of").value, 16);
assert.deepEqual(target._mmrpRefs, [{file: "original.png"}]);
assert.deepEqual(target.outputs.map(o => o.type), nodeData.output);
assert.deepEqual(target.outputs.map(o => o.name), nodeData.output_name);
assert.deepEqual(target.outputs[0].links, [101]);
assert.deepEqual(target.outputs[1].links, [102]);
widgetByName(target, "megapixels").value = 2;
configure.call(target, {widgets_values: ['[{"file":"original.png"}]', 2, 32, "pad", "area", 640, 480]});
assert.equal(widgetByName(target, "megapixels").value, 2);
assert.equal(target.outputs.length, 6);
'''.replace("BODY", body)
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
