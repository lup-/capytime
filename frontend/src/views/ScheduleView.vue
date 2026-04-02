<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header />

    <main class="flex-1 container mx-auto px-4 py-8">
      <div class="max-w-md mx-auto space-y-6">
        <!-- Навигация по датам -->
        <div class="flex items-center justify-between">
          <button
            type="button"
            class="w-10 h-10 rounded-lg border border-border flex items-center justify-center text-foreground hover:bg-secondary"
            @click="changeDate(-1)"
          >
            ‹
          </button>
          <div class="text-center">
            <p class="text-lg font-bold text-foreground">
              {{ formattedDate }}
            </p>
            <p class="text-sm text-muted-foreground">
              {{ dayName }}
            </p>
          </div>
          <button
            type="button"
            class="w-10 h-10 rounded-lg border border-border flex items-center justify-center text-foreground hover:bg-secondary"
            @click="changeDate(1)"
          >
            ›
          </button>
        </div>

        <p
          v-if="isToday"
          class="text-sm text-muted-foreground text-center"
        >
          Сейчас {{ currentTimeStr }}
        </p>

        <!-- Список встреч -->
        <div class="space-y-3">
          <p
            v-if="meetings.length === 0"
            class="text-center text-muted-foreground py-12"
          >
            Нет записей на этот день
          </p>
          <div
            v-else
            v-for="meeting in meetings"
            :key="meeting.id"
            class="rounded-xl border p-4 space-y-2 transition-colors"
            :class="meetingClasses(meeting)"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-foreground">
                  {{ meeting.time }} – {{ meeting.endTime }}
                </p>
                <p class="text-sm text-foreground">
                  {{ meeting.client }}
                </p>
                <p class="text-xs text-muted-foreground">
                  {{ meeting.format === 'online' ? 'Онлайн' : 'Очно' }}
                </p>
              </div>
              <div class="flex gap-2">
                <button
                  type="button"
                  class="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:text-primary hover:border-primary"
                >
                  ✎
                </button>
                <button
                  type="button"
                  class="h-8 px-3 rounded-lg text-xs font-medium transition-colors flex items-center gap-1"
                  :class="meeting.paid ? 'bg-primary/10 text-primary' : 'border border-border text-muted-foreground hover:border-primary hover:text-primary'"
                  @click="togglePaid(meeting.id)"
                >
                  <span v-if="meeting.paid">✓</span>
                  {{ meeting.paid ? "Оплачено" : "Оплата" }}
                </button>
              </div>
            </div>
            <span
              v-if="isCurrentMeeting(meeting)"
              class="inline-block text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded"
            >
              Сейчас
            </span>
            <span
              v-else-if="isNextMeeting(meeting)"
              class="inline-block text-xs bg-primary/20 text-primary px-2 py-0.5 rounded"
            >
              Следующая
            </span>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
  name: "ScheduleView",
  components: {
    Header,
    Footer,
  },
  data() {
    const now = new Date();
    return {
      selectedDate: now,
      meetings: [
        { id: "1", time: "10:00", endTime: "11:00", client: "Иван С.", format: "online", paid: true },
        { id: "2", time: "11:30", endTime: "12:30", client: "Мария К.", format: "offline", paid: false },
        { id: "3", time: "14:00", endTime: "15:00", client: "Алексей П.", format: "online", paid: false },
        { id: "4", time: "16:00", endTime: "17:00", client: "Елена В.", format: "online", paid: true },
      ] as Array<{
        id: string;
        time: string;
        endTime: string;
        client: string;
        format: "online" | "offline";
        paid: boolean;
      }>,
      dayNames: [
        "Воскресенье",
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
      ] as string[],
      months: [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
      ] as string[],
    };
  },
  computed: {
    now(): Date {
      return new Date();
    },
    currentTimeStr(): string {
      const h = String(this.now.getHours()).padStart(2, "0");
      const m = String(this.now.getMinutes()).padStart(2, "0");
      return `${h}:${m}`;
    },
    isToday(): boolean {
      const today = new Date();
      return this.selectedDate.toDateString() === today.toDateString();
    },
    formattedDate(): string {
      return `${this.selectedDate.getDate()} ${this.months[this.selectedDate.getMonth()]}`;
    },
    dayName(): string {
      return this.dayNames[this.selectedDate.getDay()];
    },
    currentMeeting() {
      if (!this.isToday) return undefined;
      return this.meetings.find((m) => m.time <= this.currentTimeStr && m.endTime > this.currentTimeStr);
    },
    nextMeeting() {
      if (!this.isToday) return undefined;
      return this.meetings.find((m) => m.time > this.currentTimeStr);
    },
  },
  methods: {
    changeDate(delta: number) {
      const d = new Date(this.selectedDate);
      d.setDate(d.getDate() + delta);
      this.selectedDate = d;
    },
    togglePaid(id: string) {
      this.meetings = this.meetings.map((m) => (m.id === id ? { ...m, paid: !m.paid } : m));
    },
    isCurrentMeeting(meeting: { id: string }) {
      return this.currentMeeting && this.currentMeeting.id === meeting.id;
    },
    isNextMeeting(meeting: { id: string }) {
      return this.nextMeeting && this.nextMeeting.id === meeting.id;
    },
    meetingClasses(meeting: { id: string; paid: boolean }) {
      const classes: string[] = [];
      if (meeting.paid) {
        classes.push("bg-primary/5", "border-primary/20");
      }
      if (this.isCurrentMeeting(meeting)) {
        classes.push("ring-2", "ring-primary");
      } else if (this.isNextMeeting(meeting)) {
        classes.push("ring-2", "ring-primary/40");
      } else {
        classes.push("border-border");
      }
      return classes.join(" ");
    },
  },
});
</script>

