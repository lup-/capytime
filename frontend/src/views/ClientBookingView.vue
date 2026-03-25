<template>
  <div class="min-h-screen bg-background flex flex-col">
    <button
      v-if="currentStep !== 'format' && currentStep !== 'success'"
      type="button"
      class="fixed top-4 left-4 z-50 w-10 h-10 rounded-lg bg-card border border-border flex items-center justify-center text-foreground hover:bg-secondary transition-colors"
      @click="goBack"
    >
      ←
    </button>

    <main class="flex-1 container mx-auto px-4 py-8">
      <UserBooking
        :psychologist="psychologist"
        :step="currentStep"
        @update:step="(val) => navigateTo(val)"
      />
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import UserBooking from "@/components/UserBooking.vue";
import type { Psychologist } from "@/stores/onboarding";

const BOOKING_STEPS = ["format", "slot", "contact", "success"] as const;
type BookingStep = typeof BOOKING_STEPS[number];

export default defineComponent({
  name: "ClientBookingView",
  components: {
    UserBooking,
  },
  data() {
    return {
      psychologist: {
        name: "Анна Петрова",
        specialty: "Психолог",
        avatar: null as string | null,
        onlineEnabled: true,
        offlineEnabled: true,
        onlinePrice: "4000",
        offlinePrice: "5000",
        offlineAddress: "м. Курская, ул. Ленина, д.5",
        workDaysOnline: [0, 1, 2, 3, 4] as number[],
        workDaysOffline: [0, 1, 2, 3, 4] as number[],
        workFromOnline: "10:00",
        workToOnline: "19:00",
        workFromOffline: "14:00",
        workToOffline: "20:00",
        slotDurationOnline: 90,
        slotDurationOffline: 60,
        timezone: "(UTC +03:00) Москва",
        videoLink: "Телемост",
      } as Psychologist,
    };
  },
  computed: {
    currentStep(): BookingStep {
      const name = this.$route.name as string | undefined;
      const match = name?.match(/^booking-(.+)$/);
      const step = match ? match[1] : undefined;
      if (step && BOOKING_STEPS.includes(step as BookingStep)) {
        return step as BookingStep;
      }
      return "format";
    },
  },
  watch: {
    "$route.name"(): void {},
  },
  created() {
    if (typeof window !== "undefined") {
      const saved = window.localStorage.getItem("capytimeAvatar");
      if (saved) {
        this.psychologist.avatar = saved;
      }
    }
  },
  methods: {
    navigateTo(step: BookingStep) {
      this.$router.push({ name: `booking-${step}` });
    },
    goBack() {
      const idx = BOOKING_STEPS.indexOf(this.currentStep);
      if (idx > 0) {
        const prev = BOOKING_STEPS[idx - 1];
        this.$router.push({ name: `booking-${prev}` });
      }
    },
  },
});
</script>
