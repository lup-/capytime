import { defineStore } from "pinia";
import type { Psychologist, PsychologistUpdateRequest, Specialty } from "@/lib/types";
import { getPsychologistSlug } from "@/lib/utils";
import { useAuthStore } from "./auth";
import { useErrorStore } from "./error";

export const SPECIALTIES: Specialty[] = [
  { label: "КБТ", value: "КБТ" },
  { label: "Гештальт", value: "Гештальт" },
  { label: "Семейная терапия", value: "Семейная терапия" },
  { label: "Психоанализ", value: "Психоанализ" },
  { label: "Арт-терапия", value: "Арт-терапия" },
  { label: "Игровая терапия", value: "Игровая терапия" },
  { label: "Коучинг", value: "Коучинг" },
  { label: "Нейропсихология", value: "Нейропсихология" },
  { label: "Детская психология", value: "Детская психология" },
  { label: "Подростковая психология", value: "Подростковая психология" },
  { label: "Травматерапия", value: "Травматерапия" },
  { label: "EMDR", value: "EMDR" },
  { label: "Соматическая терапия", value: "Соматическая терапия" },
  { label: "Экзистенциальный анализ", value: "Экзистенциальный анализ" },
  { label: "Логотерапия", value: "Логотерапия" },
  { label: "Поведенческая терапия", value: "Поведенческая терапия" },
  { label: "Гипнотерапия", value: "Гипнотерапия" },
  { label: "Телесно-ориентированная терапия", value: "Телесно-ориентированная терапия" },
];

export const PROBLEMS: Specialty[] = [
  { label: "Тревога", value: "Тревога" },
  { label: "Депрессия", value: "Депрессия" },
  { label: "Отношения", value: "Отношения" },
  { label: "Самооценка", value: "Самооценка" },
  { label: "Стресс", value: "Стресс" },
  { label: "Панические атаки", value: "Панические атаки" },
  { label: "Выгорание", value: "Выгорание" },
  { label: "Горевание", value: "Горевание" },
  { label: "Зависимости", value: "Зависимости" },
  { label: "Фобии", value: "Фобии" },
];

interface PsychologistState {
  psychologist: Psychologist | null;
  editMode: boolean;
  editingField: string | null;
  problemInput: string;
}

export const usePsychologistStore = defineStore("psychologist", {
  state: (): PsychologistState => ({
    psychologist: null,
    editMode: false,
    editingField: null,
    problemInput: "",
  }),
  getters: {
    slug(): string {
      if (!this.psychologist) return "";
      return getPsychologistSlug(this.psychologist);
    },
    problems(): string[] {
      return this.psychologist?.problems || [];
    },
    availableProblems(): string[] {
      return PROBLEMS.map(p => p.value).filter((p) => !(this.psychologist?.problems || []).includes(p));
    },
    specialtiesList(): string[] {
      if (!this.psychologist) return [];
      return this.psychologist.specialty.split(", ").filter(Boolean);
    },
  },
  actions: {
    async loadById(psychologistId: string): Promise<Psychologist | null> {
      try {
        const response = await fetch(`/api/psychologist/${psychologistId}`);
        if (!response.ok) {
          useErrorStore().showError("Не удалось загрузить данные");
          return null;
        }
        const data = await response.json();
        return data as Psychologist;
      } catch (error) {
        console.error("Failed to load psychologist:", error);
        useErrorStore().showError("Не удалось загрузить данные");
        return null;
      }
    },
    async loadBySlug(slug: string): Promise<Psychologist | null> {
      try {
        const response = await fetch(`/api/psychologist/by-slug/${slug}`);
        if (!response.ok) {
          useErrorStore().showError("Не удалось загрузить данные");
          return null;
        }
        const data = await response.json();
        this.psychologist = data as Psychologist;
        return data as Psychologist;
      } catch (error) {
        console.error("Failed to load psychologist by slug:", error);
        useErrorStore().showError("Не удалось загрузить профиль");
        return null;
      }
    },
    async savePsychologist(psychologistId: string, data: Partial<PsychologistUpdateRequest>, sendEmail: boolean = false): Promise<boolean> {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) {
        useErrorStore().showError("Ключ доступа не найден");
        console.error("No auth token found");
        return false;
      }
      
      const payload = { ...data };
      if (sendEmail) {
        payload.send_email = true;
      }
      
      try {
        const response = await fetch(`/api/psychologist/${psychologistId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });
        return response.ok;
      } catch (error) {
        console.error("Failed to save psychologist:", error);
        useErrorStore().showError("Не удалось сохранить данные");
        return false;
      }
    },
    setPsychologist(psychologist: Psychologist) {
      this.psychologist = psychologist;
    },
    toggleEditMode() {
      this.editMode = !this.editMode;
      if (!this.editMode) {
        this.editingField = null;
      }
    },
    setEditingField(field: string) {
      if (!this.editMode) return;
      this.editingField = this.editingField === field ? null : field;
    },
    addProblem(problem: string) {
      const trimmed = problem.trim();
      if (trimmed && this.psychologist) {
        const current = this.psychologist.problems || [];
        if (!current.includes(trimmed)) {
          this.psychologist.problems = [...current, trimmed];
        }
        this.problemInput = "";
      }
    },
    removeProblem(problem: string) {
      if (this.psychologist?.problems) {
        this.psychologist.problems = this.psychologist.problems.filter((p) => p !== problem);
      }
    },
    toggleSpecialization(spec: string) {
      if (!this.psychologist) return;
      const current = this.psychologist.specialty.split(", ").filter(Boolean);
      if (current.includes(spec)) {
        this.psychologist.specialty = current.filter((s) => s !== spec).join(", ");
      } else {
        this.psychologist.specialty = [...current, spec].join(", ");
      }
    },
  },
});