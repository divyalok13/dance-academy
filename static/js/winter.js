
/* =========================================================
   WSDC ACADEMY | WINTER EDITION
   Features:
   1. Animated SVG Santa and reindeer
   2. Falling snowflakes
   3. Infinite auto-moving offerings carousel
   4. Pause carousel on hover / focus
   5. Reduced-motion accessibility
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const hero = document.querySelector(".hero");

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    
/* =====================================================
   1. HYBRID AUTO + MANUAL OFFERINGS CAROUSEL
   ===================================================== */

const navToggle = document.querySelector(".nav-toggle");
    const navLinks = document.querySelector(".nav-links");
    if (navToggle && navLinks) {
        navToggle.hidden = false;
        document.documentElement.classList.add("navigation-ready");
        const close = () => navToggle.setAttribute("aria-expanded", "false");
        navToggle.addEventListener("click", () => navToggle.setAttribute("aria-expanded", String(navToggle.getAttribute("aria-expanded") !== "true")));
        navLinks.addEventListener("click", event => { if (event.target.closest("a")) close(); });
        document.addEventListener("keydown", event => { if (event.key === "Escape" && navToggle.getAttribute("aria-expanded") === "true") { close(); navToggle.focus(); } });
        document.addEventListener("click", event => { if (!event.target.closest(".navbar")) close(); });
    }

    const track = document.querySelector(".wsdc-offerings-track");
    if (track && track.children.length) {
        const originals = [...track.children];
        for (const side of ["before", "after"]) {
            const fragment = document.createDocumentFragment();
            originals.forEach(card => {
                const clone = card.cloneNode(true);
                clone.setAttribute("aria-hidden", "true");
                clone.querySelectorAll("[id]").forEach(node => node.removeAttribute("id"));
                clone.querySelectorAll("a, button, [tabindex]").forEach(node => node.tabIndex = -1);
                fragment.append(clone);
            });
            if (side === "before") track.prepend(fragment); else track.append(fragment);
        }
        let span = 0, position = 0, dragging = false, moved = false, previousX = 0;
        let paused = reduceMotion, hovered = false, touching = false, resumeAt = 0, last = performance.now();
        const measure = () => {
            span = originals[originals.length - 1].nextElementSibling.offsetLeft - originals[0].offsetLeft;
            position = span;
            track.scrollLeft = position;
        };
        const normalize = () => {
            if (!span) return;
            const next = ((track.scrollLeft - span) % span + span) % span + span;
            if (Math.abs(next - track.scrollLeft) > 1) track.scrollLeft = next;
            if (dragging || touching || hovered || paused || performance.now() < resumeAt || track.matches(":focus-within")) position = track.scrollLeft;
        };
        new ResizeObserver(measure).observe(track);
        measure();
        const pauseButton = document.querySelector(".offerings-pause");
        pauseButton.hidden = false;
        const label = () => { pauseButton.textContent = paused ? "Play offerings" : "Pause offerings"; };
        label();
        pauseButton.addEventListener("click", () => { paused = !paused; label(); });
        track.addEventListener("mouseenter", () => hovered = true);
        track.addEventListener("mouseleave", () => hovered = false);
        track.addEventListener("pointerdown", event => {
            if (event.pointerType === "touch") { touching = true; return; }
            if (event.button !== 0) return;
            dragging = true; moved = false; previousX = event.clientX;
        });
        window.addEventListener("pointermove", event => {
            if (!dragging) return;
            const delta = event.clientX - previousX;
            if (Math.abs(delta) > 2) moved = true;
            if (moved) { event.preventDefault(); track.classList.add("is-dragging"); track.scrollLeft -= delta; normalize(); }
            previousX = event.clientX;
        });
        const stop = () => { dragging = touching = false; track.classList.remove("is-dragging"); resumeAt = performance.now() + 1800; };
        window.addEventListener("pointerup", stop);
        window.addEventListener("pointercancel", stop);
        window.addEventListener("blur", stop);
        track.addEventListener("dragstart", event => event.preventDefault());
        track.addEventListener("click", event => { if (moved) { event.preventDefault(); moved = false; } });
        track.addEventListener("scroll", () => { normalize(); }, {passive: true});
        track.addEventListener("wheel", () => resumeAt = performance.now() + 1800, {passive: true});
        track.addEventListener("keydown", event => {
            if (["ArrowLeft", "ArrowRight"].includes(event.key)) {
                event.preventDefault(); track.scrollLeft += event.key === "ArrowRight" ? 290 : -290; normalize();
            }
        });
        const animate = now => {
            const delta = Math.min(now - last, 50); last = now;
            if (!paused && !hovered && !dragging && !touching && !document.hidden && !track.matches(":focus-within") && now > resumeAt) {
                position += delta * .028;
                track.scrollLeft = position;
                if (position >= span * 2) { position -= span; track.scrollLeft = position; }
            }
            requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }

    const testimonials = document.querySelector(".testimonials-grid");
    if (testimonials && testimonials.querySelector(".testimonial-card")) {
        const cards = [...testimonials.querySelectorAll(".testimonial-card")];
        let paused = reduceMotion;
        const next = direction => {
            const current = Math.round(testimonials.scrollLeft / (cards[0].getBoundingClientRect().width + 24));
            const atEnd = testimonials.scrollLeft >= testimonials.scrollWidth - testimonials.clientWidth - 2;
            const index = direction > 0 && atEnd ? 0 : (current + direction + cards.length) % cards.length;
            testimonials.scrollTo({left: cards[index].offsetLeft - cards[0].offsetLeft, behavior: reduceMotion ? "instant" : "smooth"});
        };
        document.querySelectorAll("[data-testimonial-step]").forEach(button => {
            button.hidden = cards.length < 2;
            button.addEventListener("click", () => next(Number(button.dataset.testimonialStep)));
        });
        const button = document.querySelector("[data-testimonial-pause]");
        button.hidden = cards.length < 2;
        const label = () => button.textContent = paused ? "Play testimonials" : "Pause testimonials";
        label(); button.addEventListener("click", () => { paused = !paused; label(); });
        setInterval(() => {
            if (!paused && !document.hidden && !testimonials.matches(":hover, :focus-within")) next(1);
        }, 6000);
    }

    const dialog = document.querySelector(".gallery-lightbox");
    const images = [...document.querySelectorAll("a.gallery-item")];
    if (dialog && images.length) {
        let index = 0, opener;
        const show = step => {
            index = (index + step + images.length) % images.length;
            const original = images[index].querySelector("img");
            dialog.querySelector("img").src = images[index].href;
            dialog.querySelector("img").alt = original.alt;
            dialog.querySelector("figcaption").textContent = `${original.alt} · ${index + 1} / ${images.length}`;
        };
        images.forEach((link, number) => link.addEventListener("click", event => {
            event.preventDefault(); opener = link; index = number; show(0); dialog.showModal();
        }));
        dialog.querySelector("[data-lightbox-close]").addEventListener("click", () => dialog.close());
        dialog.querySelectorAll("[data-lightbox-step]").forEach(button => button.addEventListener("click", () => show(Number(button.dataset.lightboxStep))));
        dialog.addEventListener("keydown", event => {
            if (["ArrowLeft", "ArrowRight"].includes(event.key)) { event.preventDefault(); show(event.key === "ArrowRight" ? 1 : -1); }
        });
        dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
        dialog.addEventListener("close", () => opener?.focus());
    }

    /* =====================================================
       2. CHRISTMAS EFFECTS: HOMEPAGE ONLY
       ===================================================== */

    if (!hero) return;

    document.body.classList.add("winter-home");

    /* =====================================================
       3. ANIMATED SANTA + REINDEER
       ===================================================== */

    const decoration = document.createElement("div");

    decoration.className = "winter-decoration";
    decoration.setAttribute("aria-hidden", "true");

    decoration.innerHTML = `
        <div class="winter-sleigh">
            <svg
                viewBox="0 0 560 160"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
                focusable="false"
            >
                <defs>
                    <linearGradient
                        id="winterGold"
                        x1="0" y1="0" x2="1" y2="1"
                    >
                        <stop offset="0%"
                              stop-color="#fff0bd"/>
                        <stop offset="55%"
                              stop-color="#d7aa54"/>
                        <stop offset="100%"
                              stop-color="#a97430"/>
                    </linearGradient>
                </defs>

                <!-- Reindeer -->
                <g
                    fill="url(#winterGold)"
                    stroke="#f6dfa5"
                    stroke-width="2"
                    stroke-linejoin="round"
                >
                    <g class="winter-deer winter-deer-one">
                        <path d="
                            M68 85
                            Q88 62 112 77
                            L143 83
                            L151 69
                            L162 66
                            L170 75
                            L165 91
                            L151 96
                            L142 91
                            L129 98
                            L117 125
                            L108 125
                            L113 98
                            L91 98
                            L82 124
                            L73 124
                            L76 96
                            L62 94 Z
                        "/>

                        <path
                            d="
                                M159 70
                                L153 47
                                L142 35
                                M153 47
                                L165 33
                                M153 47
                                L149 26
                            "
                            fill="none"
                            stroke-width="5"
                            stroke-linecap="round"
                        />
                    </g>

                    <g
                        class="winter-deer winter-deer-two"
                        transform="translate(155 -15) scale(.95)"
                    >
                        <path d="
                            M68 85
                            Q88 62 112 77
                            L143 83
                            L151 69
                            L162 66
                            L170 75
                            L165 91
                            L151 96
                            L142 91
                            L129 98
                            L117 125
                            L108 125
                            L113 98
                            L91 98
                            L82 124
                            L73 124
                            L76 96
                            L62 94 Z
                        "/>

                        <path
                            d="
                                M159 70
                                L153 47
                                L142 35
                                M153 47
                                L165 33
                                M153 47
                                L149 26
                            "
                            fill="none"
                            stroke-width="5"
                            stroke-linecap="round"
                        />
                    </g>
                </g>

                <!-- Reins -->
                <path
                    d="
                        M180 88
                        Q300 48 402 91
                        M332 75
                        Q370 65 402 91
                    "
                    fill="none"
                    stroke="#f2d69c"
                    stroke-width="2"
                    stroke-dasharray="5 4"
                />

                <!-- Santa's sleigh -->
                <g class="winter-sleigh-body">
                    <path
                        d="
                            M395 79
                            L471 79
                            Q494 88 480 116
                            L412 119
                            Q396 108 395 79 Z
                        "
                        fill="#a83c45"
                        stroke="#f0cc82"
                        stroke-width="4"
                    />

                    <!-- Runners -->
                    <path
                        d="
                            M406 117
                            Q448 139 492 116
                            M399 132
                            Q453 151 505 124
                        "
                        fill="none"
                        stroke="url(#winterGold)"
                        stroke-width="6"
                        stroke-linecap="round"
                    />

                    <!-- Santa -->
                    <circle
                        cx="436"
                        cy="64"
                        r="13"
                        fill="#f5d1ae"
                    />

                    <path
                        d="M420 56 L433 34 L449 56 Z"
                        fill="#b52f3c"
                        stroke="#f8e5d0"
                        stroke-width="3"
                    />

                    <circle
                        cx="434"
                        cy="32"
                        r="4"
                        fill="#fff8ed"
                    />

                    <path
                        d="
                            M420 79
                            Q436 70 455 82
                            L462 105
                            L415 104 Z
                        "
                        fill="#b52f3c"
                    />

                    <path
                        d="M429 72 Q437 89 447 72"
                        fill="#fff8ed"
                    />

                    <rect
                        x="413"
                        y="97"
                        width="49"
                        height="6"
                        rx="3"
                        fill="#e8c783"
                    />

                    <!-- Gift sack -->
                    <path
                        d="
                            M467 69
                            Q495 59 500 91
                            L478 100
                            Q467 89 467 69 Z
                        "
                        fill="#203c34"
                        stroke="#d7aa54"
                        stroke-width="3"
                    />
                </g>

                <!-- Decorative stars -->
                <g fill="#fff0bd">
                    <path
                        d="
                            M25 37
                            l4 9 9 4 -9 4 -4 9
                            -4 -9 -9 -4 9 -4 Z
                        "
                    />

                    <path
                        d="
                            M354 22
                            l3 7 7 3 -7 3 -3 7
                            -3 -7 -7 -3 7 -3 Z
                        "
                    />

                    <circle cx="367" cy="108" r="3"/>
                    <circle cx="208" cy="34" r="2"/>
                </g>
            </svg>
        </div>
    `;

    hero.appendChild(decoration);

    /* =====================================================
       4. RESPECT REDUCED MOTION
       ===================================================== */

    if (reduceMotion) return;

    /* =====================================================
       5. ANIMATED SNOWFALL
       ===================================================== */

    const snowLayer = document.createElement("div");

    snowLayer.className = "winter-snow";
    snowLayer.setAttribute("aria-hidden", "true");

    const isMobile = window.innerWidth < 700;

    const snowCount = isMobile ? 20 : 45;

    const fragment = document.createDocumentFragment();

    for (let i = 0; i < snowCount; i++) {
        const flake = document.createElement("span");

        flake.className = "winter-snowflake";

        const size = 2 + Math.random() * 4;
        const duration = 8 + Math.random() * 9;
        const delay = -Math.random() * 17;
        const opacity = 0.25 + Math.random() * 0.6;

        flake.style.left = `${Math.random() * 100}%`;
        flake.style.width = `${size}px`;
        flake.style.height = `${size}px`;
        flake.style.opacity = opacity;
        flake.style.animationDuration = `${duration}s`;
        flake.style.animationDelay = `${delay}s`;

        fragment.appendChild(flake);
    }

    snowLayer.appendChild(fragment);
    document.body.appendChild(snowLayer);
});
