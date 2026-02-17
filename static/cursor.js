/* ============================================================
   EatSure — Custom Cursor (Fixed)
   Place in: static/cursor.js
   ============================================================ */

(function () {
    'use strict';

    if ('ontouchstart' in window) return;

    const glow = document.createElement('div');
    glow.className = 'cursor-glow';

    const ring = document.createElement('div');
    ring.className = 'cursor-ring';

    const dot = document.createElement('div');
    dot.className = 'cursor-dot';

    document.body.appendChild(glow);
    document.body.appendChild(ring);
    document.body.appendChild(dot);

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let ringX = mouseX, ringY = mouseY;
    let glowX = mouseX, glowY = mouseY;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    const SELECTORS = 'a, button, input, textarea, select, label, [role="button"], .upload-zone, .feature-card, .btn';

    document.addEventListener('mouseover', (e) => {
        if (e.target.closest(SELECTORS)) document.body.classList.add('cursor-hover');
    });
    document.addEventListener('mouseout', (e) => {
        if (e.target.closest(SELECTORS)) document.body.classList.remove('cursor-hover');
    });

    document.addEventListener('mousedown', () => {
        dot.style.transform = 'scale(0.6)';
        ring.style.transform = 'scale(0.75)';
    });
    document.addEventListener('mouseup', () => {
        dot.style.transform = 'scale(1)';
        ring.style.transform = 'scale(1)';
    });

    function lerp(a, b, t) { return a + (b - a) * t; }

    function tick() {
        // Dot follows instantly
        dot.style.left = mouseX + 'px';
        dot.style.top  = mouseY + 'px';

        // Ring lags slightly
        ringX = lerp(ringX, mouseX, 0.15);
        ringY = lerp(ringY, mouseY, 0.15);
        ring.style.left = ringX + 'px';
        ring.style.top  = ringY + 'px';

        // Glow lags the most — dreamy effect
        glowX = lerp(glowX, mouseX, 0.08);
        glowY = lerp(glowY, mouseY, 0.08);
        glow.style.left = glowX + 'px';
        glow.style.top  = glowY + 'px';

        requestAnimationFrame(tick);
    }

    tick();
})();