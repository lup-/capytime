<template>
  <div class="flex min-h-screen items-center justify-center bg-muted">
    <div class="text-center">
      <h1 class="mb-4 text-4xl font-bold">404</h1>
      <p class="mb-4 text-xl text-muted-foreground">Oops! Page not found</p>
      <RouterLink to="/" class="text-primary underline hover:text-primary/90">
        Return to Home
      </RouterLink>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterLink } from "vue-router";

export default defineComponent({
  name: "NotFoundView",
  components: {
    RouterLink,
  },
});
</script>

