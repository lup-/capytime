<template>
  <div class="flex flex-col items-center gap-3">
    <div class="w-16 h-16 rounded-full bg-secondary flex items-center justify-center text-xl font-bold text-foreground overflow-hidden">
      <template v-if="psychologist.avatar">
        <img
          :src="psychologist.avatar"
          alt="Аватар"
          class="w-full h-full object-cover"
        />
      </template>
      <template v-else>
        {{ psychologist.name[0] }}
      </template>
    </div>
    <div class="text-center">
      <p class="font-medium text-foreground">
        {{ psychologist.name }}
      </p>
      <p
        v-if="psychologist.specialty"
        class="text-xs text-muted-foreground"
      >
        {{ psychologist.specialty }}
      </p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import type { Psychologist } from "@/stores/onboarding";

export default defineComponent({
  name: "PsychologistCard",
  props: {
    psychologist: {
      type: Object as () => Psychologist,
      required: true,
    },
  },
});
</script>
