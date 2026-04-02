<template>
  <div class="min-h-screen bg-background flex flex-col">
    <template v-if="notFound">
      <NotFoundView :message="notFoundMessage" />
    </template>

    <template v-else>
      <Header>
        <template #left>
          <button
            v-if="currentStep !== 'format' && currentStep !== 'success'"
            type="button"
            class="w-10 h-10 rounded-lg bg-card border border-border flex items-center justify-center text-foreground hover:bg-secondary transition-colors"
            @click="goBack"
          >
            ←
          </button>
        </template>
      </Header>

      <main class="flex-1 container mx-auto px-4 py-8" v-if="psychologist">
        <UserBooking
          :psychologist="psychologist"
          :step="currentStep"
          @update:step="(val) => navigateTo(val)"
        />
      </main>

      <Footer />
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import UserBooking from "@/components/UserBooking.vue";
import NotFoundView from "@/views/NotFoundView.vue";
import { usePsychologistStore } from "@/stores/psychologist";

const BOOKING_STEPS = ["format", "slot", "contact", "success"] as const;
type BookingStep = typeof BOOKING_STEPS[number];

export default defineComponent({
  name: "ClientBookingView",
  components: {
    Header,
    Footer,
    UserBooking,
    NotFoundView,
  },
  setup() {
    const psychologistStore = usePsychologistStore();
    return { psychologistStore };
  },
  data() {
    return {
      notFound: false,
      notFoundMessage: "Психолог не найден",
    };
  },
  computed: {
    psychologist() {
      return this.psychologistStore.psychologist;
    },
    psychologistSlug(): string {
      return this.$route.params.psychologistSlug as string || "";
    },
    isValidStep(): boolean {
      const name = this.$route.name as string | undefined;
      if (name === "booking") return true;
      const match = name?.match(/^booking-(.+)$/);
      const step = match ? match[1] : undefined;
      return !!(step && BOOKING_STEPS.includes(step as BookingStep));
    },
    currentStep(): BookingStep {
      const name = this.$route.name as string | undefined;
      if (name === "booking") {
        const p = this.psychologist;
        const hasOnline = p?.online?.enabled;
        const hasOffline = p?.offline?.enabled;
        if (!hasOnline || !hasOffline) return "slot";
        return "format";
      }
      const match = name?.match(/^booking-(.+)$/);
      const step = match ? match[1] : undefined;
      if (step && BOOKING_STEPS.includes(step as BookingStep)) {
        return step as BookingStep;
      }
      return "format";
    },
  },
  watch: {
    "$route.params.psychologistSlug": {
      handler() {
        this.loadBySlug();
      },
      immediate: true,
    },
    "$route.name": {
      handler() {
        if (!this.isValidStep) {
          this.notFound = true;
          this.notFoundMessage = "Страница не найдена";
        }
      },
      immediate: true,
    },
  },
  created() {
    this.loadBySlug();
  },
  methods: {
    async loadBySlug() {
      this.notFound = false;
      const slug = this.psychologistSlug;
      if (!slug) {
        this.notFound = true;
        this.notFoundMessage = "Страница не найдена";
        return;
      }
      const result = await this.psychologistStore.loadBySlug(slug);
      if (!result) {
        this.notFound = true;
        this.notFoundMessage = "Психолог не найден";
      }
    },
    navigateTo(step: BookingStep) {
      this.$router.push({ name: `booking-${step}`, params: { psychologistSlug: this.psychologistSlug } });
    },
    goBack() {
      const idx = BOOKING_STEPS.indexOf(this.currentStep);
      if (idx > 0) {
        const prev = BOOKING_STEPS[idx - 1];
        this.$router.push({ name: `booking-${prev}`, params: { psychologistSlug: this.psychologistSlug } });
      }
    },
  },
});
</script>
