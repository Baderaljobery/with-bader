import { useState } from "react";

import { useDebouncedCallback } from "./use-debounced-callback";

/**
 * Local-first editable value with debounced autosave. Each block component
 * is keyed by block.id (see block-editor.tsx), so a *different* block never
 * reuses this hook's state - the only thing this hook has to protect
 * against is the SAME block's server value changing underneath an in-
 * progress edit (e.g. a background refetch on window refocus). While a
 * local edit is pending (typed but not yet saved), incoming server values
 * are tracked but never applied to the visible value - this is what keeps
 * a keystroke from disappearing mid-type (see notebook task PART 27).
 *
 * State only (no refs) so the "adjust state during render" comparison
 * below is safe under this project's stricter react-hooks/refs rule, which
 * forbids reading/writing ref.current during render.
 */
export function useLocalDraft<T>(serverValue: T, onSave: (value: T) => void, delayMs = 600) {
  const [value, setValue] = useState(serverValue);
  const [lastServerValue, setLastServerValue] = useState(serverValue);
  const [hasPendingEdit, setHasPendingEdit] = useState(false);

  if (serverValue !== lastServerValue) {
    setLastServerValue(serverValue);
    if (!hasPendingEdit) {
      setValue(serverValue);
    }
  }

  const debouncedSave = useDebouncedCallback((next: T) => {
    setHasPendingEdit(false);
    setLastServerValue(next);
    onSave(next);
  }, delayMs);

  function handleChange(next: T) {
    setValue(next);
    setHasPendingEdit(true);
    debouncedSave(next);
  }

  function flush() {
    debouncedSave.flush(value);
  }

  return { value, handleChange, flush };
}
