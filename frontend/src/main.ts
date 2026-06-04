import { createApp as createVueApp } from "vue";
import { createPinia } from "pinia";
import { createHead } from "@vueuse/head";
import { createMemoryHistory, createWebHistory, type RouterHistory } from "vue-router";
import App from "./App.vue";
import { router } from "./router";
import "./index.css";
import "./App.css";

export function createApp(history?: RouterHistory) {
  const app = createVueApp(App);
  const head = createHead();
  const pinia = createPinia();
  const _router = router(history || createWebHistory());

  app.use(pinia);
  app.use(_router);
  app.use(head);

  return { app, router: _router, pinia, head };
}

