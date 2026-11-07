
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

const offeringsTrack = document.querySelector(
    ".wsdc-offerings-track"
);

if (offeringsTrack) {
    const originalCards = Array.from(
        offeringsTrack.querySelectorAll(
            ".wsdc-offering-card"
        )
    );

    if (originalCards.length > 0) {
        const canAnimate = !reduceMotion;

        // Create three sets for seamless looping.
        if (canAnimate && !offeringsTrack.dataset.loopReady) {
            const originals = [...originalCards];

            // Add one set before and one after.
            const prependFragment = document.createDocumentFragment();
            const appendFragment = document.createDocumentFragment();

            const cloneCard = (card) => {
                const clone = card.cloneNode(true);
                clone.setAttribute("aria-hidden", "true");
                clone.setAttribute("inert", "");
                clone.removeAttribute("id");

                clone.querySelectorAll("[id]").forEach(
                    (element) => element.removeAttribute("id")
                );

                return clone;
            };

            originals.forEach((card) => {
                prependFragment.appendChild(cloneCard(card));
                appendFragment.appendChild(cloneCard(card));
            });

            offeringsTrack.prepend(prependFragment);
            offeringsTrack.append(appendFragment);

            offeringsTrack.dataset.loopReady = "true";
        }

        if (canAnimate) {
            const totalWidth = offeringsTrack.scrollWidth / 3;

            // Start in the middle set.
            offeringsTrack.scrollLeft = totalWidth;

            let isDragging = false;
            let startX = 0;
            let startScrollLeft = 0;
            let pausedUntil = 0;
            let lastFrame = performance.now();

            const speed = 28; // pixels per second

            function normalizeScroll() {
                if (offeringsTrack.scrollLeft >= totalWidth * 2) {
                    offeringsTrack.scrollLeft -= totalWidth;
                } else if (offeringsTrack.scrollLeft < totalWidth) {
                    offeringsTrack.scrollLeft += totalWidth;
                }
            }

            function animate(now) {
                const delta = Math.min(
                    (now - lastFrame) / 1000,
                    0.05
                );

                lastFrame = now;

                const paused =
                    isDragging ||
                    offeringsTrack.matches(":hover") ||
                    offeringsTrack.matches(":focus-within") ||
                    now < pausedUntil ||
                    document.hidden;

                if (!paused) {
                    offeringsTrack.scrollLeft += speed * delta;
                    normalizeScroll();
                }

                requestAnimationFrame(animate);
            }

            offeringsTrack.addEventListener(
                "pointerdown",
                (event) => {
                    if (event.pointerType === "touch") return;

                    isDragging = true;
                    startX = event.clientX;
                    startScrollLeft = offeringsTrack.scrollLeft;

                    offeringsTrack.classList.add("is-dragging");
                    offeringsTrack.setPointerCapture(event.pointerId);
                }
            );

            offeringsTrack.addEventListener(
                "pointermove",
                (event) => {
                    if (!isDragging) return;

                    const distance = event.clientX - startX;

                    offeringsTrack.scrollLeft =
                        startScrollLeft - distance;

                    normalizeScroll();
                }
            );

            const stopDragging = () => {
                isDragging = false;
                offeringsTrack.classList.remove("is-dragging");
                pausedUntil = performance.now() + 1800;
            };

            offeringsTrack.addEventListener(
                "pointerup",
                stopDragging
            );

            offeringsTrack.addEventListener(
                "pointercancel",
                stopDragging
            );

            offeringsTrack.addEventListener(
                "scroll",
                () => {
                    if (!isDragging) {
                        normalizeScroll();
                    }
                },
                { passive: true }
            );

            requestAnimationFrame(animate);
        }
    }
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
