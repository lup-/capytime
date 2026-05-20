<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header>
      <template #right>
        <HeaderButtons />
      </template>
    </Header>

    <main class="flex-1">
      <!-- Hero -->
      <section class="container mx-auto px-4 pt-12 pb-16 md:pt-20 md:pb-24">
        <div class="max-w-2xl mx-auto text-center">
          <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground leading-tight mb-4">
            CapyTime — бесплатная и простая запись клиентов
          </h1>
          <p class="text-base md:text-lg text-muted-foreground mb-8">
            Клиенты сразу видят свободные слоты и могут записаться на удобное время
          </p>
        </div>
        <div class="max-w-md mx-auto">
          <img
            :src="calendarPreview"
            alt="Предпросмотр календаря записи"
            class="w-full rounded-xl border border-border shadow-sm"
          >
        </div>
        <div class="max-w-md mx-auto mt-8">
          <RouterLink to="/onboarding">
            <button
              type="button"
              class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            >
              {{ authStore.isAuthenticated ? 'Настройки' : 'Настроить сервис' }}
            </button>
          </RouterLink>
        </div>
      </section>

      <!-- How it works -->
      <section class="container mx-auto px-4 py-16">
        <div class="max-w-2xl text-left">
          <h2 class="text-2xl md:text-3xl font-bold text-foreground mb-6">
            Как это работает
          </h2>
          <p class="mb-4">
            Сервис CapyTime находит в вашем календаре свободные слоты и показывает их клиенту.
          </p>
          <p class="mb-4">
            Ответьте на несколько вопросов, и мы настроим для вас: 
          </p>
          <ul class="list-disc list-inside space-y-2 mb-4 text-foreground marker:text-primary">
            <li>дни и часы, свободные для бронирования;</li>
            <li>расписание всех сеансов;</li>
            <li>перерывы между сеансами;</li>
            <li>запись на очный прием.</li>
          </ul>
          <p class="mb-4">
            Добавим вашу ссылку на сервис для онлайн-встреч, чтобы сразу отправлять ее клиентам 
          </p>
        </div>
      </section>

       <!-- Security -->
       <section class="container mx-auto px-4 py-16">
         <div class="max-w-2xl text-left">
           <h2 class="text-2xl md:text-3xl font-bold text-foreground mb-6">
             Безопасность данных
           </h2>
           <p class="mb-4">
             CapyTime старательно выполняет требования законодательства и заботится о вашей безопасности. Мы храним данные специалистов:
           </p>
           <ul class="list-disc list-inside space-y-2 mb-4 text-foreground marker:text-primary">
             <li>только те публичные данные, которые специалисты указали сами (страницы специалистов);</li>
             <li>на российских серверах с суперзащитой от утечек;</li>
           </ul>
           <p class="mb-4">
             CapyTime не хранит данные о клиентах и записях. Вся информация о записи размещается в личных календарях специалистов.
           </p>
         </div>
       </section>

     </main>

     <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Header from "@/components/Header.vue";
import HeaderButtons from "@/components/HeaderButtons.vue";
import Footer from "@/components/Footer.vue";
import { useAuthStore } from "@/stores/auth";
import calendarPreview from "@/assets/calendar-preview.png";

export default defineComponent({
  name: "IndexView",
  components: {
    Header,
    HeaderButtons,
    Footer,
  },
  data() {
    return {
      calendarPreview,
    };
  },
  computed: {
    authStore() {
      return useAuthStore();
    },
  },
});
</script>

