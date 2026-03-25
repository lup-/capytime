<template>
  <div class="max-w-md mx-auto">
    <!-- Информация о психологе (общий заголовок для всех шагов) -->
    <PsychologistCard
      :psychologist="psychologist"
      class="mb-6"
    />

    <!-- Выбор формата -->
    <div
      v-if="step === 'format'"
      class="space-y-6"
    >
      <h2 class="text-xl font-bold text-foreground text-center">
        Выберите формат встречи
      </h2>
      <div class="space-y-3">
        <button
          v-if="psychologist.onlineEnabled"
          type="button"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
          @click="selectFormat('online')"
        >
          Онлайн
        </button>
        <div v-if="psychologist.offlineEnabled">
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors border border-input bg-background hover:bg-accent hover:text-accent-foreground w-full h-11"
            @click="selectFormat('offline')"
          >
            Очно
          </button>
          <p class="text-xs text-muted-foreground text-center mt-1">
            {{ psychologist.offlineAddress }}
          </p>
        </div>
      </div>
    </div>

    <!-- Выбор дня и времени -->
    <div
      v-else-if="step === 'slot'"
      class="space-y-6"
    >
      <div class="rounded-lg border border-border p-3">
        <select
          v-model="format"
          class="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
        >
          <option
            v-if="psychologist.onlineEnabled"
            value="online"
          >
            Онлайн
          </option>
          <option
            v-if="psychologist.offlineEnabled"
            value="offline"
          >
            Очно ({{ psychologist.offlineAddress }})
          </option>
        </select>
      </div>

      <h3 class="text-lg font-bold text-foreground">
        {{ currentMonthName }}
      </h3>

      <!-- Скролл по дням -->
      <div
        ref="daysScroller"
        class="flex gap-2 overflow-x-auto pb-2 cursor-grab active:cursor-grabbing select-none"
        style="scrollbar-width: none"
        @mousedown="onDaysMouseDown"
        @touchstart.passive="onDaysTouchStart"
      >
        <button
          v-for="day in days"
          :key="day.date.toISOString()"
          type="button"
          :disabled="!day.available"
          class="shrink-0 w-14 h-16 rounded-lg flex flex-col items-center justify-center text-sm font-medium transition-colors cursor-grab active:cursor-grabbing"
          :class="dayButtonClasses(day.date, day.available)"
          @mousedown.stop="onDaysMouseDown"
          @touchstart.stop.passive="onDaysTouchStart"
          @click="selectDate(day.date)"
        >
          <span class="text-xs">
            {{ shortDayName(day.date) }}
          </span>
          <span>{{ day.date.getDate() }}</span>
        </button>
      </div>

      <!-- Слоты времени -->
      <div
        v-if="selectedDate"
        class="grid grid-cols-3 gap-2"
      >
        <button
          v-for="time in timeSlots"
          :key="time"
          type="button"
          :disabled="occupiedSlots.includes(time)"
          class="h-11 rounded-lg text-sm font-medium transition-colors"
          :class="timeButtonClasses(time)"
          @click="selectedTime = time"
        >
          {{ time }}
        </button>
      </div>

      <!-- Часовой пояс (онлайн) -->
      <div v-if="format === 'online'">
        <p class="text-xs text-muted-foreground mb-1">
          Часовой пояс
        </p>
        <select
          v-model="clientTimezone"
          class="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
        >
          <option
            v-for="tz in timezones"
            :key="tz"
            :value="tz"
          >
            {{ tz }}
          </option>
        </select>
      </div>

      <button
        v-if="showStepButton"
        type="button"
        class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
        :disabled="!selectedDate || !selectedTime"
        @click="goToStep('contact')"
      >
        Далее
      </button>
    </div>

    <!-- Контакты клиента -->
    <div
      v-else-if="step === 'contact'"
      class="space-y-6"
    >
      <h2 class="text-xl font-bold text-foreground">
        Введите контактные данные
      </h2>
      <div class="space-y-3">
        <div>
          <label class="text-sm font-medium text-foreground">Имя</label>
          <input
            v-model="clientName"
            type="text"
            class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-foreground">
            Почта, на которую будет направлена информация о записи
          </label>
          <input
            v-model="clientEmail"
            type="email"
            class="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
          />
        </div>
      </div>
      <div class="flex items-center justify-between gap-3">
        <span class="text-sm text-foreground">
          Согласие на обработку
          <a
            href="#"
            class="text-primary hover:underline"
          >персональных данных</a>
        </span>
        <Toggle v-model="agreed" />
      </div>
      <button
        v-if="showStepButton"
        type="button"
        class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
        :disabled="!clientName || !clientEmail || !agreed"
        @click="goToStep('success')"
      >
        Записаться
      </button>
    </div>

    <!-- Успешная запись -->
    <div
      v-else-if="step === 'success'"
      class="space-y-6"
    >
      <h2 class="text-2xl font-bold text-foreground text-center">
        Вы записаны ✓
      </h2>
      <p class="text-muted-foreground text-center text-sm">
        Информация о встрече направлена на почту. Там вы можете перенести запись.
      </p>
      <div class="rounded-xl border border-border p-4 space-y-2">
        <p
          v-if="selectedDate"
          class="font-medium text-foreground"
        >
          {{ selectedDate.getDate() }} {{ monthName(selectedDate).toLowerCase() }},
          {{ fullDayName(selectedDate).toLowerCase() }}
        </p>
        <p class="text-foreground">
          {{ selectedTime }} (1 час)
        </p>
        <p
          v-if="format === 'online' && psychologist.videoLink"
          class="text-primary text-sm"
        >
          Ссылка на встречу ({{ psychologist.videoLink }})
        </p>
      </div>
      <button
        type="button"
        class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
      >
        Добавить в Яндекс.Календарь
      </button>
      <p class="text-xs text-muted-foreground text-center">
        Сервис записи CapyTime
      </p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Toggle from "@/components/ui/Toggle.vue";
import PsychologistCard from "@/components/PsychologistCard.vue";
import type { Psychologist } from "@/stores/onboarding";

export default defineComponent({
  name: "UserBooking",
  components: {
    Toggle,
    PsychologistCard,
  },
  props: {
    psychologist: {
      type: Object as () => Psychologist,
      required: true,
    },
    step: {
      type: String as () => "format" | "slot" | "contact" | "success",
      default: "format",
    },
    inputFormat: {
      type: String as () => "online" | "offline",
      default: undefined,
    },
    showStepButton: {
      type: Boolean,
      default: true,
    },
  },
  emits: ["update:step"],
  data() {
    return {
      format: "online" as "online" | "offline",
      selectedDate: null as Date | null,
      selectedTime: null as string | null,
      clientName: "",
      clientEmail: "",
      agreed: true,
      clientTimezone: "",
      timezones: [
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
      ] as string[],
      days: [] as { date: Date; available: boolean }[],
      timeSlots: [] as string[],
      occupiedSlots: ["12:00", "15:00"] as string[],
      currentMonthIndex: new Date().getMonth(),
      months: [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
      ] as string[],
      dayNames: ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"] as string[],
      fullDayNames: [
        "Воскресенье",
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
      ] as string[],
      isDraggingDays: false,
      daysDragStartX: 0,
      daysDragScrollLeft: 0,
    };
  },
  computed: {
    currentMonthName(): string {
      return this.months[this.currentMonthIndex];
    },
  },
  watch: {
    inputFormat(val: "online" | "offline" | undefined) {
      if (val !== undefined) {
        this.format = val;
      }
    },
    psychologist: {
      handler() {
        this.generateDays();
        this.generateTimeSlots();
      },
      deep: true,
    },
    format() {
      this.generateTimeSlots();
    },
  },
  created() {
    if (this.inputFormat !== undefined) {
      this.format = this.inputFormat;
    }
    this.clientTimezone = this.timezones[1];
    this.generateDays();
    this.generateTimeSlots();
  },
  methods: {
    generateDays() {
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth();
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const workDays =
        this.format === "online" ? this.psychologist.workDaysOnline : this.psychologist.workDaysOffline;

      const list: { date: Date; available: boolean }[] = [];
      const today = new Date(year, month, now.getDate());
      for (let day = now.getDate(); day <= daysInMonth; day += 1) {
        const date = new Date(year, month, day);
        const dayOfWeek = date.getDay();
        const adjustedDay = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
        const available = workDays.includes(adjustedDay) && date >= today;
        list.push({ date, available });
      }
      this.days = list;
    },
    generateTimeSlots() {
      const isOnline = this.format === "online";
      const fromParts = (isOnline ? this.psychologist.workFromOnline : this.psychologist.workFromOffline).split(":");
      const toParts = (isOnline ? this.psychologist.workToOnline : this.psychologist.workToOffline).split(":");
      let currentMinutes = parseInt(fromParts[0], 10) * 60 + parseInt(fromParts[1] || "0", 10);
      const endMinutes = parseInt(toParts[0], 10) * 60 + parseInt(toParts[1] || "0", 10);
      const slotDuration = isOnline ? this.psychologist.slotDurationOnline : this.psychologist.slotDurationOffline || 60;
      const slots: string[] = [];

      while (currentMinutes < endMinutes) {
        const hours = Math.floor(currentMinutes / 60);
        const mins = currentMinutes % 60;
        slots.push(`${String(hours).padStart(2, "0")}:${String(mins).padStart(2, "0")}`);
        currentMinutes += slotDuration;
      }
      this.timeSlots = slots;
    },
    selectFormat(fmt: "online" | "offline") {
      this.format = fmt;
      this.$emit("update:step", "slot");
      this.selectedDate = null;
      this.selectedTime = null;
      this.generateDays();
    },
    goToStep(step: "format" | "slot" | "contact" | "success") {
      this.$emit("update:step", step);
    },
    selectDate(date: Date) {
      this.selectedDate = date;
      this.selectedTime = null;
    },
    shortDayName(date: Date): string {
      return this.dayNames[date.getDay()];
    },
    fullDayName(date: Date): string {
      return this.fullDayNames[date.getDay()];
    },
    monthName(date: Date): string {
      return this.months[date.getMonth()];
    },
    dayButtonClasses(date: Date, available: boolean) {
      const isSelected = this.selectedDate && this.selectedDate.toDateString() === date.toDateString();
      if (isSelected) {
        return "bg-primary text-primary-foreground";
      }
      if (available) {
        return "bg-background border-2 border-primary text-primary";
      }
      return "bg-secondary text-muted-foreground";
    },
    timeButtonClasses(time: string) {
      const occupied = this.occupiedSlots.includes(time);
      const isSelected = this.selectedTime === time;
      if (isSelected) {
        return "bg-primary text-primary-foreground";
      }
      if (occupied) {
        return "bg-secondary text-muted-foreground";
      }
      return "bg-background border-2 border-primary text-primary";
    },
    onDaysMouseDown(e: MouseEvent) {
      const el = this.$refs.daysScroller as HTMLDivElement | undefined;
      if (!el) return;
      this.isDraggingDays = true;
      this.daysDragStartX = e.pageX;
      this.daysDragScrollLeft = el.scrollLeft;
      window.addEventListener("mousemove", this.onDaysMouseMove);
      window.addEventListener("mouseup", this.onDaysMouseUp);
    },
    onDaysMouseMove(e: MouseEvent) {
      if (!this.isDraggingDays) return;
      const el = this.$refs.daysScroller as HTMLDivElement | undefined;
      if (!el) return;
      const x = e.pageX;
      const walk = (x - this.daysDragStartX) * 1.5;
      el.scrollLeft = this.daysDragScrollLeft - walk;
    },
    onDaysMouseUp() {
      if (!this.isDraggingDays) return;
      this.isDraggingDays = false;
      window.removeEventListener("mousemove", this.onDaysMouseMove);
      window.removeEventListener("mouseup", this.onDaysMouseUp);
    },
    onDaysTouchStart(e: TouchEvent) {
      const el = this.$refs.daysScroller as HTMLDivElement | undefined;
      if (!el) return;
      const touch = e.touches[0];
      this.isDraggingDays = true;
      this.daysDragStartX = touch.pageX;
      this.daysDragScrollLeft = el.scrollLeft;
      window.addEventListener("touchmove", this.onDaysTouchMove, { passive: false });
      window.addEventListener("touchend", this.onDaysTouchEnd);
      window.addEventListener("touchcancel", this.onDaysTouchEnd);
    },
    onDaysTouchMove(e: TouchEvent) {
      if (!this.isDraggingDays) return;
      const el = this.$refs.daysScroller as HTMLDivElement | undefined;
      if (!el) return;
      const touch = e.touches[0];
      const x = touch.pageX;
      const walk = (x - this.daysDragStartX) * 1.5;
      el.scrollLeft = this.daysDragScrollLeft - walk;
      e.preventDefault();
    },
    onDaysTouchEnd() {
      if (!this.isDraggingDays) return;
      this.isDraggingDays = false;
      window.removeEventListener("touchmove", this.onDaysTouchMove);
      window.removeEventListener("touchend", this.onDaysTouchEnd);
      window.removeEventListener("touchcancel", this.onDaysTouchEnd);
    },
  },
});
</script>
