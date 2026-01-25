"use client"

import { useAuth } from "@clerk/nextjs"

export function useAuthToken() {
  const { getToken } = useAuth();
  return { getToken };
}
