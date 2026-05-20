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
        {{ psychologist.firstName?.[0] || "" }}
      </template>
    </div>
    <div class="text-center">
      <p class="font-medium text-foreground">
        {{ fullName }}
      </p>
      <p class="text-xs text-muted-foreground mb-2">
        Психолог
      </p>
      <p
        v-if="psychologist.specialty"
        class="text-xs text-muted-foreground"
      >
        {{ psychologist.specialty }}
      </p>
      <div
        v-if="psychologist.problems?.length"
        class="flex flex-wrap gap-1 justify-center mt-1"
      >
        <span
          v-for="problem in psychologist.problems"
          :key="problem"
          class="text-[10px] bg-secondary text-muted-foreground px-1.5 py-0.5 rounded"
        >
          {{ problem }}
        </span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from "vue";
import type { Psychologist } from "@/lib/types";

export default defineComponent({
  name: "PsychologistCard",
  props: {
    psychologist: {
      type: Object as () => Psychologist,
      required: true,
    },
  },
  setup(props) {
    const fullName = computed(() => {
      const first = props.psychologist.firstName || "";
      const last = props.psychologist.lastName || "";
      return [first, last].filter(Boolean).join(" ");
    });
    return { fullName };
  },
});
</script>
