<script lang="ts">
  import { enhance } from "$app/forms";
  import FormField from "$lib/components/molecules/FormField/FormField.svelte";
  import FormHeader from "$lib/components/molecules/FormHeader/FormHeader.svelte";
  import FormFooter from "$lib/components/molecules/FormFooter/FormFooter.svelte";
  import FormCheckbox from "../../molecules/FormCheckbox/FormCheckbox.svelte";
  import Card from "../../layouts/Card/Card.svelte";
  import FormButton from "$lib/components/molecules/FormButton/FormButton.svelte";
  import FormAlert from "$lib/components/molecules/FormAlert/FormAlert.svelte";
  import { trackFormSubmission, type FormState } from "$lib/forms";

  let submitting = $state(false);
  let { form }: { form: FormState } = $props();

  const handleSubmit = trackFormSubmission((value) => (submitting = value));
</script>

<Card class="w-full max-w-[400px]">
  <FormHeader
    title="Bem-vindo de volta"
    description="Acesse sua conta para continuar"
  />

  <form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-4">
    {#if form?.error}
      <FormAlert message={form.error} />
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

    <FormButton {submitting} loadingText="Entrando...">Entrar →</FormButton>
  </form>

  <FormFooter
    text="Não tem conta?"
    linkLabel="Criar nova conta"
    linkHref="/cadastro"
  />
</Card>
