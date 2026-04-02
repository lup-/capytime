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
        class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors w-full h-11"
        :class="canSubmit ? 'bg-primary text-primary-foreground hover:bg-primary/90' : 'bg-muted text-muted-foreground cursor-not-allowed'"
        :disabled="!canSubmit"
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
        Информация о встрече направлена на почту.
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
        <p class="text-sm text-muted-foreground">
          {{ format === 'online' ? 'Онлайн' : 'Очно' }}
        </p>
        <p v-if="priceText" class="text-foreground">
          {{ priceText }}
        </p>
        <div
          v-if="format === 'online' && psychologist.videoLink"
          class="flex items-start gap-2 flex-col"
        >
          <span class="text-sm text-muted-foreground">Ссылка на встречу:</span>
          <div class="flex gap-2 w-full items-center">
            <a
              :href="psychologist.videoLink"
              target="_blank"
              class="text-primary text-sm hover:underline"
            >
              {{ psychologist.videoLink }}
            </a>
            <button
              type="button"
              class="text-muted-foreground hover:text-foreground"
              @click="copyVideoLink"
            >
              <Copy class="w-4 h-4" />
            </button>
          </div>
        </div>
        <p
          v-else-if="format === 'offline' && psychologist.offlineAddress"
          class="text-sm text-muted-foreground"
        >
          {{ psychologist.offlineAddress }}
        </p>
      </div>
      <div class="flex gap-2">
        <a
          :href="yandexCalendarUrl"
          target="_blank"
          class="inline-flex items-center justify-center whitespace-normal text-center rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 flex-1 py-2 px-4"
        >
          Добавить в Яндекс.Календарь
        </a>
        <a
          :href="googleCalendarUrl"
          target="_blank"
          class="inline-flex items-center justify-center whitespace-normal text-center rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 flex-1 py-2 px-4"
        >
          Добавить в Google&nbsp;Календарь
        </a>
      </div>
      <a
        :href="icsDownloadUrl"
        download="appointment.ics"
        class="block text-xs text-muted-foreground text-center hover:text-foreground"
      >
        Скачать .ics файл
      </a>
      <button
        type="button"
        class="block text-sm text-primary hover:underline mx-auto"
        @click="resetBooking"
      >
        Записаться заново
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Toggle from "@/components/ui/Toggle.vue";
import PsychologistCard from "@/components/PsychologistCard.vue";
import type { Psychologist } from "@/lib/types";
import { getTimezones, getLocalTimezone } from "@/lib/utils";
import { useErrorStore } from "@/stores/error";
import { Copy } from "lucide-vue-next";

export default defineComponent({
  name: "UserBooking",
  components: {
    Toggle,
    PsychologistCard,
    Copy,
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
      loadingSlots: false,
    };
  },
  computed: {
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
    hasAvailableDays(): boolean {
      return this.days.some(day => day.available);
    },
    priceText(): string {
      const format = this.format === "online" 
        ? this.psychologist?.online 
        : this.psychologist?.offline;
      if (format?.price) {
        const price = parseInt(format.price);
        const duration = format.slotDuration || 60;
        const totalPrice = (price * duration) / 60;
        return `${totalPrice} ₽`;
      }
      return "";
    },
    icsDownloadUrl(): string {
      if (!this.selectedDate || !this.selectedTime) return "#";
      const [hours, minutes] = this.selectedTime.split(":");
      const startDate = new Date(this.selectedDate);
      startDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      const endDate = new Date(startDate);
      endDate.setHours(endDate.getHours() + 1);
      
      const formatDate = (d: Date) => {
        return d.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
      };
      
      const start = formatDate(startDate);
      const end = formatDate(endDate);
      const now = formatDate(new Date());
      
      let description = "Консультация с психологом";
      if (this.format === "online" && this.psychologist?.videoLink) {
        description += `\nСсылка на встречу: ${this.psychologist.videoLink}`;
      }
      
      const ics = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CapyTime//Booking//RU
BEGIN:VEVENT
UID:${Date.now()}@capytime
DTSTAMP:${now}
DTSTART:${start}
DTEND:${end}
SUMMARY:Психолог
DESCRIPTION:${description}
END:VEVENT
END:VCALENDAR`;
      
      const blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
      return URL.createObjectURL(blob);
    },
    yandexCalendarUrl(): string {
      if (!this.selectedDate || !this.selectedTime) return "#";
      const [hours, minutes] = this.selectedTime.split(":");
      const startDate = new Date(this.selectedDate);
      startDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      const endDate = new Date(startDate);
      endDate.setHours(endDate.getHours() + 1);
      
      const formatDateLocal = (d: Date) => {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, "0");
        const day = String(d.getDate()).padStart(2, "0");
        const h = String(d.getHours()).padStart(2, "0");
        const m = String(d.getMinutes()).padStart(2, "0");
        const s = String(d.getSeconds()).padStart(2, "0");
        return `${year}${month}${day}T${h}${m}${s}`;
      };
      
      const title = "Психолог";
      let desc = "Консультация с психологом";
      let place = "";
      
      if (this.format === "online" && this.psychologist?.videoLink) {
        desc += `\nСсылка на встречу: ${this.psychologist.videoLink}`;
      } else if (this.format === "offline" && this.psychologist?.offlineAddress) {
        place = this.psychologist.offlineAddress;
      }
      
      const params = new URLSearchParams({
        name: title,
        description: desc,
        startTs: formatDateLocal(startDate),
        endTs: formatDateLocal(endDate),
      });
      
      if (place) {
        params.append("location", place);
      }
      
      return `https://calendar.yandex.ru/event?${params.toString()}`;
    },
    googleCalendarUrl(): string {
      if (!this.selectedDate || !this.selectedTime) return "#";
      const [hours, minutes] = this.selectedTime.split(":");
      const startDate = new Date(this.selectedDate);
      startDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      const endDate = new Date(startDate);
      endDate.setHours(endDate.getHours() + 1);
      
      const formatDate = (d: Date) => {
        return d.toISOString().replace(/-/g, "").replace(/:/g, "");
      };
      
      const title = "Психолог";
      let desc = "Консультация с психологом";
      let location = "";
      
      if (this.format === "online" && this.psychologist?.videoLink) {
        desc += `\nСсылка на встречу: ${this.psychologist.videoLink}`;
      } else if (this.format === "offline" && this.psychologist?.offlineAddress) {
        location = this.psychologist.offlineAddress;
      }
      
      const params = new URLSearchParams({
        action: "TEMPLATE",
        text: title,
        dates: `${formatDate(startDate)}/${formatDate(endDate)}`,
        details: desc,
      });
      
      if (location) {
        params.append("location", location);
      }
      
      return `https://calendar.google.com/calendar/render?${params.toString()}`;
    },
  },
  watch: {
    step(val) {
      if (val === "success") {
        this.loadFromStorage();
      }
    },
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
    this.loadFromStorage();
    if (this.psychologist) {
      if (this.inputFormat !== undefined) {
        this.format = this.inputFormat;
      } else if (this.singleFormat) {
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
    goToStep(step: "format" | "slot" | "contact" | "success") {
      if (step === "success" && this.showStepButton) {
        this.createAppointment();
      } else {
        this.$emit("update:step", step);
      }
    },
    async createAppointment() {
      if (!this.selectedDate || !this.selectedTime || !this.psychologist) return;
      
      const tzOffset = this.clientTimezone.match(/GMT([+-]\d+:\d+)/);
      const offset = tzOffset ? tzOffset[1] : "+03:00";
      const dateStr = this.selectedDate.toISOString().split("T")[0];
      const [hours, minutes] = this.selectedTime.split(":");
      const datetime = `${dateStr}T${hours}:${minutes}:00${offset}`;
      
      const requestBody: Record<string, unknown> = {
        psychologist_id: this.psychologist.id,
        client_name: this.clientName,
        datetime: datetime,
      };
      
      if (this.clientEmail) {
        requestBody.client_email = this.clientEmail;
      }
      
      try {
        const response = await fetch("/api/appointments/", {
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
          return;
        }
        
        this.$emit("update:step", "success");
        this.saveToStorage();
      } catch (error) {
        useErrorStore().showError("Не удалось создать запись");
        console.error("Error creating appointment:", error);
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
    addToGoogleCalendar() {
      window.open(this.googleCalendarUrl, "_blank");
    },
    saveToStorage() {
      const data = {
        format: this.format,
        selectedDate: this.selectedDate ? this.selectedDate.toISOString() : null,
        selectedTime: this.selectedTime,
        psychologistId: this.psychologist?.id,
      };
      localStorage.setItem("booking_success_data", JSON.stringify(data));
    },
    loadFromStorage() {
      if (this.step !== "success") return;
      const stored = localStorage.getItem("booking_success_data");
      if (!stored) return;
      try {
        const data = JSON.parse(stored);
        if (data.psychologistId === this.psychologist?.id) {
          if (data.selectedDate) {
            this.selectedDate = new Date(data.selectedDate);
          }
          if (data.selectedTime) {
            this.selectedTime = data.selectedTime;
          }
          if (data.format) {
            this.format = data.format;
          }
        }
      } catch {
        // ignore parse errors
      }
    },
    resetBooking() {
      localStorage.removeItem("booking_success_data");
      this.selectedDate = null;
      this.selectedTime = null;
      this.$emit("update:step", "format");
    },
    copyVideoLink() {
      if (this.psychologist?.videoLink) {
        navigator.clipboard.writeText(this.psychologist.videoLink);
        useErrorStore().showSuccess("Скопировано!");
      }
    },
  },
});
</script>
