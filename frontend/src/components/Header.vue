<template>
  <header class="w-full border-b border-border bg-background sticky top-0 z-40">
    <div class="container mx-auto flex items-center justify-between h-14 px-4">
      <RouterLink to="/" class="text-xl font-bold text-foreground">
        CapyTime
      </RouterLink>
      <RouterLink to="/onboarding">
        <button
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2"
          type="button"
        >
          Регистрация
        </button>
      </RouterLink>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterLink } from "vue-router";

export default defineComponent({
  name: "Header",
  components: {
    RouterLink,
  },
});
</script>

