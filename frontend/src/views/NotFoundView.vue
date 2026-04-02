<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header />

    <main class="flex-1 flex flex-col items-center justify-center">
      <div class="text-center">
        <h1 class="mb-4 text-4xl font-bold">404</h1>
        <p class="mb-4 text-xl text-muted-foreground">{{ message }}</p>
        <RouterLink to="/" class="text-primary underline hover:text-primary/90">
          На главную
        </RouterLink>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterLink } from "vue-router";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
  name: "NotFoundView",
  components: {
    Header,
    Footer,
    RouterLink,
  },
  props: {
    message: {
      type: String,
      default: "Ой! Потерялось...",
    },
  },
});
</script>

