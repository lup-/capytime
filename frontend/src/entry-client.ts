import { createApp } from "./main";
import { createWebHistory } from "vue-router";

const { app, router } = createApp(createWebHistory());

router.isReady().then(() => {
  app.mount("#root");
});
