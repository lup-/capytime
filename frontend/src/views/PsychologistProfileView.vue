<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Header>
      <template #right>
        <button
          v-if="canEdit"
          type="button"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2"
          @click="toggleEditMode"
        >
          {{ psychologistStore.editMode ? "Готово" : "Редактировать" }}
        </button>
      </template>
    </Header>

    <main class="flex-1 w-full py-8 px-4 xl:px-0">
      <!-- Верхний блок (на всю ширину) -->
      <div class="w-full mx-auto space-y-6 mb-8">
        <!-- Аватар и имя -->
        <div class="flex flex-col items-center space-y-4">
          <!-- Аватар -->
          <div v-if="psychologistStore.psychologist?.avatar" class="relative">
            <img
              :src="psychologistStore.psychologist.avatar"
              alt="Аватар"
              class="w-40 h-40 rounded-full object-cover border-2 border-border"
            />
            <label
              v-if="psychologistStore.editMode"
              class="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center cursor-pointer"
            >
              <Check v-if="psychologistStore.editingField === 'avatar'" class="w-4 h-4 text-primary-foreground" /><SquarePen v-else class="w-4 h-4 text-primary-foreground" />
              <input type="file" accept="image/*" class="hidden" @change="handleAvatarUpload" />
            </label>
          </div>
          <label
            v-else
            class="w-40 h-40 rounded-full border-2 border-dashed border-border flex flex-col items-center justify-center gap-2 text-muted-foreground"
            :class="psychologistStore.editMode ? 'cursor-pointer hover:border-primary' : ''"
          >
            <span class="text-3xl">⬆</span>
            <span class="text-xs">Загрузить фото</span>
            <input v-if="psychologistStore.editMode" type="file" accept="image/*" class="hidden" @change="handleAvatarUpload" />
          </label>

          <!-- Имя -->
          <div>
            <div class="flex items-center gap-2">
              <input
                v-if="psychologistStore.editingField === 'firstName'"
                v-model="psychologistStore.psychologist!.firstName"
                type="text"
                class="text-2xl font-bold bg-transparent border-b border-input focus:outline-none"
              />
              <input
                v-if="psychologistStore.editingField === 'lastName'"
                v-model="psychologistStore.psychologist!.lastName"
                type="text"
                class="text-2xl font-bold bg-transparent border-b border-input focus:outline-none"
              />
              <template v-if="!psychologistStore.editingField?.startsWith('name')">
                <h1 class="text-2xl md:text-3xl font-bold text-foreground">
                  {{ psychologistStore.psychologist?.firstName }} {{ psychologistStore.psychologist?.lastName }}
                </h1>
              </template>
              <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('firstName')">
                <Check v-if="psychologistStore.editingField === 'firstName'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- С чем работаю -->
          <div class="flex flex-col items-center">
            <div v-if="psychologistStore.editingField === 'problems'" class="space-y-3 w-full">
              <div class="flex flex-wrap gap-2">
                <span v-for="p in psychologistStore.problems" :key="p" class="px-3 py-1.5 rounded-lg text-sm bg-primary/10 text-primary flex items-center gap-1">
                  {{ p }}
                  <button type="button" class="text-primary hover:text-red-500" @click="psychologistStore.removeProblem(p)">×</button>
                </span>
              </div>
              <div class="flex gap-2">
                <input
                  v-model="psychologistStore.problemInput"
                  type="text"
                  placeholder="Добавить проблему..."
                  class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                  @keydown.enter.prevent="psychologistStore.addProblem(psychologistStore.problemInput)"
                />
              </div>
              <div class="flex flex-wrap gap-1">
                <button v-for="p in psychologistStore.availableProblems" :key="p" type="button" class="px-2 py-1 rounded text-xs bg-secondary text-muted-foreground hover:text-foreground" @click="psychologistStore.addProblem(p)">
                  + {{ p }}
                </button>
              </div>
            </div>
            <div v-else class="flex flex-wrap gap-2 justify-center">
              <span v-for="p in psychologistStore.problems" :key="p" class="px-3 py-1.5 rounded-lg text-sm bg-secondary text-foreground">
                {{ p }}
              </span>
              <button v-if="psychologistStore.editMode" type="button" class="text-muted-foreground hover:text-primary text-sm" @click="psychologistStore.setEditingField('problems')">
                <Check v-if="psychologistStore.editingField === 'problems'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Записаться -->
          <router-link class="w-full md:w-80" :to="`/booking/${psychologistStore.slug}/format`">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors bg-primary text-primary-foreground hover:bg-primary/90 w-full h-11">
              Записаться
            </button>
          </router-link>
        </div>
      </div>

      <!-- Блок с колонками -->
      <div class="w-full mx-auto flex flex-col md:flex-row gap-8">
        <!-- Левая колонка (узкая) -->
        <div class="w-full md:w-80 flex-shrink-0 space-y-6">
          <!-- Направления -->
          <div>
            <div class="flex items-center mb-2">
              <span class="font-bold text-foreground">Направления</span>
              <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('specializations')"><Check v-if="psychologistStore.editingField === 'specializations'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" /></button>
            </div>
            <div v-if="psychologistStore.editingField === 'specializations'" class="flex flex-wrap gap-2">
              <button
                v-for="spec in SPECIALTIES.map(s => s.value)"
                :key="spec"
                type="button"
                class="px-3 py-1.5 rounded-lg text-sm transition-colors"
                :class="psychologistStore.specialtiesList.includes(spec) ? 'bg-primary text-primary-foreground' : 'bg-secondary text-foreground'"
                @click="psychologistStore.toggleSpecialization(spec)"
              >
                {{ spec }}
              </button>
            </div>
            <div v-else class="flex flex-wrap gap-2">
              <span v-for="spec in psychologistStore.specialtiesList" :key="spec" class="px-3 py-1.5 rounded-lg text-sm bg-secondary text-foreground">
                {{ spec }}
              </span>
            </div>
          </div>

          <!-- Основные метрики -->
          <div class="space-y-4">
            <div class="flex items-center">
              <div v-if="psychologistStore.editingField === 'experience'" class="flex items-center gap-2">
                <span class="text-foreground">Опыт</span>
                <input v-model="experienceInput" type="text" class="w-16 h-8 rounded-md border border-input bg-background px-2 text-sm" />
                <span class="text-foreground">лет</span>
              </div>
              <p v-else class="font-bold text-foreground">Опыт {{ experienceInput }} лет</p>
              <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('experience')"><Check v-if="psychologistStore.editingField === 'experience'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" /></button>
            </div>
            <div class="flex items-center">
              <div v-if="psychologistStore.editingField === 'onlinePrice'" class="flex items-center gap-2">
                <input v-model="psychologistStore.psychologist!.onlinePrice" type="text" class="w-20 h-8 rounded-md border border-input bg-background px-2 text-sm" />
                <span class="text-foreground">₽ / онлайн</span>
              </div>
              <p v-else class="font-bold text-foreground">{{ psychologistStore.psychologist?.onlinePrice }} ₽ / онлайн</p>
              <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('onlinePrice')"><Check v-if="psychologistStore.editingField === 'onlinePrice'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" /></button>
            </div>
            <div class="flex items-center">
              <div v-if="psychologistStore.editingField === 'offlinePrice'" class="flex items-center gap-2">
                <input v-model="psychologistStore.psychologist!.offlinePrice" type="text" class="w-20 h-8 rounded-md border border-input bg-background px-2 text-sm" />
                <span class="text-foreground">₽ / очно</span>
              </div>
              <p v-else class="font-bold text-foreground">{{ psychologistStore.psychologist?.offlinePrice }} ₽ / очно</p>
              <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('offlinePrice')"><Check v-if="psychologistStore.editingField === 'offlinePrice'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" /></button>
            </div>
            <div class="flex flex-col items-start">
              <p class="font-bold text-foreground">Адрес
                <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('offlineAddress')"><Check v-if="psychologistStore.editingField === 'offlineAddress'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" /></button>
              </p>
              <textarea v-if="psychologistStore.editingField === 'offlineAddress'" v-model="psychologistStore.psychologist!.offlineAddress" type="text" class="flex-1 h-8 rounded-md border border-input bg-background px-2 text-sm" />
              <p v-else class="text-sm text-muted-foreground">{{ psychologistStore.psychologist?.offlineAddress }}</p>
            </div>
          </div>
        </div>

        <!-- Правая колонка (широкая) -->
        <div class="flex-1 space-y-6">
          <!-- Обо мне -->
          <section class="border rounded-lg p-4">
            <div class="flex items-center justify-start mb-3">
              <h2 class="text-xl font-bold text-foreground">Обо мне</h2>
              <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('about')"><Check v-if="psychologistStore.editingField === 'about'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" /></button>
            </div>
            <textarea v-if="psychologistStore.editingField === 'about'" v-model="psychologistStore.psychologist!.about" class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm min-h-[100px]" placeholder="Расскажите о себе..." />
            <p v-else class="text-muted-foreground whitespace-pre-wrap">{{ psychologistStore.psychologist?.about || "Информация не заполнена" }}</p>
          </section>

          <!-- Образование -->
          <section class="border rounded-lg p-4">
            <div class="flex items-center justify-start mb-3">
              <h2 class="text-xl font-bold text-foreground">Образование</h2>
              <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('education')"><Check v-if="psychologistStore.editingField === 'education'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" /></button>
            </div>
            <textarea v-if="psychologistStore.editingField === 'education'" v-model="psychologistStore.psychologist!.education" class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm min-h-[100px]" placeholder="Укажите образование..." />
            <p v-else class="text-muted-foreground whitespace-pre-wrap">{{ psychologistStore.psychologist?.education || "Информация не заполнена" }}</p>
          </section>

          <!-- Профессиональный опыт -->
          <section class="border rounded-lg p-4">
            <div class="flex items-center justify-start mb-3">
              <h2 class="text-xl font-bold text-foreground">Профессиональный опыт</h2>
              <button v-if="psychologistStore.editMode" type="button" class="ml-2 text-muted-foreground hover:text-primary" @click="psychologistStore.setEditingField('proExperience')"><Check v-if="psychologistStore.editingField === 'proExperience'" class="w-4 h-4" /><SquarePen v-else class="w-4 h-4" /></button>
            </div>
            <textarea v-if="psychologistStore.editingField === 'proExperience'" v-model="psychologistStore.psychologist!.proExperience" class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm min-h-[100px]" placeholder="Опишите профессиональный опыт..." />
            <p v-else class="text-muted-foreground whitespace-pre-wrap">{{ psychologistStore.psychologist?.proExperience || "Информация не заполнена" }}</p>
          </section>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from "vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import { usePsychologistStore, SPECIALTIES, PROBLEMS } from "@/stores/psychologist";
import { useAuthStore } from "@/stores/auth";
import { SquarePen, Check } from "lucide-vue-next";

export default defineComponent({
  name: "PsychologistProfileView",
  setup() {
    const psychologistStore = usePsychologistStore();
    const authStore = useAuthStore();
    const experienceInput = ref("9");
    const canEdit = computed(() => {
      return authStore.isAuthenticated && 
             authStore.psychologist && 
             psychologistStore.psychologist &&
             authStore.psychologist.id === psychologistStore.psychologist.id;
    });
    return {
      psychologistStore,
      authStore,
      experienceInput,
      canEdit,
      SPECIALTIES,
      PROBLEMS
    };
  },
  components: {
      Header,
      Footer,
      SquarePen,
      Check
  },
  created() {
    const slug = this.$route.params.slug as string;
    if (slug) {
      this.psychologistStore.loadBySlug(slug);
    }

    if (typeof window !== "undefined") {
      const saved = window.localStorage.getItem("capytimeAvatar");
      if (saved && this.psychologistStore.psychologist) {
        this.psychologistStore.psychologist.avatar = saved;
      }
    }
  },
  methods: {
    toggleEditMode() {
      this.psychologistStore.toggleEditMode();
    },
    copyBookingLink() {
      const link = `capytime.ru/${this.psychologistStore.slug}`;
      if (navigator?.clipboard?.writeText) {
        navigator.clipboard.writeText(link);
      }
    },
    handleAvatarUpload(e: Event) {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const result = ev.target?.result as string;
        if (this.psychologistStore.psychologist) {
          this.psychologistStore.psychologist.avatar = result;
        }
        if (typeof window !== "undefined") {
          window.localStorage.setItem("capytimeAvatar", result);
        }
      };
      reader.readAsDataURL(file);
    },
  },
});
</script>
