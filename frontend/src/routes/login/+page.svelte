<script lang="ts">
  import CenteredContent from "$lib/components/layouts/CenteredContent/CenteredContent.svelte";
  import BrandLogoSection from "$lib/components/organisms/BrandLogoSection/BrandLogoSection.svelte";
  import LoginForm from "$lib/components/organisms/LoginForm/LoginForm.svelte";

  let { form } = $props();
</script>

<svelte:head>
  <title>Entrar | UniLaunch</title>
  <meta
    name="description"
    content="Entre na sua conta UniLaunch para continuar."
  />
</svelte:head>

<CenteredContent>
  <BrandLogoSection subtitle="Plataforma de Colaboração Acadêmica" />
  <LoginForm {form} />
</CenteredContent>
