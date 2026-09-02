import { useEffect, useMemo, useRef } from "react";

type DebouncedFn<Args extends unknown[]> = {
  (...args: Args): void;
  flush: (...args: Args) => void;
  cancel: () => void;
};

/** Generic debounce for autosave - callers pass a stable delay (see
 * block-editor.tsx: 600ms) and get a stable function reference back that
 * always calls the latest `callback`, plus `.flush()` to save immediately
 * on blur and `.cancel()` for cleanup. */
export function useDebouncedCallback<Args extends unknown[]>(
  callback: (...args: Args) => void,
  delayMs: number,
): DebouncedFn<Args> {
  const callbackRef = useRef(callback);
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const debounced = useMemo<DebouncedFn<Args>>(() => {
    function fn(...args: Args) {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        timeoutRef.current = null;
        callbackRef.current(...args);
      }, delayMs);
    }
    fn.flush = (...args: Args) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      callbackRef.current(...args);
    };
    fn.cancel = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
    return fn;
  }, [delayMs]);

  useEffect(() => () => debounced.cancel(), [debounced]);

  return debounced;
}
