import { DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { BLOCK_TYPE_REGISTRY } from "../lib/block-types";
import type { BlockType } from "../types/block";

type BlockTypeMenuProps = {
  onSelect: (type: BlockType) => void;
  disabledType?: BlockType;
};

/** Shared list of insertable block types - used both for "+" insertion and
 * for the "change type" submenu (see block-toolbar.tsx). Only types with a
 * real, backend-persisted editing experience are listed here - see
 * lib/block-types.ts / types/block.ts for the deferred "image"/"table". */
export function BlockTypeMenu({ onSelect, disabledType }: BlockTypeMenuProps) {
  return (
    <>
      {BLOCK_TYPE_REGISTRY.map((meta) => (
        <DropdownMenuItem
          key={meta.type}
          onClick={() => onSelect(meta.type)}
          disabled={meta.type === disabledType}
        >
          <meta.icon className="size-3.5" aria-hidden="true" />
          {meta.label}
        </DropdownMenuItem>
      ))}
    </>
  );
}
