import { useMutation, useQueryClient } from "@tanstack/react-query";

import { authApi, type RegisterInput } from "../api/auth-api";
import { authKeys } from "./query-keys";

/** Registering auto-authenticates (the backend sets the session cookie on
 * 201) - there is no separate "now go log in" step. */
export function useRegister() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: RegisterInput) => authApi.register(input),
    onSuccess: (user) => {
      queryClient.setQueryData(authKeys.currentUser, user);
    },
  });
}
