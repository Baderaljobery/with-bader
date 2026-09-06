/** Mirrors backend/app/schemas/user.py's UserResponse exactly - never
 * carries password/password_hash. */
export type AuthUser = {
  id: string;
  name: string;
  email: string;
  role: "owner" | "editor";
  created_at: string;
};
