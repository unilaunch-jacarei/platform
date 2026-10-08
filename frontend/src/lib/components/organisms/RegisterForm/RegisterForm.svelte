<script lang="ts">
  import { enhance } from "$app/forms";
  import FormField from "$lib/components/molecules/FormField/FormField.svelte";
  import FormHeader from "$lib/components/molecules/FormHeader/FormHeader.svelte";
  import FormFooter from "$lib/components/molecules/FormFooter/FormFooter.svelte";
  import Card from "$lib/components/layouts/Card/Card.svelte";
  import FormAlert from "$lib/components/molecules/FormAlert/FormAlert.svelte";
  import FormButton from "$lib/components/molecules/FormButton/FormButton.svelte";
  import { trackFormSubmission, type FormState } from "$lib/forms";

  let submitting = $state(false);
  let { form }: { form: FormState } = $props();

  const handleSubmit = trackFormSubmission((value) => (submitting = value));
</script>

<Card class="w-full max-w-[400px]">
  <FormHeader
    title="Crie sua conta"
    description="Comece sua jornada na UniLaunch"
  />

  <form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-4">
    {#if form?.error}
      <FormAlert message={form.error} />
    {/if}

    <FormField
      id="nome"
      name="nome"
      label="Nome Completo"
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
      placeholder="••••••••"
      autocomplete="new-password"
      minlength={8}
      error={form?.errors?.passwordConfirmation}
      required
    />

    <FormField
      id="passwordConfirmation"
      name="passwordConfirmation"
      label="Confirmar Senha"
      type="password"
      placeholder="••••••••"
      autocomplete="new-password"
      minlength={8}
      required
    />

    <FormButton {submitting} loadingText="Criando conta...">Criar conta</FormButton>
  </form>

  <FormFooter
    text="Já possui uma conta?"
    linkLabel="Entrar"
    linkHref="/login"
  />
</Card>
