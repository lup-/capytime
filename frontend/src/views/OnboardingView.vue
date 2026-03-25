<template>
  <div class="min-h-screen bg-background flex flex-col">
    <button
      v-if="showBackButton"
      type="button"
      class="fixed top-4 left-4 z-50 w-10 h-10 rounded-lg bg-card border border-border flex items-center justify-center text-foreground hover:bg-secondary transition-colors"
      @click="goBack"
    >
      ←
    </button>

    <OnboardingNav
      :steps="store.steps"
      :current-step="currentStep"
      :completed-steps="store.completedSteps"
      @update:currentStep="(val: string) => navigateTo(val)"
    />

    <main class="flex-1 container mx-auto px-4 py-8">
      <div class="max-w-md mx-auto">
        <!-- Шаг "Авторизация" -->
        <div
          v-if="currentStep === 'auth'"
          class="space-y-6 text-center"
        >
          <h2 class="text-2xl font-bold text-foreground">
            CapyTime
          </h2>
          <p class="text-muted-foreground">
            Авторизуйтесь, чтобы настроить сервис CapyTime
          </p>
          <input
            v-model="store.email"
            type="email"
            placeholder="example@mail.ru"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          />
          <div class="flex items-center justify-between gap-3">
            <span class="text-sm text-foreground">
              Согласие на обработку персональных данных
            </span>
            <Toggle v-model="store.agreed" />
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            :disabled="!store.email || !store.agreed"
            @click="goNext"
          >
            Настроить сервис
          </button>
          <p class="text-xs text-muted-foreground">
            Нажимая на кнопку, вы соглашаетесь с условиями пользования сервисом
          </p>
        </div>

        <!-- Шаг "Календарь" -->
        <div
          v-else-if="currentStep === 'calendar'"
          class="space-y-6"
        >
          <p class="text-foreground">
            Подключите к сервису свой рабочий календарь. CapyTime найдет в нем свободные слоты для записи клиентов. Если какой-то слот в календаре будет занят, клиент не сможет записаться на это время.
          </p>
          <p class="text-sm text-muted-foreground">
            Вы можете продолжать пользоваться своим календарем, а мы запишем новых клиентов и разошлем им уведомления
          </p>
          <div class="flex gap-4">
            <button
              type="button"
              class="flex flex-col items-center gap-2 rounded-xl border border-border p-6 hover:border-primary transition-colors"
            >
              <div class="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center text-xl font-bold text-foreground">
                Я
              </div>
              <span class="text-xs text-foreground">Яндекс Календарь</span>
            </button>
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="goNext"
          >
            Далее
          </button>
        </div>

        <!-- Шаг "Личные данные" -->
        <div
          v-else-if="currentStep === 'personal'"
          class="space-y-6"
        >
          <p class="text-foreground">
            Добавьте информацию о себе, чтобы клиенты на странице записи могли убедиться, что записываются именно к вам.
          </p>
          <div class="space-y-3">
            <div>
              <label class="text-sm font-medium text-foreground">Имя *</label>
              <input
                v-model="store.firstName"
                type="text"
                class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            <div>
              <label class="text-sm font-medium text-foreground">Фамилия</label>
              <input
                v-model="store.lastName"
                type="text"
                class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            <div>
              <label class="text-sm font-medium text-foreground">Деятельность</label>
              <MultiSelect
                v-model="store.specialties"
                :options="SPECIALTIES"
                label-key="label"
                value-key="value"
                placeholder="Выберите направления..."
                class="mt-1"
              />
            </div>
          </div>
          <BookingPreview :step="currentStep" />
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            :disabled="!store.firstName"
            @click="goNext"
          >
            Далее
          </button>
        </div>

        <!-- Шаг "Фото" -->
        <div
          v-else-if="currentStep === 'photo'"
          class="space-y-6"
        >
          <p class="text-foreground">
            Добавьте фотографию, чтобы клиентам было легко узнать вас на странице записи.
          </p>
          <div class="flex flex-col items-center gap-4">
            <label
              class="w-40 h-40 rounded-full border-2 border-dashed border-border flex flex-col items-center justify-center gap-2 text-muted-foreground cursor-pointer hover:border-primary overflow-hidden bg-secondary"
            >
              <template v-if="store.avatar">
                <img
                  :src="store.avatar"
                  alt="Аватар"
                  class="w-full h-full object-cover"
                />
              </template>
              <template v-else>
                <div class="text-center">
                  <div class="text-3xl mb-1">
                    👤
                  </div>
                  <span class="text-xs">Загрузить</span>
                </div>
              </template>
              <input
                type="file"
                accept="image/*"
                class="hidden"
                @change="handleAvatarUpload"
              />
            </label>
            <p class="text-xs text-muted-foreground">
              JPG, GIF или PNG. Макс. 5MB.
            </p>
          </div>
          <BookingPreview :step="currentStep" />
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="goNext"
          >
            Далее
          </button>
          <button
            type="button"
            class="w-full text-center text-sm text-primary hover:underline"
            @click="goNext"
          >
            Оставить без фото
          </button>
        </div>

        <!-- Шаг "Формат работы" -->
        <div
          v-else-if="currentStep === 'format'"
          class="space-y-6"
        >
          <p class="text-foreground">
            Выберите, для каких форматов работы настроить сервис.
          </p>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-foreground font-medium">Онлайн</span>
              <Toggle v-model="store.onlineEnabled" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-foreground font-medium">Очно</span>
              <Toggle v-model="store.offlineEnabled" />
            </div>
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            :disabled="!store.onlineEnabled && !store.offlineEnabled"
            @click="goNext"
          >
            Далее
          </button>
        </div>

        <!-- Шаг "Онлайн" -->
        <div
          v-else-if="currentStep === 'online'"
          class="space-y-6"
        >
          <div>
            <label class="text-sm font-medium text-foreground">Стоимость часа работы онлайн</label>
            <input
              v-model="store.onlinePrice"
              type="text"
              placeholder="4000"
              class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </div>
          <p class="text-foreground">
            Уточните информацию о расписании, чтобы настроить онлайн-запись.
          </p>
          <div>
            <p class="text-sm font-medium text-foreground mb-3">
              В какие дни отображать свободные слоты
            </p>
            <div class="flex gap-2">
              <button
                v-for="(day, index) in DAYS"
                :key="day"
                type="button"
                class="w-10 h-10 rounded-lg text-sm font-medium transition-colors"
                :class="store.onlineDays.includes(index) ? 'bg-primary text-primary-foreground' : 'bg-secondary text-foreground'"
                @click="toggleDay(index, 'online')"
              >
                {{ day }}
              </button>
            </div>
          </div>
          <div>
            <p class="text-sm font-medium text-foreground mb-3">
              В какие часы вы работаете
            </p>
            <div class="flex items-center gap-3">
              <span class="text-sm text-muted-foreground">с</span>
              <input
                v-model="store.onlineFrom"
                type="text"
                class="flex h-9 w-24 rounded-md border border-input bg-background px-3 py-1 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
              <span class="text-sm text-muted-foreground">до</span>
              <input
                v-model="store.onlineTo"
                type="text"
                class="flex h-9 w-24 rounded-md border border-input bg-background px-3 py-1 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </div>
          <div>
            <p class="text-sm font-medium text-foreground mb-2">
              Нужен ли вам перерыв после встречи
            </p>
            <div class="flex gap-3">
              <select
                v-model="store.breakNeeded"
                class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                <option value="yes">
                  Да
                </option>
                <option value="no">
                  Нет
                </option>
              </select>
              <select
                v-if="store.breakNeeded === 'yes'"
                v-model="store.breakDuration"
                class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                <option value="15">
                  15 минут
                </option>
                <option value="30">
                  30 минут
                </option>
                <option value="45">
                  45 минут
                </option>
                <option value="60">
                  60 минут
                </option>
              </select>
            </div>
          </div>
          <div>
            <p class="text-sm font-medium text-foreground mb-2">
              Часовой пояс
            </p>
            <select
              v-model="store.timezone"
              class="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
            >
              <option
                v-for="tz in TIMEZONES"
                :key="tz"
                :value="tz"
              >
                {{ tz }}
              </option>
            </select>
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="goNext"
          >
            Далее
          </button>
          <BookingPreview :step="currentStep" />
        </div>

        <!-- Шаг "Очно" -->
        <div
          v-else-if="currentStep === 'offline'"
          class="space-y-6"
        >
          <div>
            <label class="text-sm font-medium text-foreground">Стоимость часа очной работы</label>
            <input
              v-model="store.offlinePrice"
              type="text"
              placeholder="5000"
              class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
            />
          </div>
          <p class="text-foreground">
            Уточните информацию о расписании, чтобы настроить очную запись.
          </p>
          <div>
            <label class="text-sm font-medium text-foreground">Адрес для очных встреч</label>
            <input
              v-model="store.offlineAddress"
              type="text"
              placeholder="Город, метро, улица..."
              class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
            />
          </div>
          <div>
            <p class="text-sm font-medium text-foreground mb-3">
              В какие дни отображать свободные слоты
            </p>
            <div class="flex gap-2">
              <button
                v-for="(day, index) in DAYS"
                :key="day"
                type="button"
                class="w-10 h-10 rounded-lg text-sm font-medium transition-colors border-2"
                :class="offlineDayClasses(index)"
                @click="toggleDay(index, 'offline')"
              >
                {{ day }}
              </button>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-foreground">
              Часы работы как онлайн
            </span>
            <Toggle v-model="store.offlineSameAsOnline" />
          </div>
          <div v-if="!store.offlineSameAsOnline">
            <div>
              <p class="text-sm font-medium text-foreground mb-3">
                В какие часы вы работаете очно
              </p>
              <div class="flex items-center gap-3">
                <span class="text-sm text-muted-foreground">с</span>
                <input
                  v-model="store.offlineFrom"
                  type="text"
                  class="flex h-9 w-24 rounded-md border border-input bg-background px-3 py-1 text-sm"
                />
                <span class="text-sm text-muted-foreground">до</span>
                <input
                  v-model="store.offlineTo"
                  type="text"
                  class="flex h-9 w-24 rounded-md border border-input bg-background px-3 py-1 text-sm"
                />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-foreground mb-2">
                Перерыв после встречи
              </p>
              <div class="flex gap-3">
                <select
                  v-model="store.offlineBreakNeeded"
                  class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
                >
                  <option value="yes">
                    Да
                  </option>
                  <option value="no">
                    Нет
                  </option>
                </select>
                <select
                  v-if="store.offlineBreakNeeded === 'yes'"
                  v-model="store.offlineBreakDuration"
                  class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
                >
                  <option value="15">
                    15 минут
                  </option>
                  <option value="30">
                    30 минут
                  </option>
                  <option value="45">
                    45 минут
                  </option>
                  <option value="60">
                    60 минут
                  </option>
                </select>
              </div>
            </div>
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="goNext"
          >
            Далее
          </button>
          <BookingPreview :step="currentStep" />
        </div>

        <!-- Шаг "Перерыв" -->
        <div
          v-else-if="currentStep === 'break'"
          class="space-y-6"
        >
          <p class="text-foreground">
            Если сервис обнаружит в вашем расписании встречу, то также прибавит к ней перерыв. Чтобы вы смогли передохнуть и подготовиться.
          </p>
          <div class="rounded-xl border border-border p-6 bg-secondary text-center">
            <p class="text-sm text-muted-foreground">
              Пример: встреча 10:00–11:00, перерыв 30 мин → следующий свободный слот с 11:30
            </p>
          </div>
          <BookingPreview :step="currentStep" />
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="goNext"
          >
            Далее
          </button>
        </div>

        <!-- Шаг "Видеозвонки" -->
        <div
          v-else-if="currentStep === 'video'"
          class="space-y-6"
        >
          <p class="text-foreground">
            Добавьте ссылку на видеоконференцию. Она будет автоматически добавляться к онлайн-встрече.
          </p>
          <div>
            <label class="text-sm font-medium text-foreground">Ссылка на видеоконференцию</label>
            <input
              v-model="store.videoLink"
              type="text"
              placeholder="https://zoom.us/..."
              class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
            />
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="goNext"
          >
            Далее
          </button>
          <button
            type="button"
            class="w-full text-center text-sm text-primary hover:underline"
            @click="store.videoLink = ''; goNext()"
          >
            Пропустить
          </button>
        </div>

        <!-- Шаг "Готово" -->
        <div
          v-else-if="currentStep === 'done'"
          class="space-y-6 text-center"
        >
          <h2 class="text-2xl font-bold text-foreground">
            Поздравляем! 🎉
          </h2>
          <p class="text-foreground">
            Вы успешно настроили запись клиентов. Клиенты могут записаться по ссылке:
          </p>
          <div class="rounded-xl border border-border p-4 bg-secondary">
            <p class="font-medium text-primary">
            </p>
            {{ store.bookingLink }}
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="copyBookingLink"
          >
            Скопировать ссылку
          </button>
          <button
            type="button"
            class="w-full text-center text-sm text-primary hover:underline"
            @click="$router.push('/booking')"
          >
            Посмотреть страницу записи
          </button>
          <p class="text-xs text-muted-foreground">
            Внимание! Изменить настройки можно в разделе «Настройки» на главной странице CapyTime.ru
          </p>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import OnboardingNav from "@/components/OnboardingNav.vue";
import Footer from "@/components/Footer.vue";
import Toggle from "@/components/ui/Toggle.vue";
import MultiSelect from "@/components/ui/MultiSelect.vue";
import BookingPreview from "@/components/BookingPreview.vue";
import { useOnboardingStore, DAYS, TIMEZONES } from "@/stores/onboarding";

const SPECIALTIES = [
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

export default defineComponent({
  name: "OnboardingView",
  components: {
    OnboardingNav,
    Footer,
    Toggle,
    MultiSelect,
    BookingPreview,
  },
  data() {
    return {
      DAYS,
      TIMEZONES,
      SPECIALTIES,
    };
  },
  computed: {
    store(): ReturnType<typeof useOnboardingStore> {
      return useOnboardingStore();
    },
    currentStep(): string {
      const name = this.$route.name as string | undefined;
      const match = name?.match(/^onboarding-(.+)$/);
      const step = match ? match[1] : undefined;
      if (step && this.store.visibleStepIds.includes(step)) {
        return step;
      }
      if (this.store.completedSteps.length > 0) {
        const lastCompleted = this.store.completedSteps[this.store.completedSteps.length - 1];
        if (this.store.visibleStepIds.includes(lastCompleted)) {
          return lastCompleted;
        }
      }
      return this.store.visibleStepIds[0];
    },
    showBackButton(): boolean {
      return this.currentStep !== this.store.visibleStepIds[0];
    },
  },
  watch: {
    "$route.name"(): void {},
  },
  methods: {
    navigateTo(step: string) {
      this.$router.push({ name: `onboarding-${step}` });
    },
    goNext() {
      this.store.markStepComplete(this.currentStep);
      const idx = this.store.visibleStepIds.indexOf(this.currentStep);
      if (idx < this.store.visibleStepIds.length - 1) {
        const next = this.store.visibleStepIds[idx + 1];
        this.$router.push({ name: `onboarding-${next}` });
      }
    },
    goBack() {
      const idx = this.store.visibleStepIds.indexOf(this.currentStep);
      if (idx > 0) {
        const prev = this.store.visibleStepIds[idx - 1];
        this.$router.push({ name: `onboarding-${prev}` });
      } else {
        this.$router.push("/");
      }
    },
    toggleDay(index: number, type: "online" | "offline") {
      if (type === "online") {
        const list = this.store.onlineDays;
        this.store.onlineDays = list.includes(index) ? list.filter((d: number) => d !== index) : [...list, index];
        this.store.persist();
      } else {
        const list = this.store.offlineDays;
        this.store.offlineDays = list.includes(index) ? list.filter((d: number) => d !== index) : [...list, index];
        this.store.persist();
      }
    },
    offlineDayClasses(index: number): string {
      if (this.store.offlineDays.includes(index)) {
        return "bg-primary text-primary-foreground border-transparent";
      }
      if (this.store.onlineDays.includes(index)) {
        return "bg-secondary text-foreground border-primary";
      }
      return "bg-secondary text-foreground border-transparent";
    },
    copyBookingLink() {
      if (navigator?.clipboard?.writeText) {
        navigator.clipboard.writeText(this.store.bookingLink);
      }
    },
    handleAvatarUpload(e: Event) {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const result = ev.target?.result as string;
        this.store.avatar = result;
        this.store.persist();
      };
      reader.readAsDataURL(file);
    },
    persist() {
      this.store.persist();
    },
  },
});
</script>
