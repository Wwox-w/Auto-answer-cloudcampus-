<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import {
  Settings,
  Globe,
  Key,
  Cpu,
  Monitor,
  Gauge,
  Clock,
  Save,
  Loader2,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  ShieldAlert,
} from 'lucide-vue-next'
import { SwitchRoot, SwitchThumb } from 'radix-vue'
import NavBar from '@/components/NavBar.vue'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()

// --- Local form state (pre-filled from store after fetch) ---
const form = reactive({
  llm_api_base: '',
  llm_api_key: '',
  llm_model: '',
  headless: false,
  slow_mo: 300,
  page_timeout: 30000,
})

// --- UI state ---
const showApiKey = ref(false)
const saving = ref(false)
const saveSuccess = ref(false)
const saveError = ref('')
const validationErrors = ref<string[]>([])
const formTouched = ref(false)

// --- Pre-fill form when store data arrives ---
watch(
  () => configStore.llm,
  (llm) => {
    if (llm.llm_api_base || llm.llm_api_key || llm.llm_model) {
      form.llm_api_base = llm.llm_api_base
      form.llm_api_key = llm.llm_api_key
      form.llm_model = llm.llm_model
    }
  },
  { immediate: true },
)

watch(
  () => configStore.browser,
  (browser) => {
    form.headless = browser.headless
    form.slow_mo = browser.slow_mo
    form.page_timeout = browser.page_timeout
  },
  { immediate: true },
)

// --- Fetch on mount ---
onMounted(async () => {
  try {
    await configStore.fetchConfig()
  } catch {
    // Non-blocking; form defaults are already set
  }
})

// --- Validation ---
function validate(): boolean {
  const errors: string[] = []
  if (!form.llm_api_key.trim()) {
    errors.push('API Key 不能为空')
  }
  validationErrors.value = errors
  return errors.length === 0
}

// --- Save handler ---
async function handleSave() {
  formTouched.value = true
  saveError.value = ''
  saveSuccess.value = false

  if (!validate()) return

  saving.value = true
  try {
    // Sync form state into store
    configStore.llm.llm_api_base = form.llm_api_base
    configStore.llm.llm_api_key = form.llm_api_key
    configStore.llm.llm_model = form.llm_model
    configStore.browser.headless = form.headless
    configStore.browser.slow_mo = form.slow_mo
    configStore.browser.page_timeout = form.page_timeout

    await configStore.saveConfig()
    saveSuccess.value = true
    validationErrors.value = []

    // Auto-dismiss success after 4s
    setTimeout(() => {
      saveSuccess.value = false
    }, 4000)
  } catch (e) {
    saveError.value = e instanceof Error ? e.message : '保存失败，请重试'
  } finally {
    saving.value = false
  }
}

// --- Common input classes ---
const inputBase =
  'w-full h-10 rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/50 transition-colors duration-200 focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-50'
const labelBase = 'text-sm font-medium text-foreground'
const helperBase = 'text-xs text-muted-foreground mt-1.5'

// Models for dropdown suggestion
const commonModels = [
  'gpt-4o',
  'gpt-4o-mini',
  'gpt-4-turbo',
  'claude-3-opus',
  'claude-3-sonnet',
  'deepseek-chat',
  'deepseek-reasoner',
  'qwen-plus',
  'glm-4',
]
</script>

<template>
  <div class="min-h-screen bg-background">
    <NavBar />

    <main class="mx-auto max-w-2xl px-6 py-8">
      <!-- ============ Page Header ============ -->
      <div class="mb-8 flex items-center gap-4">
        <div
          class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 ring-1 ring-primary/20"
        >
          <Settings class="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-tight text-foreground">配置</h1>
          <p class="text-sm text-muted-foreground">LLM 与浏览器参数设置</p>
        </div>
      </div>

      <!-- ============ Success Toast ============ -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="saveSuccess"
          class="mb-6 flex items-center gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-300"
        >
          <CheckCircle2 class="h-4 w-4 flex-shrink-0" />
          <span>配置已保存成功</span>
        </div>
      </Transition>

      <!-- ============ Error Toast ============ -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="saveError"
          class="mb-6 flex items-center gap-3 rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-red-300"
        >
          <AlertCircle class="h-4 w-4 flex-shrink-0" />
          <span>{{ saveError }}</span>
        </div>
      </Transition>

      <!-- ============ LLM Configuration Card ============ -->
      <section class="mb-6 overflow-hidden rounded-xl border border-border bg-card">
        <!-- Card header -->
        <div class="flex items-center gap-3 border-b border-border/60 px-5 py-4">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10"
          >
            <Cpu class="h-4 w-4 text-primary" />
          </div>
          <div>
            <h2 class="text-sm font-semibold text-foreground">LLM 配置</h2>
            <p class="text-xs text-muted-foreground">大语言模型连接参数</p>
          </div>
        </div>

        <!-- Card body -->
        <div class="space-y-5 px-5 py-5">
          <!-- API Base URL -->
          <div class="space-y-2">
            <label class="flex items-center gap-2" :class="labelBase" for="api-base-url">
              <Globe class="h-3.5 w-3.5 text-muted-foreground" />
              API Base URL
            </label>
            <input
              id="api-base-url"
              v-model="form.llm_api_base"
              type="url"
              :class="inputBase"
              placeholder="https://api.deepseek.com/v1"
              autocomplete="url"
            />
            <p :class="helperBase">兼容 OpenAI 接口格式的 API 地址</p>
          </div>

          <!-- API Key -->
          <div class="space-y-2">
            <label class="flex items-center gap-2" :class="labelBase" for="api-key">
              <Key class="h-3.5 w-3.5 text-muted-foreground" />
              API Key
              <span class="text-destructive">*</span>
            </label>
            <div class="relative">
              <input
                id="api-key"
                v-model="form.llm_api_key"
                :type="showApiKey ? 'text' : 'password'"
                :class="[
                  inputBase,
                  'pr-10',
                  formTouched && validationErrors.some(e => e.includes('API Key'))
                    ? 'border-destructive/60 focus:border-destructive/60 focus:ring-destructive/20'
                    : '',
                ]"
                placeholder="sk-••••••••••••••••••••••••"
                autocomplete="off"
              />
              <button
                type="button"
                class="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-muted-foreground transition-colors hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/30"
                :aria-label="showApiKey ? '隐藏 API Key' : '显示 API Key'"
                @click="showApiKey = !showApiKey"
              >
                <EyeOff v-if="showApiKey" class="h-4 w-4" />
                <Eye v-else class="h-4 w-4" />
              </button>
            </div>

            <!-- Validation error -->
            <Transition
              enter-active-class="transition-all duration-200"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
            >
              <p
                v-if="formTouched && validationErrors.some(e => e.includes('API Key'))"
                class="flex items-center gap-1.5 text-xs text-destructive"
              >
                <ShieldAlert class="h-3 w-3" />
                API Key 不能为空
              </p>
            </Transition>

            <p :class="helperBase">用于调用大语言模型服务的密钥</p>
          </div>

          <!-- Model -->
          <div class="space-y-2">
            <label class="flex items-center gap-2" :class="labelBase" for="model">
              <Cpu class="h-3.5 w-3.5 text-muted-foreground" />
              模型
            </label>
            <div class="relative">
              <input
                id="model"
                v-model="form.llm_model"
                type="text"
                :class="[inputBase, 'pr-8']"
                placeholder="gpt-4o / deepseek-chat"
                list="model-suggestions"
                autocomplete="off"
              />
              <!-- Dropdown chevron hint -->
              <svg
                class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="m6 9 6 6 6-6" />
              </svg>
            </div>
            <datalist id="model-suggestions">
              <option v-for="m in commonModels" :key="m" :value="m" />
            </datalist>
            <p :class="helperBase">模型标识符，如 gpt-4o、deepseek-chat 等</p>
          </div>
        </div>
      </section>

      <!-- ============ Browser Configuration Card ============ -->
      <section class="mb-6 overflow-hidden rounded-xl border border-border bg-card">
        <!-- Card header -->
        <div class="flex items-center gap-3 border-b border-border/60 px-5 py-4">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10"
          >
            <Monitor class="h-4 w-4 text-primary" />
          </div>
          <div>
            <h2 class="text-sm font-semibold text-foreground">浏览器配置</h2>
            <p class="text-xs text-muted-foreground">Playwright 自动化参数</p>
          </div>
        </div>

        <!-- Card body -->
        <div class="space-y-5 px-5 py-5">
          <!-- Headless Mode Toggle -->
          <div
            class="flex items-center justify-between rounded-lg bg-background/50 px-4 py-3.5"
          >
            <div class="space-y-0.5">
              <label class="text-sm font-medium text-foreground" for="headless-switch">
                无头模式
              </label>
              <p class="text-xs text-muted-foreground">
                {{ form.headless ? '浏览器在后台静默运行' : '显示浏览器窗口用于调试' }}
              </p>
            </div>
            <SwitchRoot
              id="headless-switch"
              v-model:checked="form.headless"
              class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background data-[state=checked]:bg-primary data-[state=unchecked]:bg-muted"
            >
              <SwitchThumb
                class="pointer-events-none block h-4 w-4 rounded-full bg-white shadow-sm ring-0 transition-transform duration-200 data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0"
              />
            </SwitchRoot>
          </div>

          <!-- Operation Delay Slider -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <label class="flex items-center gap-2" :class="labelBase">
                <Gauge class="h-3.5 w-3.5 text-muted-foreground" />
                操作延迟
              </label>
              <span
                class="inline-flex items-center rounded-md bg-primary/10 px-2 py-0.5 text-xs font-mono font-medium tabular-nums text-primary"
              >
                {{ form.slow_mo }} ms
              </span>
            </div>

            <!-- Custom range slider -->
            <div class="relative flex items-center gap-3">
              <span class="text-xs tabular-nums text-muted-foreground w-8 text-right">0</span>
              <div class="relative flex-1">
                <!-- Track background -->
                <div class="absolute top-1/2 h-1.5 w-full -translate-y-1/2 rounded-full bg-muted" />
                <!-- Filled track -->
                <div
                  class="absolute top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-primary/60 transition-all duration-150"
                  :style="{ width: `${(form.slow_mo / 3000) * 100}%` }"
                />
                <!-- Range input -->
                <input
                  v-model.number="form.slow_mo"
                  type="range"
                  min="0"
                  max="3000"
                  step="50"
                  class="relative w-full appearance-none bg-transparent [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:shadow-md [&::-webkit-slider-thumb]:shadow-primary/20 [&::-webkit-slider-thumb]:ring-2 [&::-webkit-slider-thumb]:ring-background [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:transition-transform [&::-webkit-slider-thumb]:duration-150 hover:[&::-webkit-slider-thumb]:scale-110 focus-visible:[&::-webkit-slider-thumb]:ring-primary/50 focus-visible:outline-none"
                />
              </div>
              <span class="text-xs tabular-nums text-muted-foreground w-8">3000</span>
            </div>
            <p :class="helperBase">每次操作之间的等待间隔（模拟人工操作速度）</p>
          </div>

          <!-- Page Timeout -->
          <div class="space-y-2">
            <label class="flex items-center gap-2" :class="labelBase" for="page-timeout">
              <Clock class="h-3.5 w-3.5 text-muted-foreground" />
              页面超时
            </label>
            <div class="relative">
              <input
                id="page-timeout"
                v-model.number="form.page_timeout"
                type="number"
                :class="inputBase"
                placeholder="30000"
                min="5000"
                max="120000"
                step="1000"
              />
              <span
                class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground"
              >
                ms
              </span>
            </div>
            <p :class="helperBase">页面加载最大等待时间（毫秒）</p>
          </div>
        </div>
      </section>

      <!-- ============ Save Button ============ -->
      <div class="flex items-center gap-4">
        <button
          type="button"
          :disabled="saving"
          class="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all duration-200 hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
          @click="handleSave"
        >
          <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
          <Save v-else class="h-4 w-4" />
          {{ saving ? '保存中...' : '保存配置' }}
        </button>

        <!-- Status feedback inline -->
        <Transition
          enter-active-class="transition-all duration-300"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
        >
          <span
            v-if="saveSuccess"
            class="flex items-center gap-1.5 text-sm text-emerald-400"
          >
            <CheckCircle2 class="h-4 w-4" />
            已保存
          </span>
        </Transition>
      </div>

      <!-- Bottom safe-area spacer -->
      <div class="h-12" />
    </main>
  </div>
</template>
