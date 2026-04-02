import { defineStore } from "pinia";

export interface ToastMessage {
  id: string;
  type: "success" | "error";
  message: string;
}

interface ErrorState {
  toasts: ToastMessage[];
}

export const useErrorStore = defineStore("error", {
  state: (): ErrorState => ({
    toasts: [],
  }),
  actions: {
    showSuccess(message: string) {
      const id = Date.now().toString();
      this.toasts.push({ id, type: "success", message });
      setTimeout(() => this.removeToast(id), 3000);
    },
    showError(message: string) {
      const id = Date.now().toString();
      this.toasts.push({ id, type: "error", message });
      setTimeout(() => this.removeToast(id), 5000);
    },
    removeToast(id: string) {
      this.toasts = this.toasts.filter((t) => t.id !== id);
    },
  },
});