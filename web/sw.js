// Service worker: cache the model files after first download so later sessions load
// instantly and work offline. The user pays the ~80MB download exactly once.

const MODEL_CACHE = "voidwen-model-v1";
const CACHEABLE_HOSTS = ["huggingface.co", "cdn.jsdelivr.net"];

self.addEventListener("activate", (event) => {
  // Drop old cache versions on activation.
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== MODEL_CACHE).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (!CACHEABLE_HOSTS.some((h) => url.hostname.endsWith(h))) return;

  // Cache-first: model weights and libraries never change under a given URL.
  event.respondWith(
    caches.open(MODEL_CACHE).then((cache) =>
      cache.match(event.request).then(
        (hit) =>
          hit ||
          fetch(event.request).then((resp) => {
            if (resp.ok) cache.put(event.request, resp.clone());
            return resp;
          })
      )
    )
  );
});
