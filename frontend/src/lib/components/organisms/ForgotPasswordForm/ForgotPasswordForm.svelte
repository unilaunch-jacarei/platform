<!-- src/lib/components/organisms/ForgotPasswordForm/ForgotPasswordForm.svelte -->
<script lang="ts">
  import { enhance } from "$app/forms";
  import Card from "$lib/components/layouts/Card/Card.svelte";
  import BackLink from "$lib/components/molecules/BackLink/BackLink.svelte";
  import IconFormHeader from "$lib/components/molecules/IconFormHeader/IconFormHeader.svelte";
  import FormAlert from "$lib/components/molecules/FormAlert/FormAlert.svelte";
  import FormField from "$lib/components/molecules/FormField/FormField.svelte";
  import FormButton from "$lib/components/molecules/FormButton/FormButton.svelte";
  import MailIcon from "$lib/components/atoms/MailIcon/MailIcon.svelte";
  import { trackFormSubmission, type FormState } from "$lib/forms";

  let submitting = $state(false);
  let { form }: { form: FormState } = $props();

  const handleSubmit = trackFormSubmission((value) => (submitting = value));
</script>

<Card class="w-full max-w-[420px] p-8 flex flex-col gap-6">
  <BackLink href="/login" label="Voltar ao login" />

  <IconFormHeader
    title="Recuperar senha"
    description="Informe seu e-mail e, se houver uma conta, enviaremos as instruções."
  >
    {#snippet icon()}
      <MailIcon />
    {/snippet}
  </IconFormHeader>

  <form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-5">
    {#if form?.error}
      <FormAlert variant="error" message={form.error} />
    {/if}

    {#if form?.success}
      <FormAlert
        variant="success"
        message={form.message ?? "Se existir uma conta com esse e-mail, você receberá as instruções."}
      />
    {/if}

    <FormField
      id="email"
      name="email"
      label="E-mail cadastrado"
      type="email"
      placeholder="seu@email.com"
      error={form?.errors?.email}
      required
    />

    <FormButton {submitting} loadingText="Enviando...">
      Enviar link de recuperação →
    </FormButton>
  </form>
</Card>
