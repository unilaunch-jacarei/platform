<script lang="ts">
  import { enhance } from "$app/forms";
  import Button from "$lib/components/atoms/Button/Button.svelte";
  import FormField from "$lib/components/molecules/FormField/FormField.svelte";
  import FormHeader from "$lib/components/molecules/FormHeader/FormHeader.svelte";
  import FormFooter from "$lib/components/molecules/FormFooter/FormFooter.svelte";
  import FormCheckbox from "../molecules/FormCheckbox/FormCheckbox.svelte";
  import Card from "../layouts/Card/Card.svelte";

  let submitting = $state(false);
  let { form } = $props();

  function handleSubmit() {
    submitting = true;
    return async ({ update }: { update: () => Promise<void> }) => {
      await update();
      submitting = false;
    };
  }
</script>

<Card class="w-full max-w-[400px]">
  <FormHeader
    title="Bem-vindo de volta"
    description="Acesse sua conta para continuar"
  />
  
  <form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-4">
    {#if form?.error}
      <div
        class="p-3 text-xs rounded-lg bg-destructive/10 border border-destructive/20 text-destructive font-medium"
      >
        {form.error}
      </div>
    {/if}

    <FormField
      id="email"
      name="email"
      label="E-mail"
      type="email"
      placeholder="seu@email.com"
      error={form?.errors?.email}
      required
    />

    <FormField
      id="password"
      name="password"
      label="Senha"
      type="password"
      placeholder="••••••••"
      forgotPasswordHref="/recuperar-senha"
      error={form?.errors?.password}
      required
    />

    <FormCheckbox id="remember" name="remember" label="Lembrar de mim" />

    <Button type="submit" size="lg" class="w-full mt-2" disabled={submitting}>
      {submitting ? "Entrando..." : "Entrar →"}
    </Button>
  </form>

  <FormFooter
    text="Não tem conta?"
    linkLabel="Criar nova conta"
    linkHref="/cadastro"
  />
</Card>
