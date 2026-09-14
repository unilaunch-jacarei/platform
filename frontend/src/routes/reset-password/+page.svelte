<script lang="ts">
  import { enhance } from "$app/forms";
  import CenteredContent from "$lib/components/layouts/CenteredContent/CenteredContent.svelte";
  import Card from "$lib/components/layouts/Card/Card.svelte";
  import BrandLogoSection from "$lib/components/organisms/BrandLogoSection/BrandLogoSection.svelte";
  import BackLink from "$lib/components/molecules/BackLink/BackLink.svelte";
  import FormAlert from "$lib/components/molecules/FormAlert/FormAlert.svelte";
  import FormButton from "$lib/components/molecules/FormButton/FormButton.svelte";
  import FormField from "$lib/components/molecules/FormField/FormField.svelte";
  import FormHeader from "$lib/components/molecules/FormHeader/FormHeader.svelte";
  import { trackFormSubmission } from "$lib/forms";

  let { data, form } = $props();
  let submitting = $state(false);
  const handleSubmit = trackFormSubmission((value) => (submitting = value));
</script>

<svelte:head>
  <title>Nova senha | UniLaunch</title>
  <meta name="description" content="Crie uma nova senha para sua conta UniLaunch." />
</svelte:head>

<CenteredContent>
  <BrandLogoSection subtitle="Plataforma de Colaboração Acadêmica" />
  <Card class="w-full max-w-[420px]">
    <BackLink href="/login" label="Voltar ao login" />
    <FormHeader title="Crie uma nova senha" description="Use pelo menos 8 caracteres." />

    <form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-4">
      <input type="hidden" name="token" value={data.token} />

      {#if !data.token}
        <FormAlert message="O link de recuperação não contém um token válido." />
      {:else if form?.error}
        <FormAlert message={form.error} />
      {/if}

      <FormField
        id="password"
        name="password"
        type="password"
        label="Nova senha"
        autocomplete="new-password"
        minlength={8}
        required
      />
      <FormField
        id="confirmation"
        name="confirmation"
        type="password"
        label="Confirme a nova senha"
        autocomplete="new-password"
        minlength={8}
        error={form?.errors?.confirmation}
        required
      />
      <FormButton {submitting} disabled={!data.token} loadingText="Salvando...">
        Salvar nova senha
      </FormButton>
    </form>
  </Card>
</CenteredContent>
