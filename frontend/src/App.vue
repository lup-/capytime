<template>
  <router-view />
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useAuthStore } from "@/stores/auth";

export default defineComponent({
  name: "App",
  async created() {
    const authStore = useAuthStore();
    await authStore.init();
  },
});
</script>

