/**
 * Let's Design System (LDS v2.3.0)
 * Interaction Primitives: Tactile Carousel, Momentum Drag-to-Scroll & Touch Swipe
 */
(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /**
   * Universal Touch Swipe & Mouse Drag-to-Scroll Controller
   * Supports mouse pointer dragging with click suppression and touch momentum.
   */
  function enableTactileCarousel(root) {
    if (!root || root.dataset.ldsCarouselReady === '1') return;
    root.dataset.ldsCarouselReady = '1';

    let isDown = false;
    let startX = 0;
    let startScrollLeft = 0;
    let hasDragged = false;
    let lastX = 0;
    let lastTime = 0;
    let velocity = 0;
    let momentumFrame = null;

    root.style.overflowX = 'auto';
    root.style.webkitOverflowScrolling = 'touch';
    root.style.scrollbarWidth = 'none';
    root.style.touchAction = 'pan-x pan-y';
    root.classList.add('lds-tactile-carousel');

    // Pointer Down (Mouse & Touch)
    root.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      if (momentumFrame) {
        cancelAnimationFrame(momentumFrame);
        momentumFrame = null;
      }

      isDown = true;
      hasDragged = false;
      startX = e.clientX;
      lastX = e.clientX;
      startScrollLeft = root.scrollLeft;
      lastTime = performance.now();
      velocity = 0;

      root.classList.add('is-dragging');
      if (typeof root.setPointerCapture === 'function') {
        try { root.setPointerCapture(e.pointerId); } catch (_) {}
      }
    });

    // Pointer Move
    root.addEventListener('pointermove', (e) => {
      if (!isDown) return;
      const currentX = e.clientX;
      const dx = currentX - startX;
      
      if (Math.abs(dx) > 4) {
        hasDragged = true;
      }

      root.scrollLeft = startScrollLeft - dx;

      const now = performance.now();
      const dt = Math.max(1, now - lastTime);
      velocity = (currentX - lastX) / dt;
      lastX = currentX;
      lastTime = now;
    });

    // Pointer Up & Cancel with Momentum Glide
    const handlePointerEnd = (e) => {
      if (!isDown) return;
      isDown = false;
      root.classList.remove('is-dragging');

      if (typeof root.releasePointerCapture === 'function') {
        try { root.releasePointerCapture(e.pointerId); } catch (_) {}
      }

      // Apply light momentum glide on mouse release if velocity was significant
      if (!reduceMotion && Math.abs(velocity) > 0.25) {
        let currentVelocity = velocity * 14;
        const friction = 0.92;

        const stepMomentum = () => {
          if (Math.abs(currentVelocity) < 0.5 || isDown) {
            momentumFrame = null;
            return;
          }
          root.scrollLeft -= currentVelocity;
          currentVelocity *= friction;
          momentumFrame = requestAnimationFrame(stepMomentum);
        };
        momentumFrame = requestAnimationFrame(stepMomentum);
      }
    };

    root.addEventListener('pointerup', handlePointerEnd);
    root.addEventListener('pointercancel', handlePointerEnd);

    // Suppress click events if the user was dragging
    root.addEventListener('click', (e) => {
      if (hasDragged) {
        e.preventDefault();
        e.stopPropagation();
        hasDragged = false;
      }
    }, true);
  }

  function init() {
    // Select all carousels, nav tracks, and segment tracks
    const selectors = [
      '[data-lds-carousel]',
      '.service-nav-bar',
      '.cat-carousel',
      '.segment-tabs',
      '#serviceNavBar',
      '#catBar'
    ];
    document.querySelectorAll(selectors.join(', ')).forEach(enableTactileCarousel);
    document.documentElement.classList.toggle('lds-reduced-motion', reduceMotion);
  }

  window.LDS = Object.assign(window.LDS || {}, {
    version: '2.3.0',
    init,
    carousel: enableTactileCarousel
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
