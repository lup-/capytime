<template>
  <div
    class="relative"
    @click.stop
  >
    <div
      class="min-h-9 rounded-md border border-input bg-background px-3 py-1 cursor-pointer flex flex-wrap gap-1 items-center"
      :class="{ 'ring-2 ring-ring ring-offset-2': isOpen }"
    >
      <template v-if="modelValue.length > 0">
        <span
          v-for="label in modelValue"
          :key="label"
          class="inline-flex items-center gap-1 bg-secondary text-secondary-foreground text-sm rounded px-2 py-0.5"
        >
          {{ label }}
          <button
            type="button"
            class="hover:text-destructive"
            @click.stop="removeOption(label)"
          >
            ✕
          </button>
        </span>
      </template>
      <input
        ref="inputRef"
        v-model="searchText"
        type="text"
        :placeholder="modelValue.length === 0 ? placeholder : ''"
        class="flex-1 min-w-[100px] bg-transparent outline-none text-sm"
        @click.stop="toggle"
        @keydown.enter.prevent="addCustomOption"
        @keydown.backspace="handleBackspace"
      />
    </div>

    <div
      v-if="isOpen"
      class="absolute z-50 w-full mt-1 rounded-md border border-border bg-background shadow-lg max-h-60 overflow-auto"
    >
      <button
        v-for="option in filteredOptions"
        :key="getLabel(option)"
        type="button"
        class="w-full px-3 py-2 text-left text-sm hover:bg-accent flex items-center gap-2"
        @click="toggleOption(option)"
      >
        <span
          class="w-4 h-4 rounded border flex items-center justify-center"
          :class="isSelected(getLabel(option)) ? 'bg-primary border-primary text-primary-foreground' : 'border-input'"
        >
          <span v-if="isSelected(getLabel(option))">✓</span>
        </span>
        {{ getLabel(option) }}
      </button>
      <div
        v-if="searchText && !hasExactMatch"
        class="px-3 py-2 text-sm text-muted-foreground border-t"
      >
        Нажмите Enter, чтобы добавить "{{ searchText }}"
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "MultiSelect",
  props: {
    modelValue: {
      type: Array,
      default: () => [],
    },
    options: {
      type: Array,
      required: true,
    },
    labelKey: {
      type: String,
      default: "label",
    },
    valueKey: {
      type: String,
      default: "value",
    },
    placeholder: {
      type: String,
      default: "Выберите...",
    },
  },
  emits: ["update:modelValue"],
  data() {
    return {
      isOpen: false,
      searchText: "",
    };
  },
  computed: {
    filteredOptions(): unknown[] {
      if (!this.searchText) return this.options;
      const query = this.searchText.toLowerCase();
      return this.options.filter((opt) =>
        String(this.getLabel(opt)).toLowerCase().includes(query)
      );
    },
    hasExactMatch(): boolean {
      if (!this.searchText) return false;
      const query = this.searchText.toLowerCase();
      return this.options.some((opt) =>
        String(this.getLabel(opt)).toLowerCase() === query
      );
    },
  },
  methods: {
    toggle() {
      this.isOpen = !this.isOpen;
    },
    close() {
      this.isOpen = false;
      this.searchText = "";
      (this.$refs.inputRef as HTMLInputElement).blur();
    },
    getLabel(option: unknown): string {
      if (typeof option === "string") return option;
      return (option as Record<string, unknown>)[this.labelKey] as string;
    },
    isSelected(label: string): boolean {
      return this.modelValue.some((v) => v.toLowerCase() === label.toLowerCase());
    },
    toggleOption(option: unknown) {
      const label = this.getLabel(option);
      const current = [...this.modelValue];
      const idx = current.findIndex((v) => v.toLowerCase() === label.toLowerCase());

      if (idx >= 0) {
        current.splice(idx, 1);
      } else {
        current.push(label);
      }

      this.$emit("update:modelValue", current);
    },
    addCustomOption() {
      if (!this.searchText.trim()) return;

      const current = [...this.modelValue];
      const newOption = this.searchText.trim();

      if (!current.some((v) => v.toLowerCase() === newOption.toLowerCase())) {
        current.push(newOption);
        this.$emit("update:modelValue", current);
      }

      this.searchText = "";
    },
    removeOption(label: string) {
      const current = [...this.modelValue];
      const idx = current.findIndex((v) => v.toLowerCase() === label.toLowerCase());

      if (idx >= 0) {
        current.splice(idx, 1);
        this.$emit("update:modelValue", current);
      }
    },
    handleBackspace() {
      if (this.searchText === "" && this.modelValue.length > 0) {
        const current = [...this.modelValue];
        current.pop();
        this.$emit("update:modelValue", current);
      }
    },
    handleClickOutside(e: MouseEvent) {
      const target = e.target as HTMLElement;
      if (!target.closest(".relative")) {
        this.isOpen = false;
        this.searchText = "";
      }
    },
  },
  mounted() {
    document.addEventListener("click", this.handleClickOutside);
  },
  unmounted() {
    document.removeEventListener("click", this.handleClickOutside);
  },
});
</script>
