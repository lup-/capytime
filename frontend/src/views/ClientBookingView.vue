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
          <button
            v-else-if="editToken"
            type="button"
            class="w-10 h-10 rounded-lg bg-card border border-border flex items-center justify-center text-foreground hover:bg-secondary transition-colors"
            @click="goHome"
          >
            ←
          </button>
        </template>
      </Header>

      <main class="flex-1 container mx-auto px-4 py-8" v-if="psychologist">
        <UserBooking
          :psychologist="psychologist"
          :step="currentStep"
          :edit-token="editToken"
          @update:step="(val, data) => navigateTo(val, data)"
          @appointment-created="onAppointmentCreated"
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
    editToken(): string | null {
      return this.$route.params.editToken as string || null;
    },
    isEditMode(): boolean {
      return !!this.editToken;
    },
    isValidStep(): boolean {
      const name = this.$route.name as string | undefined;
      if (name === "booking") return true;
      if (name === "booking-edit") return true;
      if (name === "booking-success") return true;
      const match = name?.match(/^booking-(format|slot|contact)$/);
      return !!match;
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
      if (name === "booking-format") return "format";
      if (name === "booking-slot") return "slot";
      if (name === "booking-contact") return "contact";
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
    navigateTo(step: BookingStep, data?: any) {
      if (step === "success") {
        const token = data?.edit_token || this.editToken;
        this.$router.push({
          name: `booking-success`,
          params: { psychologistSlug: this.psychologistSlug, editToken: token },
        });
      } else {
        const routeName = `booking-${step}`;
        const params: Record<string, string> = { psychologistSlug: this.psychologistSlug };
        if (this.isEditMode) {
          params.editToken = this.editToken;
        }
        this.$router.push({ name: routeName, params });
      }
    },
    goBack() {
      const idx = BOOKING_STEPS.indexOf(this.currentStep);
      if (idx > 0) {
        const prev = BOOKING_STEPS[idx - 1];
        const params: Record<string, string> = { psychologistSlug: this.psychologistSlug };
        if (this.editToken) {
          params.editToken = this.editToken;
        }
        this.$router.push({ name: `booking-${prev}`, params });
      }
    },
    goHome() {
      this.$router.push({ name: "home" });
    },
    onAppointmentCreated(data: any) {
      this.$router.push({
        name: `booking-success`,
        params: { psychologistSlug: this.psychologistSlug, editToken: data.edit_token },
      });
    },
  },
});
</script>
