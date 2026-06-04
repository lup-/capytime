import { createApp } from "./main";
import { createMemoryHistory } from "vue-router";
import { renderToString } from "vue/server-renderer";
import { renderHeadToString } from "@vueuse/head";

export async function render(url: string, origin?: string, ssrApiUrl?: string) {
  const { app, router, head } = createApp(createMemoryHistory());

  const apiOrigin = origin || "";
  app.provide("apiOrigin", apiOrigin);

  router.push(url);
  await router.isReady();

  let statusCode = 200;
  if (router.currentRoute.value.name === "not-found") {
    statusCode = 404;
  }

  const route = router.currentRoute.value;
  const pageData: { title?: string; content?: string } = {};

  let pageKey: string | null = null;
  if (route.name === "privacy-policy") pageKey = "privacy-policy";
  else if (route.name === "personal-data-processing") pageKey = "personal-data-processing";
  else if (route.name === "terms-of-service") pageKey = "terms-of-service";
  else if (route.path.startsWith("/capy/")) pageKey = `capy/${(route.params as any).slug}`;
  else if (route.path.startsWith("/gorod/")) pageKey = `gorod/${(route.params as any).slug}`;
  else if (route.path.startsWith("/sravni/")) pageKey = `sravni/${(route.params as any).slug}`;
  else if (route.path.startsWith("/howto/")) pageKey = `howto/${(route.params as any).slug}`;

  if (pageKey) {
    try {
      const baseUrl = (ssrApiUrl || apiOrigin).replace(/\/+$/, "");
      const url = `${baseUrl}/api/pages/${encodeURIComponent(pageKey)}`;
      const res = await fetch(url);
      if (res.ok) {
        const json = await res.json();
        pageData.title = json.title;
        pageData.content = json.content;
      }
    } catch {}
  }

  const ctx: Record<string, any> = { pageData, pageKey };
  const html = await renderToString(app, ctx);
  const headResult = renderHeadToString(head);
  let headTags = headResult.headTags || "";

  const defaultTitle = "CapyTime — бесплатная и простая запись клиентов";
  const pageTitle = pageData.title ? `${pageData.title} — CapyTime` : defaultTitle;
  headTags = `<title>${pageTitle}</title>\n` + headTags;

  if (pageKey) {
    const parts = pageKey.split("/");
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
    const items = [{ "@type": "ListItem", position: 1, name: "Главная", item: "https://capytime.ru/" }];
    if (parts.length === 1) {
      const label = breadcrumbLabels[parts[0]] || pageData.title || parts[0];
      items.push({ "@type": "ListItem", position: 2, name: label });
    } else if (parts.length === 2) {
      const [section, slug] = parts;
      const sectionLabel = sectionLabels[section] || section;
      items.push({ "@type": "ListItem", position: 2, name: sectionLabel });
      items.push({ "@type": "ListItem", position: 3, name: pageData.title || slug });
    }
    headTags += `<script type="application/ld+json">${JSON.stringify({ "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items })}<\/script>\n`;
  }

  let preFetchedScript = "";
  if (pageData.content) {
    const payload: Record<string, { title: string; content: string }> = {};
    if (pageKey) payload[pageKey] = { title: pageData.title || "", content: pageData.content || "" };
    const safeJson = JSON.stringify(payload).replace(/</g, "\\u003C");
    preFetchedScript = `<script>window.__PRE_FETCHED__=${safeJson}<\/script>`;
  }

  return { html, headTags, preFetchedScript, ctx, statusCode };
}
