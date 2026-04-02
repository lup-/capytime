<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header>
      <template #right>
        <RouterLink to="/onboarding">
          <button
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2"
            type="button"
          >
            Регистрация
          </button>
        </RouterLink>
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
          <div class="w-full rounded-xl border border-border shadow-sm bg-secondary h-64 flex items-center justify-center">
            <span class="text-sm text-muted-foreground">
              Здесь будет предпросмотр календаря записи
            </span>
          </div>
        </div>
      </section>

      <!-- Setup block -->
      <section class="container mx-auto px-4 pb-16">
        <div class="max-w-md mx-auto space-y-4">
          <button
            type="button"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11"
            :disabled="!agreed"
            @click="handleSetup"
          >
            Настроить сервис
          </button>
          <div class="flex items-center justify-between gap-3">
            <a href="#" class="text-xs text-primary hover:underline">
              Согласие на обработку персональных данных
            </a>
            <Toggle v-model="agreed" />
          </div>
          <p class="text-xs text-muted-foreground">
            Нажимая на кнопку, вы соглашаетесь с условиями использования сервиса
          </p>
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
            CapyTime старательно выполняет требования законодательства и заботится о вашей безопасности. Мы храним данные специалистов и клиентов:
          </p>
          <ul class="list-disc list-inside space-y-2 mb-4 text-foreground marker:text-primary">
            <li>временно, пока не пройдет встреча;</li>
            <li>на российских серверах с суперзащитой от утечек;</li>
            <li>обезличенно, чтобы никто не мог сопоставить имя клиента и его запись к специалисту.</li>
          </ul>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import Toggle from "@/components/ui/Toggle.vue";

export default defineComponent({
  name: "IndexView",
  components: {
    Header,
    Footer,
    Toggle,
  },
  data() {
    return {
      agreed: false,
    };
  },
  methods: {
    handleSetup() {
      if (this.agreed) {
        this.$router.push({ path: "/onboarding", query: { step: "calendar" } });
      }
    },
  },
});
</script>

