import { useMutation, useQueryClient } from "@tanstack/react-query";

import { authApi, type LoginInput } from "../api/auth-api";
import { authKeys } from "./query-keys";

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: LoginInput) => authApi.login(input),
    onSuccess: (user) => {
      queryClient.setQueryData(authKeys.currentUser, user);
    },
  });
}
