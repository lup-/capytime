import { defineStore } from "pinia";

export const ALL_STEPS = [
  { id: "auth", label: "Авторизация" },
  { id: "calendar", label: "Календарь" },
  { id: "personal", label: "Личные данные" },
  { id: "photo", label: "Фотография" },
  { id: "format", label: "Формат работы" },
  { id: "online", label: "Онлайн" },
  { id: "offline", label: "Очно" },
  { id: "break", label: "Перерыв" },
  { id: "video", label: "Видеозвонки" },
  { id: "done", label: "Готово" },
];

export const TIMEZONES = [
  "(UTC +02:00) Калининград",
  "(UTC +03:00) Москва",
  "(UTC +04:00) Самара",
  "(UTC +05:00) Екатеринбург",
  "(UTC +06:00) Омск",
  "(UTC +07:00) Красноярск",
  "(UTC +08:00) Иркутск",
  "(UTC +09:00) Якутск",
  "(UTC +10:00) Владивосток",
  "(UTC +11:00) Магадан",
  "(UTC +12:00) Камчатка",
];

export const DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

export interface Psychologist {
  name: string;
  specialty: string;
  avatar: string | null;
  onlineEnabled: boolean;
  offlineEnabled: boolean;
  onlinePrice: string;
  offlinePrice: string;
  offlineAddress: string;
  workDaysOnline: number[];
  workDaysOffline: number[];
  workFromOnline: string;
  workToOnline: string;
  workFromOffline: string;
  workToOffline: string;
  slotDurationOnline: number;
  slotDurationOffline: number;
  timezone: string;
  videoLink: string | null;
}

const STORAGE_KEY = "capytime_onboarding";

interface OnboardingState {
  completedSteps: string[];
  onlineEnabled: boolean;
  offlineEnabled: boolean;
  email: string;
  agreed: boolean;
  firstName: string;
  lastName: string;
  specialties: string[];
  onlinePrice: string;
  offlinePrice: string;
  offlineAddress: string;
  onlineDays: number[];
  offlineDays: number[];
  onlineFrom: string;
  onlineTo: string;
  offlineSameAsOnline: boolean;
  offlineFrom: string;
  offlineTo: string;
  breakNeeded: string;
  breakDuration: string;
  offlineBreakNeeded: string;
  offlineBreakDuration: string;
  timezone: string;
  avatar: string | null;
  videoLink: string;
}

function loadFromStorage(): Partial<OnboardingState> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return {};
}

function saveToStorage(state: OnboardingState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {}
}

export const useOnboardingStore = defineStore("onboarding", {
  state: (): OnboardingState => {
    const saved = loadFromStorage();
    const offset = -new Date().getTimezoneOffset() / 60;
    const match = TIMEZONES.find((tz) => tz.includes(`+${String(offset).padStart(2, "0")}:00`));

    return {
      completedSteps: saved.completedSteps || [],
      onlineEnabled: saved.onlineEnabled ?? true,
      offlineEnabled: saved.offlineEnabled ?? true,
      email: saved.email || "",
      agreed: saved.agreed ?? true,
      firstName: saved.firstName || "",
      lastName: saved.lastName || "",
      specialties: saved.specialties || [],
      onlinePrice: saved.onlinePrice || "",
      offlinePrice: saved.offlinePrice || "",
      offlineAddress: saved.offlineAddress || "",
      onlineDays: saved.onlineDays ?? [0, 1, 2, 3, 4],
      offlineDays: saved.offlineDays ?? [0, 1, 2, 3, 4],
      onlineFrom: saved.onlineFrom || "10:00",
      onlineTo: saved.onlineTo || "19:00",
      offlineSameAsOnline: saved.offlineSameAsOnline ?? true,
      offlineFrom: saved.offlineFrom || "10:00",
      offlineTo: saved.offlineTo || "19:00",
      breakNeeded: saved.breakNeeded || "yes",
      breakDuration: saved.breakDuration || "30",
      offlineBreakNeeded: saved.offlineBreakNeeded || "yes",
      offlineBreakDuration: saved.offlineBreakDuration || "30",
      timezone: saved.timezone || match || TIMEZONES[1],
      avatar: saved.avatar || null,
      videoLink: saved.videoLink || "",
    };
  },
  getters: {
    steps(): { id: string; label: string; hidden?: boolean }[] {
      return ALL_STEPS.map((s) => ({
        ...s,
        hidden:
          (s.id === "online" && !this.onlineEnabled) ||
          (s.id === "offline" && !this.offlineEnabled),
      }));
    },
    visibleStepIds(): string[] {
      return this.steps.filter((s) => !s.hidden).map((s) => s.id);
    },
    bookingLink(): string {
      const translit = (s: string) => {
        const map: Record<string, string> = {
          а: "a", б: "b", в: "v", г: "g", д: "d", е: "e", ё: "yo", ж: "zh", з: "z", и: "i",
          й: "y", к: "k", л: "l", м: "m", н: "n", о: "o", п: "p", р: "r", с: "s", т: "t",
          у: "u", ф: "f", х: "h", ц: "ts", ч: "ch", ш: "sh", щ: "sch", ъ: "", ы: "y", ь: "",
          э: "e", ю: "yu", я: "ya",
        };
        return s.toLowerCase().split("").map((c) => map[c] || c).join("").replace(/[^a-z0-9]/g, "");
      };
      const first = translit(this.firstName.trim());
      const last = translit(this.lastName.trim());
      const slug = last ? `${first}-${last}` : first || "yourname";
      return `capytime.ru/${slug}`;
    },
    psychologist(): Psychologist {
      const onlineBreakDuration = this.breakNeeded === "yes" ? parseInt(this.breakDuration || "30", 10) : 0;
      const offlineBreakDuration = this.offlineBreakNeeded === "yes" ? parseInt(this.offlineBreakDuration || "30", 10) : 0;

      const offlineFrom = this.offlineSameAsOnline ? this.onlineFrom : this.offlineFrom;
      const offlineTo = this.offlineSameAsOnline ? this.onlineTo : this.offlineTo;

      return {
        name: `${this.firstName} ${this.lastName}`.trim() || "Специалист",
        specialty: this.specialties.join(", ") || "",
        avatar: this.avatar,
        onlineEnabled: this.onlineEnabled,
        offlineEnabled: this.offlineEnabled,
        onlinePrice: this.onlinePrice || "0",
        offlinePrice: this.offlinePrice || "0",
        offlineAddress: this.offlineAddress || "",
        workDaysOnline: this.onlineDays,
        workDaysOffline: this.offlineDays,
        workFromOnline: this.onlineFrom || "10:00",
        workToOnline: this.onlineTo || "19:00",
        workFromOffline: offlineFrom || "10:00",
        workToOffline: offlineTo || "19:00",
        slotDurationOnline: 60 + onlineBreakDuration,
        slotDurationOffline: 60 + offlineBreakDuration,
        timezone: this.timezone,
        videoLink: this.videoLink || null,
      };
    },
  },
  actions: {
    persist() {
      saveToStorage(this.$state);
    },
    markStepComplete(step: string) {
      if (!this.completedSteps.includes(step)) {
        this.completedSteps.push(step);
      }
      this.persist();
    },
    reset() {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem("capytimeAvatar");
    },
  },
});
