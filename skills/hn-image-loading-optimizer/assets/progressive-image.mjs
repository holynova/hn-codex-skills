/** Reference implementation adapted from rubber-stamp; not its original code.
 * Only commits successfully loaded/decoded images for the current request.
 * invalidate() ignores old results; it does not abort their network requests.
 */
export function createProgressiveImageController(view, { makeImage = () => new Image() } = {}) {
  let revision = 0;

  async function loadDecoded(url) {
    const image = makeImage();
    await new Promise((resolve, reject) => {
      const cleanup = () => { image.onload = null; image.onerror = null; };
      image.onload = () => { cleanup(); resolve(); };
      image.onerror = () => { cleanup(); reject(new Error(`Image load failed: ${url}`)); };
      image.src = url;
      if (image.complete && image.naturalWidth > 0) { cleanup(); resolve(); }
    });
    if (typeof image.decode === "function") await image.decode();
    if (!(image.naturalWidth > 0)) throw new Error(`Image has no pixels: ${url}`);
    return image;
  }

  return {
    invalidate() { revision += 1; },
    async show({ thumbnail, detail, original, alt = "", allowOriginalFallback = false }) {
      if (!thumbnail) throw new Error("A thumbnail URL is required");
      const request = ++revision;
      view.alt = alt;
      view.src = thumbnail;
      const candidates = [...new Set([
        detail,
        allowOriginalFallback ? original : null,
      ].filter((url) => url && url !== thumbnail))];
      let lastError = null;
      for (const url of candidates) {
        if (request !== revision) return { status: "stale" };
        try {
          const image = await loadDecoded(url);
          if (request !== revision) return { status: "stale" };
          view.src = image.src;
          return { status: "upgraded", url: image.src };
        } catch (error) {
          if (request !== revision) return { status: "stale" };
          lastError = error;
        }
      }
      return { status: "preview", error: lastError };
    },
  };
}
