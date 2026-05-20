<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header />
    <main class="flex-1 container mx-auto px-4 py-8 max-w-md mx-auto">
      <PsychologistCard
        :psychologist="psychologist"
        class="mb-6"
      />

      <div class="space-y-6">
        <div>
          <h2
            class="text-2xl font-bold text-center"
            :class="isExpired ? 'text-red-500' : 'text-foreground'"
          >
            {{ isExpired ? 'Встреча прошла' : 'Все получилось!' }}
          </h2>
          <h3 class="text-xl font-bold text-center" v-if="!isExpired">
            Вы записаны к психологу ✓
          </h3>
        </div>

        <p class="text-muted-foreground text-center text-sm">
          Информацию о встрече уже отправили на почту, ссылка для переноса записи так же там. Так же вы можете <a href="#" @click="rescheduleAgain">перенести встречу</a> при помощи ссылки ниже
        </p>
        <div class="rounded-xl border border-border p-4 space-y-2">
          <p
            v-if="selectedDate"
            class="font-medium text-foreground"
          >
            {{ selectedDate.getDate() }} {{ monthName(selectedDate) }},
            {{ fullDayName(selectedDate).toLowerCase() }}
          </p>
          <p class="text-foreground">
            {{ selectedTime }} — {{ endTime }}
          </p>
          <p class="text-sm text-muted-foreground">
            {{ format === 'online' ? 'Онлайн' : 'Очно' }}
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
          v-if="!isExpired"
          type="button"
          class="block text-sm text-primary hover:underline mx-auto"
          @click="rescheduleAgain"
        >
          Перенести запись
        </button>
        <button
          v-else
          type="button"
          class="block text-sm text-primary hover:underline mx-auto"
          @click="bookAgain"
        >
          Записаться заново
        </button>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import PsychologistCard from "@/components/PsychologistCard.vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import { usePsychologistStore } from "@/stores/psychologist";
import { useErrorStore } from "@/stores/error";
import { Copy } from "lucide-vue-next";

export default defineComponent({
  name: "BookingSuccessView",
  components: {
    Header,
    Footer,
    PsychologistCard,
    Copy,
  },
  data() {
    return {
      months: [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря",
      ] as string[],
      fullDayNames: [
        "Воскресенье", "Понедельник", "Вторник", "Среда",
        "Четверг", "Пятница", "Суббота",
      ] as string[],
      selectedDate: null as Date | null,
      selectedTime: null as string | null,
      format: "online" as "online" | "offline",
      loading: true,
    };
  },
  computed: {
    endTime(): string | null {
      if (!this.selectedTime) return null;
      const [hours, minutes] = this.selectedTime.split(":").map(Number);
      const endHours = hours + 1;
      return `${String(endHours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
    },
    isExpired(): boolean {
      if (!this.selectedDate || !this.selectedTime) return false;
      const [hours, minutes] = this.selectedTime.split(":");
      const appointmentDate = new Date(this.selectedDate);
      appointmentDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      return appointmentDate < new Date();
    },
    psychologist() {
      return usePsychologistStore().psychologist || {};
    },
    psychologistSlug(): string {
      return this.$route.params.psychologistSlug as string || "";
    },
    editToken(): string {
      return this.$route.params.editToken as string || "";
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
  },
  async created() {
    await this.loadPsychologist();
    await this.loadAppointmentData();
  },
  methods: {
    async loadPsychologist() {
      const slug = this.psychologistSlug;
      if (!slug) return;
      await usePsychologistStore().loadBySlug(slug);
    },
    async loadAppointmentData() {
      if (!this.editToken) {
        this.loading = false;
        return;
      }

      try {
        const response = await fetch(
          `/api/appointments/event/${encodeURIComponent(this.editToken)}`
        );
        
        if (!response.ok) {
          useErrorStore().showError("Не удалось загрузить данные записи");
          this.loading = false;
          return;
        }
        
        const data = await response.json();
        if (data.datetime) {
          const dt = new Date(data.datetime);
          this.selectedDate = dt;
          this.selectedTime = `${String(dt.getHours()).padStart(2, "0")}:${String(dt.getMinutes()).padStart(2, "0")}`;
        }
      } catch (error) {
        useErrorStore().showError("Не удалось загрузить данные записи");
      }
      this.loading = false;
    },
    rescheduleAgain() {
      if (this.editToken) {
        this.$router.push({
          name: `booking-edit`,
          params: { psychologistSlug: this.psychologistSlug, editToken: this.editToken },
        });
      }
    },
    bookAgain() {
      this.$router.push({
        name: `booking`,
        params: { psychologistSlug: this.psychologistSlug },
      });
    },
    monthName(date: Date): string {
      return this.months[date.getMonth()];
    },
    fullDayName(date: Date): string {
      return this.fullDayNames[date.getDay()];
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
