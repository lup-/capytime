import { defineStore } from "pinia";
import type { Psychologist } from "@/lib/types";
import { getPsychologistSlug } from "@/lib/utils";
import { useErrorStore } from "./error";

const API_BASE = "/api/auth";

interface AuthState {
  isAuthenticated: boolean;
  psychologist: Psychologist | null;
  token: string | null;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    isAuthenticated: false,
    psychologist: null,
    token: localStorage.getItem("psychologist_token"),
  }),
  getters: {
    slug(): string {
      if (!this.psychologist) return "";
      return getPsychologistSlug(this.psychologist);
    },
  },
  actions: {
    async init() {
      if (this.token) {
        await this.verify();
      }
    },
    async verify() {
      if (!this.token) return false;
      try {
        const res = await fetch(`${API_BASE}/verify`, {
          method: "POST",
          headers: { Authorization: `Bearer ${this.token}` },
        });
        if (!res.ok) return false;
        const data = await res.json();
        this.psychologist = data;
        this.isAuthenticated = true;
        return true;
      } catch {
        useErrorStore().showError("Ошибка соединения");
        return false;
      }
    },
    async refresh() {
      if (!this.token) return false;
      try {
        const res = await fetch(`${API_BASE}/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: this.token }),
        });
        if (!res.ok) return false;
        const data = await res.json();
        this.token = data.access_token;
        localStorage.setItem("psychologist_token", data.access_token);
        return true;
      } catch {
        useErrorStore().showError("Ошибка соединения");
        return false;
      }
    },
    async login(email: string, password: string) {
      try {
        const res = await fetch(`${API_BASE}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          useErrorStore().showError("Неверный email или пароль");
          return false;
        }
        const data = await res.json();
        this.token = data.access_token;
        localStorage.setItem("psychologist_token", data.access_token);
        return await this.verify();
      } catch {
        useErrorStore().showError("Ошибка соединения");
        return false;
      }
    },
    logout() {
      this.isAuthenticated = false;
      this.psychologist = null;
      this.token = null;
      localStorage.removeItem("psychologist_token");
    },
    setToken(token: string) {
      this.token = token;
      localStorage.setItem("psychologist_token", token);
    },
  },
});
