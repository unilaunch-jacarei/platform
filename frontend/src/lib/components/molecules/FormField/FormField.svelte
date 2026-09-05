<!-- src/lib/components/molecules/FormField/FormField.svelte -->
<script lang="ts">
  import type { Snippet } from "svelte";
  import type { HTMLInputAttributes } from "svelte/elements";
  import Input from "../../atoms/Input/Input.svelte";
  import Typography from "../../atoms/Typography/Typography.svelte";

  type FormFieldProps = Omit<HTMLInputAttributes, "children"> & {
    id?: string;
    label?: string;
    error?: string;
    description?: string;
    required?: boolean;
    class?: string;
    value?: string | number | null;
    forgotPasswordHref?: string;
    forgotPasswordLabel?: string;
    children?: Snippet;
  };

  let {
    id,
    label,
    error,
    description,
    required = false,
    class: className = "",
    value = $bindable(""),
    type = "text",
    forgotPasswordHref,
    forgotPasswordLabel = "Esqueci minha senha",
    children,
    ...restProps
  }: FormFieldProps = $props();

  let showPassword = $state(false);

  const computedType = $derived(
    type === "password" ? (showPassword ? "text" : "password") : type,
  );
</script>

<div class="flex flex-col gap-1.5 w-full {className}">
  <!-- Header do Campo: Label e Link de Recuperação -->
  {#if label || (type === "password" && forgotPasswordHref)}
    <div class="flex items-center justify-between w-full">
      {#if label}
        <label
          for={id}
          class="inline-flex items-center gap-1 cursor-pointer w-fit"
        >
          <Typography variant="label">{label}</Typography>
          {#if required}
            <span
              class="text-destructive font-bold text-xs"
              title="Campo obrigatório">*</span
            >
          {/if}
        </label>
      {/if}

      {#if type === "password" && forgotPasswordHref}
        <a
          href={forgotPasswordHref}
          class="text-xs font-semibold text-accent hover:underline transition-colors ml-auto"
        >
          {forgotPasswordLabel}
        </a>
      {/if}
    </div>
  {/if}

  <!-- Slot do Input / Input Nativo -->
  <div class="relative w-full">
    {#if children}
      {@render children()}
    {:else}
      <Input
        {id}
        type={computedType}
        bind:value
        {required}
        aria-invalid={!!error}
        class={type === "password" ? "pr-10" : ""}
        {...restProps}
      />

      <!-- Botão de Visibilidade da Senha -->
      {#if type === "password"}
        <button
          type="button"
          onclick={() => (showPassword = !showPassword)}
          class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          tabindex="-1"
          aria-label={showPassword ? "Ocultar senha" : "Exibir senha"}
        >
          {#if showPassword}
            <!-- Ícone Olho Aberto -->
            <svg
              class="size-4 shrink-0 stroke-2"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          {:else}
            <!-- Ícone Olho Fechado -->
            <svg
              class="size-4 shrink-0 stroke-2"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
              <path
                d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"
              />
              <path
                d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"
              />
              <line x1="2" x2="22" y1="2" y2="22" />
            </svg>
          {/if}
        </button>
      {/if}
    {/if}
  </div>

  <!-- Descrição Auxiliar -->
  {#if description && !error}
    <Typography variant="caption" class="text-xs text-muted">
      {description}
    </Typography>
  {/if}

  <!-- Mensagem de Erro -->
  {#if error}
    <Typography
      variant="caption"
      class="text-xs text-destructive flex items-center gap-1 font-medium transition-all duration-150"
    >
      <svg
        class="size-3.5 shrink-0 stroke-[2.5]"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12" y2="17" />
      </svg>
      {error}
    </Typography>
  {/if}
</div>
