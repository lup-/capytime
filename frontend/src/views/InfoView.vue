<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header>
      <template #right>
        <HeaderButtons />
      </template>
    </Header>

    <main class="flex-1 container mx-auto px-4 py-8 md:py-12">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-2xl md:text-3xl font-bold text-foreground mb-8">Информация</h1>

        <div v-if="loading" class="space-y-4 animate-pulse">
          <div class="h-4 bg-muted rounded w-48" />
          <div class="h-4 bg-muted rounded w-full" />
          <div class="h-4 bg-muted rounded w-5/6" />
          <div class="h-4 bg-muted rounded w-4/6" />
        </div>

        <div v-else class="space-y-10">
          <section v-for="group in groups" :key="group.key">
            <h2 class="text-xl font-semibold text-foreground mb-4">{{ group.title }}</h2>
            <ul class="space-y-2">
              <li v-for="page in group.pages" :key="page.path">
                <RouterLink
                  :to="'/' + page.path"
                  class="text-primary hover:underline"
                >
                  {{ page.title }}
                </RouterLink>
              </li>
            </ul>
          </section>
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

interface Page {
  path: string;
  title: string;
}

interface PageGroup {
  key: string;
  title: string;
  pages: Page[];
}

const GROUP_MAP: Record<string, string> = {
  capy: "Для специалистов",
  gorod: "По городам",
  sravni: "Сравнения",
  howto: "Инструкции",
};

export default defineComponent({
  name: "InfoView",
  components: {
    Header,
    HeaderButtons,
    Footer,
  },
  data() {
    return {
      loading: true,
      groups: [] as PageGroup[],
    };
  },
  async mounted() {
    try {
      const res = await fetch("/api/pages");
      if (!res.ok) throw new Error("Failed to load pages");
      const pages: Page[] = await res.json();
      this.groups = this.buildGroups(pages);
    } catch {
      this.groups = [];
    } finally {
      this.loading = false;
    }
  },
  methods: {
    buildGroups(pages: Page[]): PageGroup[] {
      const groupMap = new Map<string, Page[]>();
      const docs: Page[] = [];

      for (const page of pages) {
        const slashIdx = page.path.indexOf("/");
        if (slashIdx === -1) {
          docs.push(page);
        } else {
          const prefix = page.path.slice(0, slashIdx);
          if (GROUP_MAP[prefix]) {
            if (!groupMap.has(prefix)) groupMap.set(prefix, []);
            groupMap.get(prefix)!.push(page);
          }
        }
      }

      const groups: PageGroup[] = [];
      const order = ["capy", "gorod", "sravni", "howto"];
      for (const key of order) {
        const pages = groupMap.get(key);
        if (pages) {
          groups.push({ key, title: GROUP_MAP[key], pages });
        }
      }

      if (docs.length) {
        groups.push({ key: "docs", title: "Документы", pages: docs });
      }

      return groups;
    },
  },
});
</script>
