<template>
  <div class="w-full border-b border-border bg-background">
    <div
      ref="scrollRef"
      class="flex gap-1 overflow-x-auto px-4 py-3 scrollbar-hide"
      style="scrollbar-width: none; ms-overflow-style: none"
    >
      <button
        v-for="step in visibleSteps"
        :key="step.id"
        :ref="step.id === currentStep ? 'activeRef' : null"
        type="button"
        :disabled="!calendarConnected && step.id !== 'calendar'"
        @click="handleStepClick(step.id)"
        class="shrink-0 rounded-sm px-3 py-1.5 text-xs font-medium transition-colors"
        :class="buttonClasses(step)"
      >
        {{ step.label }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType, ref, computed, watch, onMounted, nextTick } from "vue";

interface StepItem {
  id: string;
  label: string;
  hidden?: boolean;
}

export default defineComponent({
  name: "OnboardingNav",
  props: {
    steps: {
      type: Array as PropType<StepItem[]>,
      required: true,
    },
    currentStep: {
      type: String,
      required: true,
    },
    completedSteps: {
      type: Array as PropType<string[]>,
      required: true,
    },
    calendarConnected: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:currentStep"],
  setup(props, { emit }) {
    const scrollRef = ref<HTMLDivElement | null>(null);
    const activeRef = ref<HTMLButtonElement | null>(null);

    const visibleSteps = computed(() => props.steps.filter((s) => !s.hidden));

    const scrollToActive = () => {
      if (!scrollRef.value || !activeRef.value) return;
      const container = scrollRef.value;
      const el = activeRef.value;
      const scrollLeft = el.offsetLeft - container.offsetWidth / 2 + el.offsetWidth / 2;
      container.scrollTo({ left: scrollLeft, behavior: "smooth" });
    };

    const handleStepClick = (stepId: string) => {
      if (!props.calendarConnected && stepId !== "calendar") {
        return;
      }
      emit("update:currentStep", stepId);
    };

    const buttonClasses = (step: StepItem) => {
      const isActive = step.id === props.currentStep;
      const isCompleted = props.completedSteps.includes(step.id);
      const isDisabled = !props.calendarConnected && step.id !== "calendar";

      return [
        isActive && "bg-foreground text-background",
        isCompleted && !isActive && "bg-primary/10 text-primary",
        !isActive && !isCompleted && !isDisabled && "text-muted-foreground hover:bg-secondary",
        isDisabled && "text-muted-foreground/50 cursor-not-allowed",
      ]
        .filter(Boolean)
        .join(" ");
    };

    watch(
      () => props.currentStep,
      async () => {
        await nextTick();
        scrollToActive();
      }
    );

    onMounted(() => {
      scrollToActive();
    });

    return {
      scrollRef,
      activeRef,
      visibleSteps,
      handleStepClick,
      buttonClasses,
    };
  },
});
</script>

