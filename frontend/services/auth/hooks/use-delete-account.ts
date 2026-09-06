import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { authApi } from "../api/auth-api";

/** Deletes the current user's account and everything they own on the
 * backend, then clears the whole query cache and redirects to /login -
 * same cache/redirect discipline as useLogout, since the session is gone
 * either way. */
export function useDeleteAccount() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: () => authApi.deleteAccount(),
    onSuccess: () => {
      queryClient.clear();
      router.push("/login");
    },
  });
}
