/* Photo and video gallery. Media is requested only when its viewer is opened. */
document.addEventListener("DOMContentLoaded", () => {
    "use strict";
    const cards = [...document.querySelectorAll("a.gallery-item")];
    const dialog = document.querySelector(".gallery-lightbox");
    if (!cards.length || !dialog || typeof dialog.showModal !== "function") return;

    const filters = document.querySelector(".gallery-filters");
    const results = document.querySelector(".gallery-results");
    const empty = document.querySelector(".gallery-filter-empty");
    const photo = dialog.querySelector("img");
    const video = dialog.querySelector("video");
    const caption = dialog.querySelector("figcaption");
    const status = dialog.querySelector(".gallery-media-status");
    const original = dialog.querySelector(".gallery-original");
    const steps = [...dialog.querySelectorAll("[data-lightbox-step]")];
    let visible = cards, index = 0, opener, swipeStart = null;

    const resetMedia = () => {
        video.pause();
        video.removeAttribute("src");
        video.removeAttribute("poster");
        video.load(); // Abort any previous download and release decoder resources.
        video.hidden = true;
        photo.hidden = true;
        photo.removeAttribute("src");
        status.textContent = "";
    };
    const show = step => {
        resetMedia();
        index = (index + step + visible.length) % visible.length;
        const card = visible[index];
        const title = card.dataset.title;
        const isVideo = card.dataset.mediaType === "video";
        caption.textContent = `${title} · ${index + 1} / ${visible.length}`;
        original.href = card.href;
        original.setAttribute("aria-label", `Open original ${isVideo ? "video" : "photo"}: ${title} (new tab)`);
        steps.forEach(button => button.disabled = visible.length < 2);
        if (isVideo) {
            video.hidden = false;
            video.poster = card.querySelector("img").src;
            video.setAttribute("aria-label", title);
            video.src = card.href;
            status.textContent = "Press play to watch. Sound may be included.";
        } else {
            photo.alt = title;
            photo.hidden = false;
            status.textContent = "Loading photo…";
            photo.src = card.href;
        }
    };
    photo.addEventListener("load", () => { if (!photo.hidden) status.textContent = ""; });
    photo.addEventListener("error", () => { if (!photo.hidden) status.textContent = "This photo could not load. Try opening the original."; });
    video.addEventListener("waiting", () => { if (!video.hidden) status.textContent = "Loading video…"; });
    video.addEventListener("playing", () => status.textContent = "");
    video.addEventListener("canplay", () => { if (!video.hidden) status.textContent = video.paused ? "Press play to watch." : ""; });
    video.addEventListener("error", () => { if (!video.hidden && video.getAttribute("src")) status.textContent = "This video could not play. Try opening the original."; });

    cards.forEach(card => card.addEventListener("click", event => {
        // Preserve new-tab/download modifier behavior and the no-JS link fallback.
        if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        opener = card;
        index = visible.indexOf(card);
        show(0);
        document.body.classList.add("gallery-modal-open");
        dialog.showModal();
    }));
    filters.hidden = false;
    results.hidden = false;
    const updateResults = () => results.textContent = `${visible.length} ${visible.length === 1 ? "moment" : "moments"}`;
    updateResults();
    filters.querySelectorAll("[data-gallery-filter]").forEach(button => button.addEventListener("click", () => {
        const type = button.dataset.galleryFilter;
        filters.querySelectorAll("button").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
        cards.forEach(card => card.hidden = type !== "all" && card.dataset.mediaType !== type);
        visible = cards.filter(card => !card.hidden);
        empty.hidden = visible.length !== 0;
        updateResults();
    }));
    dialog.querySelector("[data-lightbox-close]").addEventListener("click", () => dialog.close());
    steps.forEach(button => button.addEventListener("click", () => show(Number(button.dataset.lightboxStep))));
    dialog.addEventListener("keydown", event => {
        // Leave seek, volume and playback shortcuts to the native video controls.
        if (event.target === video) return;
        if (["ArrowLeft", "ArrowRight"].includes(event.key)) {
            event.preventDefault();
            show(event.key === "ArrowRight" ? 1 : -1);
        }
    });
    photo.addEventListener("touchstart", event => {
        swipeStart = event.touches.length === 1 ? {x: event.touches[0].clientX, y: event.touches[0].clientY} : null;
    }, {passive: true});
    photo.addEventListener("touchend", event => {
        if (!swipeStart || !event.changedTouches.length) return;
        const dx = event.changedTouches[0].clientX - swipeStart.x;
        const dy = event.changedTouches[0].clientY - swipeStart.y;
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) show(dx < 0 ? 1 : -1);
        swipeStart = null;
    }, {passive: true});
    photo.addEventListener("touchcancel", () => swipeStart = null, {passive: true});
    dialog.addEventListener("click", event => {
        const bounds = dialog.getBoundingClientRect();
        if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
    });
    dialog.addEventListener("close", () => {
        resetMedia();
        document.body.classList.remove("gallery-modal-open");
        opener?.focus();
    });
});
