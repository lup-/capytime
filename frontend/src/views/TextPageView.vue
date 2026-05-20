<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header>
      <template #right>
        <HeaderButtons />
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
import Header from "@/components/Header.vue";
import HeaderButtons from "@/components/HeaderButtons.vue";
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
    Header,
    HeaderButtons,
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
