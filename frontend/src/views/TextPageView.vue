<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header>
      <template #right>
        <HeaderButtons />
      </template>
    </Header>

    <main class="flex-1 container mx-auto px-4 py-8 md:py-12">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-2xl md:text-3xl font-bold text-foreground mb-6">{{ pageTitle }}</h1>
        <div
          v-if="loading"
          class="space-y-4 animate-pulse"
        >
          <div class="h-4 bg-muted rounded w-full" />
          <div class="h-4 bg-muted rounded w-5/6" />
          <div class="h-4 bg-muted rounded w-4/6" />
          <div class="h-4 bg-muted rounded w-full" />
          <div class="h-4 bg-muted rounded w-3/6" />
        </div>
        <div
          v-else
          class="prose prose-sm prose-slate dark:prose-invert max-w-none whitespace-pre-wrap text-foreground"
          v-html="content"
        />
      </div>
    </main>

    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, inject, onMounted } from "vue";
import { useSSRContext } from "vue";
import { useHead } from "@vueuse/head";
import Header from "@/components/Header.vue";
import HeaderButtons from "@/components/HeaderButtons.vue";
import Footer from "@/components/Footer.vue";

const breadcrumbLabels: Record<string, string> = {
  "privacy-policy": "Политика конфиденциальности",
  "personal-data-processing": "Правила обработки персональных данных",
  "terms-of-service": "Правила пользования сервисом",
};

const sectionLabels: Record<string, string> = {
  capy: "Специалистам",
  gorod: "Города",
  sravni: "Сравнение",
  howto: "Инструкции",
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
      default: "",
    },
    pageKey: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const apiOrigin = inject("apiOrigin", "");

    let preFetched: { title: string; content: string } | null = null;

    if (typeof window !== "undefined") {
      const g = (window as any).__PRE_FETCHED__;
      if (g?.[props.pageKey]) preFetched = g[props.pageKey];
    } else {
      try {
        const ctx = useSSRContext();
        if (ctx?.pageData?.content) {
          preFetched = { title: ctx.pageData.title || "", content: ctx.pageData.content || "" };
        }
      } catch {}
    }

    const pageTitle = ref(preFetched?.title || props.title);
    const content = ref(preFetched?.content || "");
    const loading = ref(!preFetched);

    async function fetchContent() {
      loading.value = true;
      const base = apiOrigin || (typeof window !== "undefined" ? window.location.origin : "");
      try {
        const res = await fetch(`${base}/api/pages/${encodeURIComponent(props.pageKey)}`);
        if (!res.ok) throw new Error("Page not found");
        const data = await res.json();
        content.value = data.content;
        pageTitle.value = data.title;
      } catch {
        content.value = "";
        pageTitle.value = props.title;
      } finally {
        loading.value = false;
      }
    }

    if (!preFetched) {
      onMounted(() => {
        fetchContent();
        window.scrollTo(0, 0);
      });
    } else {
      onMounted(() => {
        window.scrollTo(0, 0);
      });
    }

    watch(() => props.pageKey, () => {
      fetchContent();
      if (typeof window !== "undefined") {
        window.scrollTo(0, 0);
      }
    });

    const breadcrumbItems = computed(() => {
      const parts = props.pageKey.split("/");
      const items = [{ "@type": "ListItem", position: 1, name: "Главная", item: "https://capytime.ru/" }];

      if (parts.length === 1) {
        const label = breadcrumbLabels[parts[0]] || props.title || parts[0];
        items.push({ "@type": "ListItem", position: 2, name: label });
      } else if (parts.length === 2) {
        const [section, slug] = parts;
        const sectionLabel = sectionLabels[section] || section;
        items.push({ "@type": "ListItem", position: 2, name: sectionLabel });
        items.push({ "@type": "ListItem", position: 3, name: props.title || slug });
      }

      return items;
    });

    useHead({
      script: computed(() => [
        {
          type: "application/ld+json",
          innerHTML: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumbItems.value,
          }),
        },
      ]),
    });

    return { pageTitle, content, loading };
  },
});
</script>

<style scoped>
:deep(table) {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius);
  overflow: hidden;
  margin: 1.5em 0;
  font-size: 0.875rem;
}

:deep(th) {
  background: hsl(var(--muted));
  font-weight: 600;
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid hsl(var(--border));
  border-right: 1px solid hsl(var(--border));
}

:deep(th:last-child) {
  border-right: none;
}

:deep(td) {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid hsl(var(--border));
  border-right: 1px solid hsl(var(--border));
  vertical-align: top;
}

:deep(td:last-child) {
  border-right: none;
}

:deep(tr:last-child td) {
  border-bottom: none;
}

:deep(tr:nth-child(even) td) {
  background: hsl(var(--muted) / 0.4);
}

:deep(blockquote) {
  border-left: 3px solid hsl(var(--primary));
  padding: 1rem 1.25rem;
  margin: 1.5em 0;
  background: hsl(var(--muted) / 0.3);
  border-radius: 0 var(--radius) var(--radius) 0;
  font-style: italic;
  color: hsl(var(--foreground));
}

:deep(.cta) {
  margin: 2em 0;
  text-align: center;
}

:deep(.cta a),
:deep(a.btn) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.75rem 1.5rem;
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  transition: background 0.15s ease;
  text-decoration: none;
}

:deep(.cta a:hover),
:deep(a.btn:hover) {
  background: hsl(var(--primary) / 0.9);
}

:deep(.faq) {
  margin: 1.5em 0;
}

:deep(.faq p) {
  margin-bottom: 1.25em;
  padding-bottom: 1.25em;
  border-bottom: 1px solid hsl(var(--border));
}

:deep(.faq p:last-child) {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

:deep(.faq strong) {
  display: block;
  margin-bottom: 0.25em;
}

:deep(ul) {
  list-style: none;
  padding-left: 0;
  margin: 1em 0;
}

:deep(ul li) {
  padding-left: 1.75em;
  position: relative;
  margin-bottom: 0.75em;
}

:deep(ul li::before) {
  content: "✓";
  position: absolute;
  left: 0;
  top: 0;
  color: hsl(var(--primary));
  font-weight: 700;
  font-size: 1.1em;
}

:deep(ul.problems li::before) {
  content: "✕";
  color: hsl(var(--destructive));
}

:deep(ol) {
  list-style: none;
  counter-reset: num;
  padding-left: 0;
  margin: 1em 0;
}

:deep(ol li) {
  counter-increment: num;
  padding-left: 2.5em;
  position: relative;
  margin-bottom: 1em;
  min-height: 1.75em;
  display: flex;
  align-items: center;
}

:deep(ol li::before) {
  content: counter(num);
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 1.75em;
  height: 1.75em;
  border-radius: 50%;
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  font-size: 0.85em;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

:deep(h2) {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 2em;
  margin-bottom: 0.75em;
  color: hsl(var(--foreground));
}
</style>
