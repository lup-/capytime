<template>
  <header class="w-full border-b border-border bg-background sticky top-0 z-40">
    <ToastContainer />
    <div class="container mx-auto flex items-center justify-between h-16 px-4">
      <div class="flex items-center gap-4">
        <slot name="left" />
        <RouterLink to="/" class="flex items-center">
          <img src="@/assets/logo.png" alt="CapyTime" class="h-12 hover:animate-spin cursor-pointer" />
        </RouterLink>
      </div>
      <div class="flex items-center gap-2">
        <slot name="right" />
        <UserMenu />
      </div>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterLink } from "vue-router";
import UserMenu from "@/components/UserMenu.vue";
import ToastContainer from "@/components/ToastContainer.vue";

export default defineComponent({
  name: "Header",
  components: {
    RouterLink,
    UserMenu,
    ToastContainer,
  },
});
</script>

