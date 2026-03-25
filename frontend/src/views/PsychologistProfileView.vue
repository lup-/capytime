<template>
  <div class="min-h-screen bg-background flex flex-col">
    <main class="flex-1 container mx-auto px-4 py-8">
      <div class="max-w-md mx-auto space-y-8">
        <!-- Переключатель режима редактирования -->
        <div class="flex justify-end">
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md border border-input bg-background px-3 py-1 text-xs font-medium shadow-sm hover:bg-accent hover:text-accent-foreground"
            :class="editMode ? 'bg-primary text-primary-foreground border-transparent' : ''"
            @click="toggleEditMode"
          >
            {{ editMode ? "Готово" : "Редактировать" }}
          </button>
        </div>

        <button
          v-if="editMode"
          type="button"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md border border-input bg-background px-3 py-2 text-xs font-medium shadow-sm hover:bg-accent hover:text-accent-foreground w-full"
          @click="copyBookingLink"
        >
          Ссылка на страницу записи для клиентов
        </button>

        <!-- Аватар -->
        <div class="flex justify-center">
          <div v-if="avatar" class="relative">
            <img
              :src="avatar"
              alt="Аватар"
              class="w-40 h-40 rounded-full object-cover border-2 border-border"
            />
            <label
              v-if="editMode"
              class="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center cursor-pointer"
            >
              <span class="text-xs text-primary-foreground">
                ✎
              </span>
              <input
                type="file"
                accept="image/*"
                class="hidden"
                @change="handleAvatarUpload"
              />
            </label>
          </div>
          <label
            v-else
            class="w-40 h-40 rounded-full border-2 border-dashed border-border flex flex-col items-center justify-center gap-2 text-muted-foreground"
            :class="editMode ? 'cursor-pointer hover:border-primary' : ''"
          >
            <span class="text-3xl">
              ⬆
            </span>
            <span class="text-xs">Загрузить фото</span>
            <input
              v-if="editMode"
              type="file"
              accept="image/*"
              class="hidden"
              @change="handleAvatarUpload"
            />
          </label>
        </div>

        <!-- Имя -->
        <div>
          <div class="flex items-center">
            <input
              v-if="editingField === 'name'"
              v-model="name"
              type="text"
              class="text-2xl font-bold bg-transparent border-b border-input focus:outline-none"
            />
            <h1
              v-else
              class="text-2xl md:text-3xl font-bold text-foreground"
            >
              {{ name }}
            </h1>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('name')"
            >
              ✎
            </button>
          </div>
        </div>

        <!-- Направления -->
        <div>
          <div class="flex items-center mb-2">
            <span class="text-sm text-muted-foreground">
              Направления
            </span>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('specializations')"
            >
              ✎
            </button>
          </div>
          <div
            v-if="editingField === 'specializations'"
            class="flex flex-wrap gap-2"
          >
            <button
              v-for="spec in allSpecializations"
              :key="spec"
              type="button"
              class="px-3 py-1.5 rounded-lg text-sm transition-colors"
              :class="specializations.includes(spec) ? 'bg-primary text-primary-foreground' : 'bg-secondary text-foreground'"
              @click="toggleSpecialization(spec)"
            >
              {{ spec }}
            </button>
          </div>
          <div
            v-else
            class="flex flex-wrap gap-2"
          >
            <span
              v-for="spec in specializations"
              :key="spec"
              class="px-3 py-1.5 rounded-lg text-sm bg-secondary text-foreground"
            >
              {{ spec }}
            </span>
          </div>
        </div>

        <!-- Основные метрики -->
        <div class="space-y-2">
          <div class="flex items-center">
            <div v-if="editingField === 'experience'" class="flex items-center gap-2">
              <span class="text-foreground">Опыт</span>
              <input
                v-model="experience"
                type="text"
                class="w-16 h-8 rounded-md border border-input bg-background px-2 text-sm"
              />
              <span class="text-foreground">лет</span>
            </div>
            <p
              v-else
              class="font-bold text-foreground"
            >
              Опыт {{ experience }} лет
            </p>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('experience')"
            >
              ✎
            </button>
          </div>
          <div class="flex items-center">
            <div v-if="editingField === 'onlinePrice'" class="flex items-center gap-2">
              <input
                v-model="onlinePrice"
                type="text"
                class="w-20 h-8 rounded-md border border-input bg-background px-2 text-sm"
              />
              <span class="text-foreground">₽ / онлайн</span>
            </div>
            <p
              v-else
              class="font-bold text-foreground"
            >
              {{ onlinePrice }} ₽ / онлайн
            </p>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('onlinePrice')"
            >
              ✎
            </button>
          </div>
          <div class="flex items-center">
            <div v-if="editingField === 'offlinePrice'" class="flex items-center gap-2">
              <input
                v-model="offlinePrice"
                type="text"
                class="w-20 h-8 rounded-md border border-input bg-background px-2 text-sm"
              />
              <span class="text-foreground">₽ / очно</span>
            </div>
            <p
              v-else
              class="font-bold text-foreground"
            >
              {{ offlinePrice }} ₽ / очно
            </p>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('offlinePrice')"
            >
              ✎
            </button>
          </div>
          <div class="flex items-center">
            <input
              v-if="editingField === 'offlineAddress'"
              v-model="offlineAddress"
              type="text"
              class="flex-1 h-8 rounded-md border border-input bg-background px-2 text-sm"
            />
            <p
              v-else
              class="text-sm text-muted-foreground"
            >
              {{ offlineAddress }}
            </p>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('offlineAddress')"
            >
              ✎
            </button>
          </div>
        </div>

        <!-- CTA -->
        <router-link to="/booking">
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
          >
            Выбрать время
          </button>
        </router-link>

        <!-- С чем работаю -->
        <section>
          <div class="flex items-center mb-3">
            <h2 class="text-xl font-bold text-foreground">
              С чем я работаю
            </h2>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('problems')"
            >
              ✎
            </button>
          </div>
          <div v-if="editingField === 'problems'" class="space-y-3">
            <div class="flex flex-wrap gap-2">
              <span
                v-for="p in problems"
                :key="p"
                class="px-3 py-1.5 rounded-lg text-sm bg-primary/10 text-primary flex items-center gap-1"
              >
                {{ p }}
                <button
                  type="button"
                  class="text-primary hover:text-red-500"
                  @click="removeProblem(p)"
                >
                  ×
                </button>
              </span>
            </div>
            <div class="flex gap-2">
              <input
                v-model="problemInput"
                type="text"
                placeholder="Добавить проблему..."
                class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                @keydown.enter.prevent="addProblem(problemInput)"
              />
            </div>
            <div class="flex flex-wrap gap-1">
              <button
                v-for="p in availableProblems"
                :key="p"
                type="button"
                class="px-2 py-1 rounded text-xs bg-secondary text-muted-foreground hover:text-foreground"
                @click="addProblem(p)"
              >
                + {{ p }}
              </button>
            </div>
          </div>
          <div
            v-else
            class="flex flex-wrap gap-2"
          >
            <span
              v-for="p in problems"
              :key="p"
              class="px-3 py-1.5 rounded-lg text-sm bg-secondary text-foreground"
            >
              {{ p }}
            </span>
          </div>
        </section>

        <!-- Обо мне -->
        <section>
          <div class="flex items-center mb-3">
            <h2 class="text-xl font-bold text-foreground">
              Обо мне
            </h2>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('about')"
            >
              ✎
            </button>
          </div>
          <textarea
            v-if="editingField === 'about'"
            v-model="about"
            class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm min-h-[100px]"
            placeholder="Расскажите о себе..."
          />
          <p
            v-else
            class="text-muted-foreground"
          >
            {{ about || "Информация не заполнена" }}
          </p>
        </section>

        <!-- Образование -->
        <section>
          <div class="flex items-center mb-3">
            <h2 class="text-xl font-bold text-foreground">
              Образование
            </h2>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('education')"
            >
              ✎
            </button>
          </div>
          <textarea
            v-if="editingField === 'education'"
            v-model="education"
            class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm min-h-[100px]"
            placeholder="Укажите образование..."
          />
          <p
            v-else
            class="text-muted-foreground"
          >
            {{ education || "Информация не заполнена" }}
          </p>
        </section>

        <!-- Профессиональный опыт -->
        <section>
          <div class="flex items-center mb-3">
            <h2 class="text-xl font-bold text-foreground">
              Профессиональный опыт
            </h2>
            <button
              v-if="editMode"
              type="button"
              class="ml-2 text-muted-foreground hover:text-primary"
              @click="toggleField('proExperience')"
            >
              ✎
            </button>
          </div>
          <textarea
            v-if="editingField === 'proExperience'"
            v-model="proExperience"
            class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm min-h-[100px]"
            placeholder="Опишите профессиональный опыт..."
          />
          <p
            v-else
            class="text-muted-foreground"
          >
            {{ proExperience || "Информация не заполнена" }}
          </p>
        </section>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "PsychologistProfileView",
  data() {
    return {
      editMode: false,
      name: "Анна Петрова",
      specializations: ["КПТ", "Гештальт"] as string[],
      experience: "9",
      onlinePrice: "4000",
      offlinePrice: "5000",
      offlineAddress: "м. Курская, ул. Ленина, д.5",
      problems: ["Тревога", "Депрессия", "Самооценка"] as string[],
      about: "",
      education: "",
      proExperience: "",
      problemInput: "",
      avatar: null as string | null,
      editingField: null as string | null,
      allSpecializations: [
        "КПТ",
        "Гештальт",
        "Психоанализ",
        "Семейная терапия",
        "Арт-терапия",
        "EMDR",
        "Телесная терапия",
        "Экзистенциальная терапия",
      ] as string[],
      allProblems: [
        "Тревога",
        "Депрессия",
        "Отношения",
        "Самооценка",
        "Стресс",
        "Панические атаки",
        "Выгорание",
        "Горевание",
        "Зависимости",
        "Фобии",
      ] as string[],
    };
  },
  computed: {
    availableProblems(): string[] {
      return this.allProblems.filter((p) => !this.problems.includes(p));
    },
  },
  created() {
    if (typeof window !== "undefined") {
      const saved = window.localStorage.getItem("capytimeAvatar");
      if (saved) {
        this.avatar = saved;
      }
    }
  },
  methods: {
    toggleEditMode() {
      this.editMode = !this.editMode;
      if (!this.editMode) {
        this.editingField = null;
      }
    },
    toggleField(field: string) {
      if (!this.editMode) return;
      this.editingField = this.editingField === field ? null : field;
    },
    toggleSpecialization(spec: string) {
      if (this.specializations.includes(spec)) {
        this.specializations = this.specializations.filter((s) => s !== spec);
      } else {
        this.specializations = [...this.specializations, spec];
      }
    },
    addProblem(problem: string) {
      const trimmed = problem.trim();
      if (trimmed && !this.problems.includes(trimmed)) {
        this.problems = [...this.problems, trimmed];
      }
      this.problemInput = "";
    },
    removeProblem(problem: string) {
      this.problems = this.problems.filter((p) => p !== problem);
    },
    copyBookingLink() {
      const slug = this.name.toLowerCase().replace(/\s/g, "");
      const link = `capytime.ru/${slug}`;
      if (navigator?.clipboard?.writeText) {
        navigator.clipboard.writeText(link);
      }
    },
    handleAvatarUpload(e: Event) {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const result = ev.target?.result as string;
        this.avatar = result;
        if (typeof window !== "undefined") {
          window.localStorage.setItem("capytimeAvatar", result);
        }
      };
      reader.readAsDataURL(file);
    },
  },
});
</script>

