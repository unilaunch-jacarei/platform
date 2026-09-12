<script lang="ts">
  import { enhance } from "$app/forms";
  import CenteredContent from "$lib/components/layouts/CenteredContent/CenteredContent.svelte";
  import BrandLogoLoginSection from "$lib/components/organisms/BrandLogoLoginSection/BrandLogoLoginSection.svelte";
  import LoginForm from "$lib/components/organisms/LoginForm/LoginForm.svelte";

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
  <title>Entrar | UniLaunch</title>
  <meta
    name="description"
    content="Entre na sua conta UniLaunch para continuar."
  />
</svelte:head>

<CenteredContent>
  <BrandLogoLoginSection />
  <LoginForm {form} />
</CenteredContent>
