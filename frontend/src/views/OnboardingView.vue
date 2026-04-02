<template>
  <div class="min-h-screen bg-background flex flex-col relative">
    <Header>
      <template #left>
        <button
          v-if="showBackButton"
          type="button"
          class="w-10 h-10 rounded-lg bg-card border border-border flex items-center justify-center text-foreground hover:bg-secondary transition-colors"
          @click="goBack"
        >
          ←
        </button>
      </template>
    </Header>

    <OnboardingNav
      :steps="store.steps"
      :current-step="currentStep"
      :completed-steps="store.completedSteps"
      @update:currentStep="(val: string) => navigateTo(val)"
    />

    <main class="flex-1 container mx-auto px-4 py-8">
      <div class="max-w-md mx-auto">
        <!-- Шаг "Календарь" -->
        <div
          v-if="currentStep === 'calendar'"
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
              class="flex flex-col items-center gap-2 rounded-xl border p-6 transition-colors"
              :class="store.googleCalendarConnected ? 'bg-green-100 border-green-300 cursor-not-allowed' : isConnectingCalendar ? 'bg-gray-100 border-gray-300 cursor-wait' : 'border-border hover:border-primary'"
              :disabled="store.googleCalendarConnected || isConnectingCalendar"
              @click="connectGoogleCalendar"
            >
              <div
                class="w-12 h-12 rounded-lg flex items-center justify-center text-xl font-bold"
                :class="store.googleCalendarConnected ? 'bg-green-200 text-green-800' : isConnectingCalendar ? 'bg-gray-200 text-gray-600' : 'bg-secondary text-foreground'"
              >
                <template v-if="isConnectingCalendar">
                  <svg class="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </template>
                <template v-else>
                  G
                </template>
              </div>
              <span
                class="text-xs"
                :class="store.googleCalendarConnected ? 'text-green-700' : isConnectingCalendar ? 'text-gray-600' : 'text-foreground'"
              >{{ isConnectingCalendar ? 'Подключение...' : 'Google Календарь' }}</span>
            </button>
            <!-- Yandex Calendar ( временно скрыт ) -->
            <button
              v-if="false"
              type="button"
              class="flex flex-col items-center gap-2 rounded-xl border border-border p-6 hover:border-primary transition-colors"
            >
              <div class="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center text-xl font-bold text-foreground">
                Я
              </div>
              <span class="text-xs text-foreground">Яндекс Календарь</span>
            </button>
          </div>
          <div
            v-if="store.googleCalendarConnected"
            class="text-sm text-green-600"
          >
            Календарь подключён
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            :disabled="!store.googleCalendarConnected"
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
              <label class="text-sm font-medium text-foreground">Специализация</label>
              <MultiSelect
                v-model="store.specialties"
                :options="SPECIALTIES"
                label-key="label"
                value-key="value"
                placeholder="Выберите направления..."
                class="mt-1"
              />
            </div>
            <div>
              <label class="text-sm font-medium text-foreground">С чем вы работаете</label>
              <MultiSelect
                v-model="store.problems"
                :options="PROBLEMS"
                label-key="label"
                value-key="value"
                placeholder="Выберите проблемы..."
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
              <Toggle v-model="store.online.enabled" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-foreground font-medium">Очно</span>
              <Toggle v-model="store.offline.enabled" />
            </div>
          </div>
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            :disabled="!store.online.enabled && !store.offline.enabled"
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
              v-model="store.online.price"
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
                :class="store.online.days.includes(index) ? 'bg-primary text-primary-foreground' : 'bg-secondary text-foreground'"
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
                  v-model="store.online.timeFrom"
                  type="text"
                  class="flex h-9 w-24 rounded-md border border-input bg-background px-3 py-1 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
                <span class="text-sm text-muted-foreground">до</span>
                <input
                  v-model="store.online.timeTo"
                type="text"
                class="flex h-9 w-24 rounded-md border border-input bg-background px-3 py-1 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-foreground">
                Нужен ли вам перерыв после встречи
              </span>
              <Toggle v-model="store.online.breakNeeded" />
            </div>
            <select
              v-if="store.online.breakNeeded"
              v-model="store.online.breakDuration"
              class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm mt-3"
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
              v-model="store.offline.price"
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
          <div v-if="!store.offlineSameAsOnline" class="space-y-6">
            <div>
              <p class="text-sm font-medium text-foreground mb-3">
                В какие часы вы работаете очно
              </p>
              <div class="flex items-center gap-3">
                <span class="text-sm text-muted-foreground">с</span>
                <input
                  v-model="store.offline.timeFrom"
                  type="text"
                  class="flex h-9 w-24 rounded-md border border-input bg-background px-3 py-1 text-sm"
                />
                <span class="text-sm text-muted-foreground">до</span>
                <input
                  v-model="store.offline.timeTo"
                  type="text"
                  class="flex h-9 w-24 rounded-md border border-input bg-background px-3 py-1 text-sm"
                />
              </div>
            </div>
            <div>
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-foreground">
                  Перерыв после встречи
                </span>
                <Toggle v-model="store.offline.breakNeeded" />
              </div>
              <select
                v-if="store.offline.breakNeeded"
                v-model="store.offline.breakDuration"
                class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm mt-3"
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
        <!--div
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
        </div-->

        <!-- Шаг "Видеозвонки" -->
        <div
          v-else-if="currentStep === 'video'"
          class="space-y-6"
        >
          <p class="text-foreground">
            Как создавать видеоконференции для онлайн-встреч с клиентами?
          </p>
          <div class="space-y-3">
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                v-model="store.videoConferenceMode"
                type="radio"
                value="per_booking"
                class="w-4 h-4 text-primary"
              />
              <span class="text-sm text-foreground">Для каждой записи создаётся своя конференция</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                v-model="store.videoConferenceMode"
                type="radio"
                value="single"
                class="w-4 h-4 text-primary"
              />
              <span class="text-sm text-foreground">Одна конференция для всех клиентов</span>
            </label>
          </div>

          <div v-if="store.videoConferenceMode === 'single'">
            <label class="text-sm font-medium text-foreground">Ссылка на видеоконференцию</label>
            <input
              v-model="store.videoLink"
              type="text"
              placeholder="https://zoom.us/..."
              class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
            />
          </div>

          <div v-if="store.videoConferenceMode === 'per_booking'">
            <button
              type="button"
              class="flex flex-col items-center gap-2 rounded-xl border p-6 transition-colors"
              :class="store.yandexTelemostConnected ? 'bg-green-100 border-green-300 cursor-not-allowed' : isConnectingTelemost ? 'bg-gray-100 border-gray-300 cursor-wait' : 'border-border hover:border-primary'"
              :disabled="store.yandexTelemostConnected || isConnectingTelemost"
              @click="connectYandexTelemost"
            >
              <div
                class="w-12 h-12 rounded-lg flex items-center justify-center text-xl font-bold"
                :class="store.yandexTelemostConnected ? 'bg-green-200 text-green-800' : isConnectingTelemost ? 'bg-gray-200 text-gray-600' : 'bg-secondary text-foreground'"
              >
                <template v-if="isConnectingTelemost">
                  <svg class="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </template>
                <template v-else>
                  Я
                </template>
              </div>
              <span
                class="text-xs"
                :class="store.yandexTelemostConnected ? 'text-green-700' : isConnectingTelemost ? 'text-gray-600' : 'text-foreground'"
              >{{ isConnectingTelemost ? 'Подключение...' : 'Яндекс Телемост' }}</span>
            </button>
            <div
              v-if="store.yandexTelemostConnected"
              class="text-sm text-green-600 mt-2"
            >
              Яндекс Телемост подключён
            </div>
          </div>

          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            :disabled="!isVideoStepValid"
            @click="goNext"
          >
            Далее
          </button>
          <button
            v-if="!isVideoStepValid"
            type="button"
            class="w-full text-center text-sm text-primary hover:underline"
            @click="store.videoLink = ''; store.videoConferenceMode = 'per_booking'; goNext()"
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
          <div class="rounded-xl border border-border p-4 bg-secondary flex items-center justify-between gap-2">
            <span class="font-medium text-primary truncate">
              {{ store.bookingLink }}
            </span>
            <button
              type="button"
              class="flex-shrink-0 text-muted-foreground hover:text-primary"
              @click="copyBookingLink"
            >
              <Copy class="w-4 h-4" />
            </button>
          </div>
          <!--button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="$router.push(`/profile/${store.psychologistSlug}`)"
          >
            Посмотреть и дополнить свою страницу
          </button-->
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="$router.push(`/booking/${store.psychologistSlug}`)"
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
import Header from "@/components/Header.vue";
import OnboardingNav from "@/components/OnboardingNav.vue";
import Footer from "@/components/Footer.vue";
import Toggle from "@/components/ui/Toggle.vue";
import MultiSelect from "@/components/ui/MultiSelect.vue";
import BookingPreview from "@/components/BookingPreview.vue";
import { useOnboardingStore, DAYS } from "@/stores/onboarding";
import { useAuthStore } from "@/stores/auth";
import { usePsychologistStore, SPECIALTIES, PROBLEMS } from "@/stores/psychologist";
import { useErrorStore } from "@/stores/error";
import { getTimezones, getLocalTimezone } from "@/lib/utils";
import { Copy } from "lucide-vue-next";

export default defineComponent({
  name: "OnboardingView",
  components: {
    Header,
    OnboardingNav,
    Footer,
    Toggle,
    MultiSelect,
    BookingPreview,
    Copy,
  },
  data() {
    return {
      DAYS,
      TIMEZONES: getTimezones(),
      SPECIALTIES,
      PROBLEMS,
      isConnectingCalendar: false,
      isConnectingTelemost: false,
    };
  },
  async mounted() {
    const token = useAuthStore().token;
    if (token) {
      await this.store.loadFromBackend(token);
    }
    if (!this.store.timezone) {
      this.store.timezone = getLocalTimezone();
    }
    await this.handleOAuthCallback();

    if (this.currentStep !== "calendar" && !this.authStore.isAuthenticated) {
      useErrorStore().showError("Вы не авторизованы. Пожалуйста, начните с шага календаря.");
      this.$router.replace({ name: "onboarding-calendar" });
      return;
    }
  },
  computed: {
    store(): ReturnType<typeof useOnboardingStore> {
      return useOnboardingStore();
    },
    authStore(): ReturnType<typeof useAuthStore> {
      return useAuthStore();
    },
    currentStep(): string {
      const name = this.$route.name as string | undefined;
      const match = name?.match(/^onboarding-(.+)$/);
      const step = match ? match[1] : undefined;
      if (step && (this.store.visibleStepIds.includes(step) || step === "online" || step === "offline")) {
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
    isVideoStepValid(): boolean {
      if (this.store.videoConferenceMode === "per_booking") {
        return this.store.yandexTelemostConnected;
      }
      return !!this.store.videoLink;
    },
  },
  watch: {
    "$route.name"(): void {},
  },
  methods: {
    async handleOAuthCallback() {
      if (this.$route.query.error) {
        useErrorStore().showError(this.$route.query.error as string);
      }
      
      if (this.$route.query.psychologist_token) {
        const token = this.$route.query.psychologist_token as string;
        
        this.authStore.setToken(token);
        
        const isCalendarPage = window.location.pathname.includes("calendar");
        const isVideoPage = window.location.pathname.includes("video");
        
        if (isCalendarPage || isVideoPage) {
          await this.store.loadFromBackend(token);
        }
        
        const query = { ...this.$route.query };
        delete query.psychologist_token;
        delete query.code;
        delete query.state;
        delete query.error;
        
        this.$router.replace({ query });
      }
    },
    goNext() {
      this.store.markStepComplete(this.currentStep);
      const idx = this.store.visibleStepIds.indexOf(this.currentStep);
      const nextStep = this.store.visibleStepIds[idx + 1];
      
      if (nextStep) {
        this.$router.push({ name: `onboarding-${nextStep}` });
      }
      
      if (nextStep === "done") {
        this.finalizeOnboarding();
      }
    },
    async finalizeOnboarding() {
      const psychologistStore = usePsychologistStore();
      await this.authStore.verify();
      const psychologistId = this.authStore.psychologist?.id;
      if (psychologistId) {
        await psychologistStore.savePsychologist(psychologistId, this.store.psychologist, true);
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
    navigateTo(step: string) {
      if (this.store.visibleStepIds.includes(step)) {
        this.$router.push({ name: `onboarding-${step}` });
      } else if (step === "online" || step === "offline") {
        this.$router.push({ name: `onboarding-${step}` });
      }
    },
    toggleDay(index: number, type: "online" | "offline") {
      if (type === "online") {
        const list = this.store.online.days;
        this.store.online.days = list.includes(index) ? list.filter((d: number) => d !== index) : [...list, index];
        this.store.persist();
      } else {
        const list = this.store.offline.days;
        this.store.offline.days = list.includes(index) ? list.filter((d: number) => d !== index) : [...list, index];
        this.store.persist();
      }
    },
    offlineDayClasses(index: number): string {
      if (this.store.offline.days.includes(index)) {
        return "bg-primary text-primary-foreground border-transparent";
      }
      if (this.store.online.days.includes(index)) {
        return "bg-secondary text-foreground border-primary";
      }
      return "bg-secondary text-foreground border-transparent";
    },
    copyBookingLink() {
      if (navigator?.clipboard?.writeText) {
        navigator.clipboard.writeText(this.store.bookingLink);
        useErrorStore().showSuccess("Скопировано!");
      }
    },
    handleAvatarUpload(e: Event) {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (!file) return;
      
      this.uploadAvatar(file);
    },
    async uploadAvatar(file: File) {
      const psychologistId = this.authStore.psychologist?.id;
      if (!psychologistId) {
        useErrorStore().showError("Вы не авторизованы");
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch(
          `/api/psychologist/${psychologistId}/upload-avatar`,
          {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${this.authStore.token}`,
            },
            body: formData,
          }
        );

        if (!response.ok) {
          throw new Error("Upload failed");
        }

        const data = await response.json();
        this.store.avatar = data.avatar_url;
        this.store.persist();
      } catch (error) {
        console.error("Failed to upload avatar:", error);
        useErrorStore().showError("Не удалось загрузить аватар");
      }
    },
    async connectGoogleCalendar() {
      this.isConnectingCalendar = true;
      
      const returnUrl = `${window.location.origin}/onboarding/calendar`;
      const psychologistToken = this.authStore.token || "";
      
      try {
        const response = await fetch(
          `/api/oauth/google/authorize?psychologist_token=${encodeURIComponent(psychologistToken)}&return_url=${encodeURIComponent(returnUrl)}`
        );
        const data = await response.json();
        
        if (data.error) {
          useErrorStore().showError(data.error || "Не удалось начать авторизацию");
          this.isConnectingCalendar = false;
          return;
        }
        
        if (data.authorization_url) {
          window.location.href = data.authorization_url;
        }
      } catch (error) {
        console.error("Failed to start Google OAuth:", error);
        useErrorStore().showError("Не удалось подключить календарь. Попробуйте ещё раз.");
        this.isConnectingCalendar = false;
      }
    },
    async connectYandexTelemost() {
      this.isConnectingTelemost = true;
      
      const returnUrl = `${window.location.origin}/onboarding/video`;
      const psychologistToken = this.authStore.token || "";
      
      try {
        const response = await fetch(
          `/api/oauth/yandex/authorize?psychologist_token=${encodeURIComponent(psychologistToken)}&return_url=${encodeURIComponent(returnUrl)}`
        );
        const data = await response.json();
        
        if (data.error) {
          useErrorStore().showError(data.error || "Не удалось начать авторизацию");
          this.isConnectingTelemost = false;
          return;
        }
        
        if (data.authorization_url) {
          window.location.href = data.authorization_url;
        }
      } catch (error) {
        console.error("Failed to start Yandex Telemost OAuth:", error);
        useErrorStore().showError("Не удалось подключить Яндекс Телемост. Попробуйте ещё раз.");
        this.isConnectingTelemost = false;
      }
    },
    persist() {
      this.store.persist();
    },
  },
});
</script>
