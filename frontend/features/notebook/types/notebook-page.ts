/** Mirrors backend/app/schemas/notebook_page.py exactly. `position` is a
 * plain non-negative integer on this backend (unlike Block.position, which
 * is a float) - see app/models/notebook_page.py. */

export type NotebookPage = {
  id: string;
  notebook_id: string;
  title: string;
  position: number;
  created_at: string;
  updated_at: string;
};

export type NotebookPageCreateInput = {
  title: string;
  position: number;
};

export type NotebookPageUpdateInput = {
  title?: string;
  position?: number;
};
