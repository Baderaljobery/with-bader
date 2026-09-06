/** Mirrors backend/app/schemas/notebook.py exactly. */

export type Notebook = {
  id: string;
  guest_id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type NotebookCreateInput = {
  title: string;
};

export type NotebookUpdateInput = {
  title?: string;
};
