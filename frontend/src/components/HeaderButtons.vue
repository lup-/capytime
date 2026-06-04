<template>
  <RouterLink to="/onboarding">
    <button
      type="button"
      class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2"
    >
      {{ authStore.isAuthenticated ? 'Настройки' : 'Регистрация' }}
    </button>
  </RouterLink>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";

export default defineComponent({
  name: "HeaderButtons",
  components: {
    RouterLink,
  },
  computed: {
    authStore() {
      return useAuthStore();
    },
  },
});
</script>
