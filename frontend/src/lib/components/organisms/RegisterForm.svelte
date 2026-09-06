<script lang="ts">
  import { enhance } from "$app/forms";
  import Button from "$lib/components/atoms/Button/Button.svelte";
  import FormField from "$lib/components/molecules/FormField/FormField.svelte";
  import FormHeader from "$lib/components/molecules/FormHeader/FormHeader.svelte";
  import FormFooter from "$lib/components/molecules/FormFooter/FormFooter.svelte";
  import Card from "$lib/components/layouts/Card/Card.svelte";

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
    title="Crie sua conta"
    description="Comece sua jornada na UniLaunch"
  />

  <form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-4">
    {#if form?.error}
      <div
        class="p-3 text-xs rounded-lg bg-destructive/10 border border-destructive/20 text-destructive font-medium"
        role="alert"
      >
        {form.error}
      </div>
    {/if}

    <FormField
      id="nome"
      name="nome"
      label="Nome"
      placeholder="Seu nome"
      autocomplete="name"
      value={form?.nome ?? ""}
      required
    />

    <FormField
      id="email"
      name="email"
      label="E-mail"
      type="email"
      placeholder="seu@email.com"
      autocomplete="email"
      value={form?.email ?? ""}
      required
    />

    <FormField
      id="password"
      name="password"
      label="Senha"
      type="password"
      placeholder="Mínimo de 8 caracteres"
      autocomplete="new-password"
      minlength={8}
      required
    />

    <Button type="submit" size="lg" class="w-full mt-2" disabled={submitting}>
      {submitting ? "Criando conta..." : "Criar conta"}
    </Button>
  </form>

  <FormFooter
    text="Já possui uma conta?"
    linkLabel="Entrar"
    linkHref="/login"
  />
</Card>