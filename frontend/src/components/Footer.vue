<template>
  <footer class="w-full border-t border-border mt-16 py-8 px-4">
    <div class="container mx-auto">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-muted-foreground">
        <div>
          <p class="font-medium">ИП Иванов Иван Иванович</p>
          <p>ОГРН: 123456789012345</p>
        </div>
        <div>
          <p>ИНН: 123456789</p>
          <p>Адрес: г. Москва, ул. Примерная, д. 1</p>
        </div>
        <div>
          <p>Лицензия: №12345</p>
          <p>© {{ currentYear }} CapyTime</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "Footer",
  data() {
    return {
      currentYear: new Date().getFullYear(),
    };
  },
});
</script>

