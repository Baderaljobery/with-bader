import { apiClient } from "@/lib/api/client";
import type { AuthUser } from "../types/user";

export type RegisterInput = {
  name: string;
  email: string;
  password: string;
};

export type LoginInput = {
  email: string;
  password: string;
};

/** Every call here relies on the browser sending/receiving the HttpOnly
 * session cookie automatically (see lib/api/client.ts's credentials:
 * "include") - none of these ever touch localStorage/sessionStorage or any
 * frontend-visible token. */
export const authApi = {
  register: (input: RegisterInput): Promise<AuthUser> =>
    apiClient.post<AuthUser>("/api/auth/register", input),

  login: (input: LoginInput): Promise<AuthUser> =>
    apiClient.post<AuthUser>("/api/auth/login", input),

  getCurrentUser: (): Promise<AuthUser> => apiClient.get<AuthUser>("/api/auth/me"),

  logout: (): Promise<void> => apiClient.post<void>("/api/auth/logout"),

  deleteAccount: (): Promise<void> => apiClient.delete<void>("/api/auth/account"),
};
