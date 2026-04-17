<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header>
      <template #right>
        <RouterLink to="/onboarding">
          <button
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2"
            type="button"
          >
            Регистрация
          </button>
        </RouterLink>
      </template>
    </Header>

    <main class="flex-1 container mx-auto px-4 py-8 md:py-12">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-2xl md:text-3xl font-bold text-foreground mb-6">{{ title }}</h1>
        <div class="prose prose-sm prose-slate dark:prose-invert max-w-none whitespace-pre-wrap text-foreground">
          {{ content }}
        </div>
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

import privacyPolicyText from "@/assets/texts/privacy-policy.txt?raw";
import personalDataProcessingText from "@/assets/texts/personal-data-processing.txt?raw";
import termsOfServiceText from "@/assets/texts/terms-of-service.txt?raw";

const textContents: Record<string, string> = {
  "privacy-policy": privacyPolicyText,
  "personal-data-processing": personalDataProcessingText,
  "terms-of-service": termsOfServiceText,
};

export default defineComponent({
  name: "TextPageView",
  components: {
    RouterLink,
    Header,
    Footer,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    pageKey: {
      type: String,
      required: true,
    },
  },
  watch: {
    pageKey() {
      window.scrollTo(0, 0);
    },
  },
  mounted() {
    window.scrollTo(0, 0);
  },
  computed: {
    content(): string {
      return textContents[this.pageKey] || "";
    },
  },
});
</script>
