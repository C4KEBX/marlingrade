import { useEffect, useState } from "react";

/** True only when the browser explicitly asks for reduced motion. Guards
 *  `matchMedia` existence so jsdom (which omits it) falls through to "animate". */
function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

/**
 * Animates 0 → `target` over `ms` via requestAnimationFrame, re-running whenever
 * `target` changes. Returns the current rounded value. When the user prefers
 * reduced motion, returns `target` immediately with no animation.
 */
export function useCountUp(target: number, ms = 600): number {
  const [value, setValue] = useState<number>(() =>
    prefersReducedMotion() ? target : 0,
  );

  useEffect(() => {
    if (prefersReducedMotion()) {
      setValue(target);
      return;
    }
    let raf = 0;
    const start = performance.now();
    const tick = (now: number): void => {
      const t = Math.min(1, (now - start) / ms);
      setValue(Math.round(target * t));
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, ms]);

  return value;
}
