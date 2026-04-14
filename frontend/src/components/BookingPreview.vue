<template>
  <p class="text-sm font-medium text-foreground mb-3 mt-12">
    Превью страницы записи
  </p>
  <div
    v-if="store.firstName"
    class="rounded-xl border border-border p-4"
  >
    <template v-if="step === 'online' || step === 'offline'">
      <UserBooking
        :psychologist="store.psychologist"
        step="slot"
        :input-format="step"
        :show-step-button="false"
      />
    </template>
    <template v-else>
      <PsychologistCard :psychologist="store.psychologist" />
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import PsychologistCard from "@/components/PsychologistCard.vue";
import UserBooking from "@/components/UserBooking.vue";
import { useOnboardingStore } from "@/stores/onboarding";

export default defineComponent({
  name: "BookingPreview",
  components: {
    PsychologistCard,
    UserBooking,
  },
  props: {
    step: {
      type: String,
      default: null,
    },
  },
  computed: {
    store(): ReturnType<typeof useOnboardingStore> {
      return useOnboardingStore();
    },
  },
});
</script>
