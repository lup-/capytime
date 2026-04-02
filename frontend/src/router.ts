import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import IndexView from "./views/IndexView.vue";
import OnboardingView from "./views/OnboardingView.vue";
import ClientBookingView from "./views/ClientBookingView.vue";
import PsychologistProfileView from "./views/PsychologistProfileView.vue";
import ScheduleView from "./views/ScheduleView.vue";
import NotFoundView from "./views/NotFoundView.vue";
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
  },
  ...(["format", "slot", "contact", "success"] as const).map((step) => ({
    path: `/booking/:psychologistSlug/${step}`,
    name: `booking-${step}`,
    component: ClientBookingView,
  })),
];

const routes: RouteRecordRaw[] = [
  { path: "/", name: "home", component: IndexView },
  ...onboardingSteps,
  ...bookingSteps,
  { path: "/profile/:slug", name: "profile", component: PsychologistProfileView },
  { path: "/schedule", name: "schedule", component: ScheduleView },
  {
    path: "/oauth/google/callback",
    redirect: (to) => ({ name: "onboarding-calendar", query: to.query }),
  },
  { path: "/:pathMatch(.*)*", name: "not-found", component: NotFoundView },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

