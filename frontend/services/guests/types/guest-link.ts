/** Mirrors backend/app/schemas/guest_link.py. */
export type GuestLink = {
  id: string;
  guest_id: string;
  label: string;
  url: string;
  created_at: string;
};

export type GuestLinkCreateInput = {
  label: string;
  url: string;
};

export type GuestLinkUpdateInput = Partial<GuestLinkCreateInput>;
