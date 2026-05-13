<template>
  <footer class="w-full border-t border-border mt-16 py-8 px-4">
    <div class="container mx-auto">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
        <div class="flex flex-col sm:flex-row gap-2 sm:gap-4">
          <RouterLink to="/privacy-policy" class="hover:text-primary transition-colors">
            Политика конфиденциальности
          </RouterLink>
          <RouterLink to="/personal-data-processing" class="hover:text-primary transition-colors">
            Правила обработки персональных данных
          </RouterLink>
          <RouterLink to="/terms-of-service" class="hover:text-primary transition-colors">
            Правила пользования сервисом
          </RouterLink>
        </div>
        <p>©&nbsp;{{ currentYear }}&nbsp;CapyTime</p>
      </div>
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterLink } from "vue-router";

export default defineComponent({
  name: "Footer",
  components: {
    RouterLink,
  },
  data() {
    return {
      currentYear: new Date().getFullYear(),
    };
  },
});
</script>
