<template>
  <div class="fixed top-20 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-2">
    <TransitionGroup name="toast">
      <div
        v-for="toast in errorStore.toasts"
        :key="toast.id"
        class="text-sm px-4 py-2 rounded-lg shadow-lg"
        :class="toast.type === 'success' ? 'text-green-600 bg-green-50 border border-green-200' : 'text-red-600 bg-red-50 border border-red-200'"
      >
        {{ toast.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useErrorStore } from "@/stores/error";

export default defineComponent({
  name: "ToastContainer",
  setup() {
    const errorStore = useErrorStore();
    return { errorStore };
  },
});
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>