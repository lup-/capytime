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

    <!-- Security -->
      <section class="container mx-auto px-4 py-16">
        <div class="max-w-2xl text-left">
          <h2 class="text-2xl md:text-3xl font-bold text-foreground mb-6">
            Безопасность данных
          </h2>
          <p class="mb-4">
            Сервис CapyTime хранит данные:
          </p>
          <ul class="list-disc list-inside space-y-2 mb-4 text-foreground marker:text-primary">
            <li>в соответствии с 152 ФЗ,</li>
            <li>временно, пока не пройдет встреча,</li>
            <li>обезличенно, чтобы никто не мог сопоставить имя клиента и его запись к специалисту.</li>
          </ul>
        </div>
        <div class="mt-8 max-w-md mx-auto">
          <img :src="secure" alt="Безопасность данных" class="w-full rounded-xl border border-border shadow-sm">
        </div>
      </section>

      <!-- Features -->
      <section class="container mx-auto px-4 py-16">
        <div class="max-w-2xl text-left mb-10">
          <h2 class="text-2xl md:text-3xl font-bold text-foreground mb-6">
            Возможности сервиса
          </h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-white rounded-xl p-6 border-2 border-primary/20">
            <p class="text-foreground mb-4">CapyTime находит в вашем google-календаре свободные слоты и показывает клиенту</p>
            <img :src="screen01" alt="Свободные слоты в Google-календаре" class="w-full rounded-lg">
          </div>
          <div class="bg-white rounded-xl p-6 border-2 border-primary/20">
            <p class="text-foreground mb-4">Дни и часы работы можно настроить</p>
            <img :src="screen02" alt="Настройка дней и часов работы" class="w-full rounded-lg">
          </div>
          <div class="bg-white rounded-xl p-6 border-2 border-primary/20">
            <p class="text-foreground mb-4">Настройте размер перерыва после сессии, и CapyTime добавит его после каждого бронирования</p>
            <img :src="screen03" alt="Настройка перерыва после сессии" class="w-full rounded-lg">
          </div>
          <div class="bg-white rounded-xl p-6 border-2 border-primary/20">
            <p class="text-foreground mb-4">Сервис позволяет записывать клиентов на очную и онлайн-встречи</p>
            <img :src="screen04" alt="Запись на очные и онлайн-встречи" class="w-full rounded-lg">
          </div>
          <div class="bg-white rounded-xl p-6 border-2 border-primary/20">
            <p class="text-foreground mb-4">Укажите свой сервис видеосвязи, и CapyTime отправит клиенту ссылку на онлайн-встречу</p>
            <img :src="screen05" alt="Сервис видеосвязи" class="w-full rounded-lg">
          </div>
          <div class="bg-white rounded-xl p-6 border-2 border-primary/20">
            <p class="text-foreground mb-4">Клиент получит email с информацией о записи и при необходимости сможет ее перенести. Возможность переноса можно отключить.</p>
          </div>
          <div class="bg-white rounded-xl p-6 border-2 border-primary/20">
            <p class="text-foreground mb-4">Также мы напомним и клиенту, и вам о записи за сутки. Ничего не потеряется.</p>
            <img :src="screen07" alt="Напоминание о записи за сутки" class="w-full rounded-lg">
          </div>
        </div>
      </section>

     </main>

     <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useHead } from "@vueuse/head";
import Header from "@/components/Header.vue";
import HeaderButtons from "@/components/HeaderButtons.vue";
import Footer from "@/components/Footer.vue";
import { useAuthStore } from "@/stores/auth";
import calendarPreview from "@/assets/calendar-preview.png";
import secure from "@/assets/secure.jpg";
import screen01 from "@/assets/screen01.png";
import screen02 from "@/assets/screen02.png";
import screen03 from "@/assets/screen03.png";
import screen04 from "@/assets/screen04.png";
import screen05 from "@/assets/screen05.png";
import screen07 from "@/assets/screen07.png";


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
      secure,
      screen01,
      screen02,
      screen03,
      screen04,
      screen05,
      screen07,
    };
  },
  computed: {
    authStore() {
      return useAuthStore();
    },
  },
  setup() {
    useHead({
      script: [
        {
          type: "application/ld+json",
          innerHTML: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
              {
                "@type": "Question",
                "name": "Сколько стоит CapyTime?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "CapyTime полностью бесплатен. Никаких тарифов, пробных периодов и скрытых платежей."
                }
              },
              {
                "@type": "Question",
                "name": "Нужно ли устанавливать приложение?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "Нет, CapyTime работает в браузере на телефоне, планшете и компьютере."
                }
              },
              {
                "@type": "Question",
                "name": "Какие календари поддерживаются?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "Google Calendar. Мы работаем над добавлением Outlook."
                }
              },
              {
                "@type": "Question",
                "name": "Как клиенты получают напоминания?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "По электронной почте. Клиент получает письмо с подтверждением записи и напоминание перед приёмом."
                }
              },
              {
                "@type": "Question",
                "name": "Подходит ли сервис для команды?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "Да, несколько специалистов могут использовать один аккаунт."
                }
              },
              {
                "@type": "Question",
                "name": "Что нужно для старта?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "Зарегистрироваться, подключить календарь и отправить клиентам ссылку на запись. Весь процесс занимает 5 минут."
                }
              }
            ]
          })
        }
      ]
    });
  },
});
</script>

