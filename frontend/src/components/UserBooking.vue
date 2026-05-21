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
      <template v-if="hasBothFormats">
        <h2 class="text-xl font-bold text-foreground text-center">
          Выберите формат встречи
        </h2>
        <div class="space-y-3">
          <button
            v-if="psychologist.online.enabled"
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            @click="selectFormat('online')"
          >
            Онлайн
          </button>
          <div v-if="psychologist.offline.enabled">
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
      </template>
      <template v-else>
        <div class="rounded-lg border border-border p-4 text-center">
          <p class="text-sm text-foreground">
            {{ singleFormatLabel }}
          </p>
          <p v-if="singleFormat === 'offline' && psychologist.offlineAddress" class="text-xs text-muted-foreground mt-1">
            {{ psychologist.offlineAddress }}
          </p>
        </div>
        <button
          type="button"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
          @click="goToStep('slot')"
        >
          Далее
        </button>
      </template>
    </div>

    <!-- Выбор дня и времени -->
    <div
      v-else-if="step === 'slot'"
      class="space-y-6"
    >
      <template v-if="hasBothFormats">
        <select
          v-model="format"
          class="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
        >
          <option
            v-if="psychologist.online.enabled"
            value="online"
          >
            Онлайн
          </option>
          <option
            v-if="psychologist.offline.enabled"
            value="offline"
          >
            Очно
          </option>
        </select>
        <p
          v-if="format === 'offline' && psychologist.offlineAddress"
          class="text-xs text-muted-foreground"
        >
          {{ psychologist.offlineAddress }}
        </p>
      </template>
      <template v-else>
        <div class="rounded-lg border border-border p-3 text-center">
          <p class="text-sm text-foreground">
            {{ singleFormatLabel }}
          </p>
          <p
            v-if="singleFormat === 'offline' && psychologist.offlineAddress"
            class="text-xs text-muted-foreground mt-1"
          >
            {{ psychologist.offlineAddress }}
          </p>
        </div>
      </template>

      <h3 class="text-lg font-bold text-foreground">
        {{ currentMonthName }}
      </h3>

      <!-- Скролл по дням -->
      <div
        v-if="loadingSlots"
        class="flex gap-2 overflow-x-auto pb-2"
      >
        <div
          v-for="i in 7"
          :key="i"
          class="shrink-0 w-14 h-16 rounded-lg flex items-center justify-center"
        >
          <div class="w-full h-full rounded-lg bg-muted animate-pulse" />
        </div>
      </div>
      <div
        v-else-if="!hasAvailableDays"
        class="rounded-lg border border-border p-4 text-center"
      >
        <p class="text-sm text-muted-foreground">
          Доступного времени записи нет
        </p>
      </div>
      <div
        v-else
        ref="daysScroller"
        class="flex gap-2 overflow-x-auto pb-2 cursor-grab active:cursor-grabbing select-none"
        style="scrollbar-width: none"
        @mousedown="onDaysMouseDown"
        @touchstart="onDaysTouchStart"
      >
        <div
          v-for="day in days"
          :key="day.date.toISOString()"
          class="shrink-0 w-14 h-16 rounded-lg flex flex-col items-center justify-center text-sm font-medium transition-colors"
          :class="dayButtonClasses(day.date, day.available)"
          @click="day.available && selectDate(day.date)"
        >
          <span class="text-xs">
            {{ shortDayName(day.date) }}
          </span>
          <span>{{ day.date.getDate() }}</span>
        </div>
      </div>

      <!-- Слоты времени -->
      <div
        v-if="selectedDate"
        class="grid grid-cols-3 gap-2"
      >
        <div
          v-if="loadingSlots"
          v-for="i in 6"
          :key="i"
          class="h-11 rounded-lg"
        >
          <div class="w-full h-full rounded-lg animate-pulse" />
        </div>
        <div
          v-else-if="timeSlots.length === 0"
          class="col-span-3 rounded-lg border border-border p-4 text-center"
        >
          <p class="text-sm text-muted-foreground">
            Нет доступного времени на этот день
          </p>
        </div>
        <button
          v-else
          v-for="slot in timeSlots"
          :key="slot.time"
          type="button"
          :disabled="!slot.available"
          class="h-11 rounded-lg text-sm font-medium transition-colors"
          :class="timeButtonClasses(slot)"
          @click="onTimeSelect(slot.time)"
        >
          {{ slot.time }}
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
          <RouterLink
            to="/personal-data-processing"
            class="text-primary hover:underline"
          >персональных данных</RouterLink>
        </span>
        <Toggle v-model="agreed" />
      </div>
      <button
        v-if="showStepButton"
        type="button"
        class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors w-full h-11"
        :class="canSubmit && !submitting ? 'bg-primary text-primary-foreground hover:bg-primary/90' : 'bg-muted text-muted-foreground cursor-not-allowed'"
        :disabled="!canSubmit || submitting"
        @click="createAppointment"
      >
        <template v-if="submitting">
          <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ submitButtonText }}
        </template>
        <template v-else>
          {{ submitButtonText }}
        </template>
      </button>
    </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterLink } from "vue-router";
import Toggle from "@/components/ui/Toggle.vue";
import PsychologistCard from "@/components/PsychologistCard.vue";
import type { Psychologist } from "@/lib/types";
import { getTimezones, getLocalTimezone } from "@/lib/utils";
import { useErrorStore } from "@/stores/error";

export default defineComponent({
  name: "UserBooking",
  components: {
    RouterLink,
    Toggle,
    PsychologistCard,
  },
  props: {
    psychologist: {
      type: Object as () => Psychologist,
      required: true,
    },
    step: {
      type: String as () => "format" | "slot" | "contact",
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
    editToken: {
      type: String,
      default: null,
    },
  },
  emits: ["update:step", "appointment-created"],
  data() {
    return {
      format: "online" as "online" | "offline",
      selectedDate: null as Date | null,
      selectedTime: null as string | null,
      clientName: "",
      clientEmail: "",
      agreed: false,
      clientTimezone: "",
      timezones: [] as string[],
      days: [] as { date: Date; available: boolean }[],
      timeSlots: [] as { time: string; available: boolean }[],
      availableSlotsByDate: {} as Record<string, { time: string; available: boolean }[]>,
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
      isDraggingDays: false,
      daysDragStartX: 0,
      daysDragScrollLeft: 0,
      loadingSlots: false,
      submitting: false,
    };
  },
  computed: {
    isEditMode(): boolean {
      return !!this.editToken;
    },
    hasBothFormats(): boolean {
      return !!(this.psychologist?.online?.enabled && this.psychologist?.offline?.enabled);
    },
    singleFormat(): "online" | "offline" | null {
      let hasOnline = this.psychologist?.online?.enabled;
      let hasOffline = this.psychologist?.offline?.enabled;
      if (hasOnline && hasOffline) {
        return null;
      }

      if (hasOnline) return "online";
      if (hasOffline) return "offline";
      
      return null;
    },
    singleFormatLabel(): string {
      if (this.singleFormat === "online") return "Встреча пройдёт онлайн";
      if (this.singleFormat === "offline") return "Встреча пройдёт очно";
      return "";
    },
    currentMonthName(): string {
      return this.months[this.currentMonthIndex];
    },
    canSubmit(): boolean {
      return !!(this.clientName && this.agreed);
    },
    submitButtonText(): string {
      return this.isEditMode ? "Перенести" : "Записаться";
    },

    hasAvailableDays(): boolean {
      return this.days.some(day => day.available);
    },
  },
  watch: {
    inputFormat(val: "online" | "offline" | undefined) {
      if (val !== undefined) {
        this.format = val;
      }
    },
    format() {
      this.loadAvailableSlots();
    },
    clientTimezone() {
      this.loadAvailableSlots();
    },
    psychologist: {
      handler() {
        if (this.inputFormat === undefined && this.singleFormat) {
          this.format = this.singleFormat;
        }
        this.loadAvailableSlots();
      },
      deep: true,
    },
  },
  created() {
    this.timezones = getTimezones();
    this.clientTimezone = getLocalTimezone();
    if (this.isEditMode) {
      this.loadExistingAppointment();
    }
    if (this.psychologist) {
      if (this.inputFormat !== undefined) {
        this.format = this.inputFormat;
      } else if (this.singleFormat && !this.isEditMode) {
        this.format = this.singleFormat;
        this.$emit("update:step", "slot");
      }
      this.loadAvailableSlots();
    }
  },
  methods: {
    async loadAvailableSlots() {
      if (!this.psychologist) return;
      if (this.loadingSlots) return;
      this.loadingSlots = true;
      const today = new Date();
      const dateFrom = today.toISOString().split("T")[0];
      const dateTo = new Date(today);
      dateTo.setDate(dateTo.getDate() + 14);
      const dateToStr = dateTo.toISOString().split("T")[0];
      
      const requestBody: Record<string, unknown> = {
        dateFrom,
        dateTo: dateToStr,
        format: this.format,
        clientTimezone: this.clientTimezone,
      };
      
      if (this.psychologist?.id) {
        requestBody.psychologistId = this.psychologist.id;
      } else if (this.psychologist) {
        requestBody.psychologist = {...this.psychologist, avatar: null};
      }
      
      try {
        const response = await fetch("/api/calendar/available", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        });
        
        if (!response.ok) {
          useErrorStore().showError("Не удалось загрузить расписание");
          return;
        }
        
        const data = await response.json();
        this.days = data.days.map((day: { date: string; available: boolean }) => ({
          date: new Date(day.date),
          available: day.available,
        }));
        
        this.availableSlotsByDate = {};
        data.days.forEach((day: { date: string; slots: { time: string; available: boolean }[] }) => {
          this.availableSlotsByDate[day.date] = day.slots.map((slot: { time: string; available: boolean }) => ({
            time: slot.time,
            available: slot.available,
          }));
        });
        
        if (this.selectedDate) {
          this.updateTimeSlotsFromState();
        } else {
          const firstAvailableDay = data.days.find((d: { available: boolean }) => d.available);
          if (firstAvailableDay) {
            this.selectedDate = new Date(firstAvailableDay.date);
            this.timeSlots = this.availableSlotsByDate[firstAvailableDay.date] || [];
          }
        }
      } catch (error) {
        useErrorStore().showError("Не удалось загрузить данные");
        console.error("Error loading available slots:", error);
      } finally {
        this.loadingSlots = false;
      }
    },
    selectFormat(fmt: "online" | "offline") {
      this.format = fmt;
      this.$emit("update:step", "slot");
      this.selectedDate = null;
      this.selectedTime = null;
    },
    goToStep(step: "format" | "slot" | "contact") {
      this.$emit("update:step", step);
    },
    async createAppointment() {
      if (!this.selectedDate || !this.selectedTime || !this.psychologist) return;
      this.submitting = true;
      
      const tzOffset = this.clientTimezone.match(/GMT([+-]\d+:\d+)/);
      const offset = tzOffset ? tzOffset[1] : "+03:00";
      const dateStr = this.selectedDate.toISOString().split("T")[0];
      const [hours, minutes] = this.selectedTime.split(":");
      const datetime = `${dateStr}T${hours}:${minutes}:00${offset}`;
      
      try {
        let url = "/api/appointments/";
        let requestBody: Record<string, unknown> = {
          psychologist_id: this.psychologist.id,
          client_name: this.clientName,
          datetime: datetime,
          format: this.format,
        };
        
        if (this.clientEmail) {
          requestBody.client_email = this.clientEmail;
        }
        
        if (this.isEditMode && this.editToken) {
          url = "/api/appointments/reschedule";
          requestBody = {
            edit_token: this.editToken,
            datetime: datetime,
            client_name: this.clientName,
            client_email: this.clientEmail || undefined,
            format: this.format,
          };
        }
        
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        });
        
        if (!response.ok) {
          try {
            const errorData = await response.json();
            if (errorData.detail && Array.isArray(errorData.detail) && errorData.detail[0]?.msg) {
              useErrorStore().showError(errorData.detail[0].msg);
            } else {
              useErrorStore().showError("Не удалось создать запись");
            }
          } catch {
            useErrorStore().showError("Не удалось создать запись");
          }
          this.submitting = false;
          return;
        }
        
        const data = await response.json();
        this.submitting = false;
        this.$emit("appointment-created", data);
      } catch (error) {
        this.submitting = false;
        useErrorStore().showError("Не удалось создать запись");
        console.error("Error creating appointment:", error);
      }
    },
    async loadExistingAppointment() {
      if (!this.editToken) return;
      
      try {
        const response = await fetch(
          `/api/appointments/event/${encodeURIComponent(this.editToken)}`
        );
        
        if (!response.ok) {
          useErrorStore().showError("Не удалось загрузить данные записи");
          return;
        }
        
        const data = await response.json();
        this.clientName = data.client_name || "";
        this.clientEmail = data.client_email || "";
      } catch (error) {
        useErrorStore().showError("Не удалось загрузить данные записи");
        console.error("Error loading existing appointment:", error);
      }
    },
    selectDate(date: Date) {
      this.selectedDate = date;
      this.selectedTime = null;
      this.updateTimeSlotsFromState();
    },
    onTimeSelect(time: string) {
      this.selectedTime = time;
      if (this.showStepButton) {
        this.goToStep("contact");
      }
    },
    updateTimeSlotsFromState() {
      if (!this.selectedDate) return;
      const dateStr = this.selectedDate.toISOString().split("T")[0];
      this.timeSlots = this.availableSlotsByDate[dateStr] || [];
    },
    shortDayName(date: Date): string {
      return this.dayNames[date.getDay()];
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
    timeButtonClasses(slot: { time: string; available: boolean }) {
      const isSelected = this.selectedTime === slot.time;
      if (isSelected) {
        return "bg-primary text-primary-foreground";
      }
      if (!slot.available) {
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
