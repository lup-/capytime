import { createRouter, createWebHistory, type RouterHistory, type RouteRecordRaw } from "vue-router";
import IndexView from "./views/IndexView.vue";
import OnboardingView from "./views/OnboardingView.vue";
import ClientBookingView from "./views/ClientBookingView.vue";
import BookingSuccessView from "./views/BookingSuccessView.vue";
import PsychologistProfileView from "./views/PsychologistProfileView.vue";
import ScheduleView from "./views/ScheduleView.vue";
import NotFoundView from "./views/NotFoundView.vue";
import TextPageView from "./views/TextPageView.vue";
import InfoView from "./views/InfoView.vue";
import { ALL_STEPS } from "./stores/onboarding";

const onboardingSteps: RouteRecordRaw[] = [
  {
    path: "/onboarding",
    redirect: () => ({ name: "onboarding-calendar" }),
  },
  ...ALL_STEPS.map((step) => ({
    path: `/onboarding/${step.id}`,
    name: `onboarding-${step.id}`,
    component: OnboardingView,
  })),
];

const bookingSteps: RouteRecordRaw[] = [
  {
    path: "/booking",
    redirect: () => ({ name: "home" }),
  },
  {
    path: "/booking/:psychologistSlug",
    name: "booking",
    component: ClientBookingView,
    props: true,
  },
  {
    path: "/booking/:psychologistSlug/event/:editToken/success",
    name: "booking-success",
    component: BookingSuccessView,
    props: true,
  },
  {
    path: "/booking/:psychologistSlug/event/:editToken",
    name: "booking-edit",
    component: ClientBookingView,
    props: true,
    redirect: (to) => {
      return { name: "booking-format", params: { psychologistSlug: to.params.psychologistSlug, editToken: to.params.editToken } };
    },
  },
  {
    path: "/booking/:psychologistSlug/:editToken?/format",
    name: "booking-format",
    component: ClientBookingView,
    props: true,
  },
  {
    path: "/booking/:psychologistSlug/:editToken?/slot",
    name: "booking-slot",
    component: ClientBookingView,
    props: true,
  },
  {
    path: "/booking/:psychologistSlug/:editToken?/contact",
    name: "booking-contact",
    component: ClientBookingView,
    props: true,
  },
];

const routes: RouteRecordRaw[] = [
  { path: "/", name: "home", component: IndexView },
  ...onboardingSteps,
  ...bookingSteps,
  { path: "/profile/:slug", name: "profile", component: PsychologistProfileView },
  { path: "/schedule", name: "schedule", component: ScheduleView },
  { path: "/privacy-policy", name: "privacy-policy", component: TextPageView, props: { title: "Политика конфиденциальности", pageKey: "privacy-policy" } },
  { path: "/personal-data-processing", name: "personal-data-processing", component: TextPageView, props: { title: "Правила обработки персональных данных", pageKey: "personal-data-processing" } },
  { path: "/terms-of-service", name: "terms-of-service", component: TextPageView, props: { title: "Правила пользования сервисом", pageKey: "terms-of-service" } },
  { path: "/capy/:slug", component: TextPageView, props: (r) => ({ pageKey: `capy/${r.params.slug}` }) },
  { path: "/gorod/:slug", component: TextPageView, props: (r) => ({ pageKey: `gorod/${r.params.slug}` }) },
  { path: "/sravni/:slug", component: TextPageView, props: (r) => ({ pageKey: `sravni/${r.params.slug}` }) },
  { path: "/howto/:slug", component: TextPageView, props: (r) => ({ pageKey: `howto/${r.params.slug}` }) },
  { path: "/info", name: "info", component: InfoView },
  { path: "/:pathMatch(.*)*", name: "not-found", component: NotFoundView },
];

export function router(history?: RouterHistory) {
  return createRouter({
    history: history || createWebHistory(),
    routes,
  });
}

export { routes };

