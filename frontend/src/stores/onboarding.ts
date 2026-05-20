import { defineStore } from "pinia";
import { getPsychologistSlug, getLocalTimezone } from "@/lib/utils";
import type { Psychologist, ScheduleParams, PsychologistProfile } from "@/lib/types";
import { useAuthStore } from "./auth";
import { usePsychologistStore } from "./psychologist";

export const ALL_STEPS = [
  { id: "calendar", label: "Календарь" },
  { id: "personal", label: "Личные данные" },
  { id: "photo", label: "Фотография" },
  { id: "format", label: "Формат работы" },
  { id: "online", label: "Онлайн" },
  { id: "offline", label: "Очно" },
  { id: "video", label: "Видеозвонки" },
  { id: "done", label: "Готово" },
];

export const DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

const STORAGE_KEY = "capytime_onboarding";

interface OnboardingStorage {
  completedSteps?: string[];
}

function loadOnboardingState(): OnboardingStorage {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return {};
}

function saveOnboardingState(state: OnboardingStorage) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {}
}

interface OnboardingState {
  psychologistId: string | null;
  completedSteps: string[];
  firstName: string;
  lastName: string;
  specialties: string[];
  problems: string[];
  offlineAddress: string;
  offlineSameAsOnline: boolean;
  timezone: string;
  avatar: string | null;
  videoLink: string;
  videoConferenceMode: "per_booking" | "single";
  yandexTelemostConnected: boolean;
  googleCalendarConnected: boolean;
  online: ScheduleParams;
  offline: ScheduleParams;
}

export const useOnboardingStore = defineStore("onboarding", {
  state: (): OnboardingState => {
    const saved = loadOnboardingState();
    return {
      psychologistId: null,
      completedSteps: saved.completedSteps || [],
      firstName: "",
      lastName: "",
      specialties: [],
      problems: [],
      offlineAddress: "",
      offlineSameAsOnline: true,
      timezone: getLocalTimezone(),
      avatar: null,
      videoLink: "",
      videoConferenceMode: "per_booking",
      yandexTelemostConnected: false,
      googleCalendarConnected: false,
      online: {
        enabled: true,
        price: "",
        days: [0, 1, 2, 3, 4],
        timeFrom: "10:00",
        timeTo: "19:00",
        breakNeeded: true,
        breakDuration: "30",
        slotDuration: 60,
      },
      offline: {
        enabled: true,
        price: "",
        days: [0, 1, 2, 3, 4],
        timeFrom: "10:00",
        timeTo: "19:00",
        breakNeeded: true,
        breakDuration: "30",
        slotDuration: 60,
      },
    };
  },
  getters: {
    steps(): { id: string; label: string; hidden?: boolean }[] {
      return ALL_STEPS.map((s) => ({
        ...s,
        hidden:
          (s.id === "online" && !this.online.enabled) ||
          (s.id === "offline" && !this.offline.enabled),
      }));
    },
    visibleStepIds(): string[] {
      return this.steps.filter((s) => !s.hidden).map((s) => s.id);
    },
    bookingLink(): string {
      return `capytime.ru/booking/${this.psychologistSlug}`;
    },
    psychologistSlug(): string {
      let psychologist = useAuthStore().psychologist || {};
      return getPsychologistSlug({...psychologist, firstName: this.firstName, lastName: this.lastName });
    },
    psychologist(): Psychologist {
      const onlineBreakDuration = this.online.breakNeeded ? parseInt(this.online.breakDuration || "30", 10) : 0;
      const offlineBreakDuration = this.offline.breakNeeded ? parseInt(this.offline.breakDuration || "30", 10) : 0;

      const offlineFrom = this.offlineSameAsOnline ? this.online.timeFrom : this.offline.timeFrom;
      const offlineTo = this.offlineSameAsOnline ? this.online.timeTo : this.offline.timeTo;

      return {
        id: "",
        firstName: this.firstName,
        lastName: this.lastName,
        slug: this.psychologistSlug,
        specialty: this.specialties.join(", ") || "",
        avatar: this.avatar,
        online: {
          enabled: this.online.enabled,
          price: this.online.price || "0",
          days: this.online.days,
          timeFrom: this.online.timeFrom || "10:00",
          timeTo: this.online.timeTo || "19:00",
          breakNeeded: this.online.breakNeeded,
          breakDuration: this.online.breakDuration,
          slotDuration: 60,
        },
        offline: {
          enabled: this.offline.enabled,
          price: this.offline.price || "0",
          days: this.offline.days,
          timeFrom: offlineFrom || "10:00",
          timeTo: offlineTo || "19:00",
          breakNeeded: this.offline.breakNeeded,
          breakDuration: this.offline.breakDuration,
          slotDuration: 60,
        },
        offlineAddress: this.offlineAddress || "",
        timezone: this.timezone,
        videoLink: this.videoLink || null,
        videoConferenceMode: this.videoConferenceMode,
        problems: this.problems,
        googleCalendarConnected: this.googleCalendarConnected,
        yandexTelemostConnected: this.yandexTelemostConnected,
      };
    },
  },
  actions: {
    async loadFromBackend(token: string): Promise<boolean> {
      const authStore = useAuthStore();
      authStore.token = token;
      const verified = await authStore.verify();
      
      if (!verified || !authStore.psychologist) {
        this.reset();
        return false;
      }
      
      const data = authStore.psychologist;
      
      if (data.id) {
        this.psychologistId = data.id;
      }
      
      if (data.firstName) {
        this.firstName = data.firstName;
      }
      if (data.lastName) {
        this.lastName = data.lastName;
      }
      
      if (data.specialty) {
        this.specialties = data.specialty.split(", ").filter(Boolean);
      }
      if (data.problems) {
        this.problems = [...data.problems];
      }

      this.googleCalendarConnected = data.googleCalendarConnected;
      this.yandexTelemostConnected = data.yandexTelemostConnected;

      if (data.timezone) {
        this.timezone = data.timezone;
      }
      
      if (data.online) {
        this.online = {
          enabled: data.online.enabled ?? true,
          price: data.online.price ?? "",
          days: data.online.days ?? [0, 1, 2, 3, 4],
          timeFrom: data.online.timeFrom ?? "10:00",
          timeTo: data.online.timeTo ?? "19:00",
          breakNeeded: data.online.breakNeeded ?? true,
          breakDuration: data.online.breakDuration || "30",
          slotDuration: data.online.slotDuration || 60,
        };
      }
      
      if (data.offline) {
        this.offline = {
          enabled: data.offline.enabled ?? true,
          price: data.offline.price ?? "",
          days: data.offline.days ?? [0, 1, 2, 3, 4],
          timeFrom: data.offline.timeFrom ?? "10:00",
          timeTo: data.offline.timeTo ?? "19:00",
          breakNeeded: data.offline.breakNeeded ?? true,
          breakDuration: data.offline.breakDuration || "30",
          slotDuration: data.offline.slotDuration || 60,
        };
      }
      
      if (data.offlineAddress) {
        this.offlineAddress = data.offlineAddress;
      }
      
      if (data.videoConferenceMode) {
        this.videoConferenceMode = data.videoConferenceMode;
      }
      if (data.videoLink) {
        this.videoLink = data.videoLink;
      }
      
      if (data.avatar) {
        this.avatar = data.avatar;
      }
      
      return true;
    },
    async persist() {
      const psychologistStore = usePsychologistStore();
      
      if (this.psychologistId) {
        await psychologistStore.savePsychologist(this.psychologistId, this.psychologist);
      }
    },
    markStepComplete(step: string) {
      if (!this.completedSteps.includes(step)) {
        this.completedSteps.push(step);
        saveOnboardingState({ completedSteps: this.completedSteps });
      }
      this.persist();
    },
    reset() {
      const authStore = useAuthStore();
      authStore.logout();
      localStorage.removeItem("capytimeAvatar");
      localStorage.removeItem(STORAGE_KEY);
    },
  },
});
