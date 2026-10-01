import assert from "node:assert/strict";
import test from "node:test";
import { createProgressiveImageController } from "../skills/hn-image-loading-optimizer/assets/progressive-image.mjs";

function setup({ withDecode = true, cached = false } = {}) {
  const view = { src: "", alt: "" };
  const images = [];
  const controller = createProgressiveImageController(view, { makeImage() {
    let resolveDecode;
    let rejectDecode;
    const decoded = new Promise((resolve, reject) => { resolveDecode = resolve; rejectDecode = reject; });
    const image = {
      complete: cached,
      naturalWidth: cached ? 400 : 0,
      src: "",
      load() { this.complete = true; this.naturalWidth = 400; this.onload?.(); },
      fail() { this.onerror?.(); },
      resolveDecode,
      rejectDecode,
    };
    if (withDecode) image.decode = () => decoded;
    images.push(image);
    return image;
  } });
  return { view, images, controller };
}

const item = (id) => ({ thumbnail: `${id}-thumb.webp`, detail: `${id}-detail.webp`, alt: id });
const tick = () => new Promise((resolve) => setImmediate(resolve));

test("keeps thumbnail visible until high-resolution decoding completes", async () => {
  const { view, images, controller } = setup();
  const result = controller.show(item("A"));
  assert.equal(view.src, "A-thumb.webp");
  images[0].load();
  await tick();
  assert.equal(view.src, "A-thumb.webp");
  images[0].resolveDecode();
  assert.equal((await result).status, "upgraded");
  assert.equal(view.src, "A-detail.webp");
});

test("late A response cannot replace the current B image", async () => {
  const { view, images, controller } = setup();
  const a = controller.show(item("A"));
  const b = controller.show(item("B"));
  images[1].load(); images[1].resolveDecode();
  await b;
  images[0].load(); images[0].resolveDecode();
  assert.equal((await a).status, "stale");
  assert.equal(view.src, "B-detail.webp");
});

test("closing a view invalidates pending high-resolution results", async () => {
  const { view, images, controller } = setup();
  const result = controller.show(item("A"));
  controller.invalidate();
  images[0].load(); images[0].resolveDecode();
  assert.equal((await result).status, "stale");
  assert.equal(view.src, "A-thumb.webp");
});

test("decode failure preserves preview and does not automatically request original", async () => {
  const { view, images, controller } = setup();
  const result = controller.show({ ...item("A"), original: "A.png" });
  images[0].load();
  await tick();
  images[0].rejectDecode(new Error("corrupt image"));
  assert.equal((await result).status, "preview");
  assert.equal(view.src, "A-thumb.webp");
  assert.equal(images.length, 1);
});

test("opt-in original fallback is bounded and all failures retain the thumbnail", async () => {
  const { view, images, controller } = setup();
  const result = controller.show({ ...item("A"), original: "A.png", allowOriginalFallback: true });
  images[0].fail();
  await tick();
  assert.equal(images[1].src, "A.png");
  images[1].fail();
  assert.equal((await result).status, "preview");
  assert.equal(images.length, 2);
  assert.equal(view.src, "A-thumb.webp");
});

test("already-loaded images work without the decode API", async () => {
  const { view, controller } = setup({ withDecode: false, cached: true });
  assert.equal((await controller.show(item("A"))).status, "upgraded");
  assert.equal(view.src, "A-detail.webp");
});
