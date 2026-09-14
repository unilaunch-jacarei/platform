<script lang="ts">
  import CenteredContent from "$lib/components/layouts/CenteredContent/CenteredContent.svelte";
  import BrandLogoSection from "$lib/components/organisms/BrandLogoSection/BrandLogoSection.svelte";
  import ForgotPasswordForm from "$lib/components/organisms/ForgotPasswordForm/ForgotPasswordForm.svelte";

  let showPassword = $state(false);
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

<svelte:head>
  <title>Recuperar senha | UniLaunch</title>
  <meta name="description" content="Recupere sua senha da conta UniLaunch." />
</svelte:head>

<CenteredContent>
  <BrandLogoSection subtitle="Plataforma de Colaboração Acadêmica" />
  <ForgotPasswordForm {form} />
</CenteredContent>
