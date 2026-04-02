<template>
  <div class="relative">
    <button
      v-if="!authStore.isAuthenticated"
      type="button"
      class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-9 w-9"
      @click="showAuthModal = true"
    >
      <User class="h-5 w-5" />
    </button>

    <div v-else class="relative">
      <button
        type="button"
        class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-9 w-9"
        @click="showMenu = !showMenu"
      >
        <Menu class="h-5 w-5" />
      </button>

      <div
        v-if="showMenu"
        class="absolute right-0 mt-2 w-48 rounded-md border border-border bg-background shadow-lg"
      >
        <!--RouterLink
          :to="`/profile/${authStore.slug}`"
          class="flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-accent hover:text-accent-foreground first:rounded-t-md last:rounded-b-md"
          @click="showMenu = false"
        >
          <User class="h-4 w-4" />
          Профиль
        </RouterLink-->
        <!--RouterLink
          to="/schedule"
          class="flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-accent hover:text-accent-foreground first:rounded-t-md last:rounded-b-md"
          @click="showMenu = false"
        >
          <Calendar class="h-4 w-4" />
          Записи
        </RouterLink-->
        <button
          type="button"
          class="flex w-full items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-accent hover:text-accent-foreground first:rounded-t-md last:rounded-b-md"
          @click="handleLogout"
        >
          <LogOut class="h-4 w-4" />
          Выход
        </button>
      </div>
    </div>

    <div
      v-if="showAuthModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="showAuthModal = false"
    >
      <div class="w-full max-w-md rounded-lg border border-border bg-background p-6 shadow-lg mx-4">
        <h2 class="text-xl font-bold text-foreground mb-4">Вход</h2>
        <p class="text-sm text-muted-foreground mb-4">
          Войдите, чтобы получить доступ к управлению записями и профилем
        </p>
        <!--button
          type="button"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-11 w-full"
          @click="handleLogin"
        >
          Войти
        </button-->
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { User, Menu, LogOut, Calendar } from "lucide-vue-next";

export default defineComponent({
  name: "UserMenu",
  components: {
    RouterLink,
    User,
    Menu,
    LogOut,
    Calendar,
  },
  data() {
    return {
      showMenu: false,
      showAuthModal: false,
    };
  },
  setup() {
    const authStore = useAuthStore();
    return {
      authStore,
    };
  },
  methods: {
    handleLogin() {
      this.authStore.login();
      this.showAuthModal = false;
    },
    handleLogout() {
      this.authStore.logout();
      this.showMenu = false;
    },
  },
});
</script>
