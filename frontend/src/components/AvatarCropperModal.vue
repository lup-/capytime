<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
    @click.self="$emit('cancel')"
  >
    <div class="bg-card rounded-xl p-6 w-full max-w-lg mx-4 shadow-xl">
      <h3 class="text-lg font-semibold text-foreground mb-4">
        Обрезка фото
      </h3>

      <div class="rounded-lg overflow-hidden bg-secondary">
        <Cropper
          v-if="src"
          ref="cropperRef"
          :src="src"
          :stencil-component="CircleStencil"
          :aspect-ratio="1"
          :check-image-orientation="false"
          class="h-80"
        />
      </div>

      <p class="text-xs text-muted-foreground mt-3 text-center">
        Перетащите изображение, чтобы выбрать область
      </p>

      <div class="flex gap-3 mt-4">
        <button
          type="button"
          class="flex-1 inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 border border-input bg-background hover:bg-secondary h-10"
          @click="$emit('cancel')"
        >
          Отмена
        </button>
        <button
          type="button"
          class="flex-1 inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 h-10"
          @click="confirm"
        >
          Сохранить
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from "vue";
import { Cropper, CircleStencil } from "vue-advanced-cropper";
import "vue-advanced-cropper/dist/style.css";

export default defineComponent({
  name: "AvatarCropperModal",
  components: { Cropper, CircleStencil },
  props: {
    file: {
      type: File,
      required: true,
    },
  },
  emits: ["confirm", "cancel"],
  setup(props, { emit }) {
    const cropperRef = ref<InstanceType<typeof Cropper> | null>(null);

    const src = computed(() => URL.createObjectURL(props.file));

    function confirm() {
      const cropper = cropperRef.value;
      if (!cropper) return;

      const result = cropper.getResult();
      const sourceCanvas = result.canvas;
      if (!sourceCanvas) return;

      const cvs = document.createElement("canvas");
      cvs.width = 250;
      cvs.height = 250;
      const ctx = cvs.getContext("2d");
      if (!ctx) return;

      ctx.drawImage(sourceCanvas, 0, 0, 250, 250);

      cvs.toBlob(
        (blob) => {
          if (!blob) return;
          const croppedFile = new File([blob], "avatar.webp", {
            type: "image/webp",
          });
          emit("confirm", croppedFile);
        },
        "image/webp",
        85,
      );
    }

    return { cropperRef, src, CircleStencil, confirm };
  },
});
</script>
