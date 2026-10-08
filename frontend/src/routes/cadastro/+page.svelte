<script lang="ts">
  import CenteredContent from "$lib/components/layouts/CenteredContent/CenteredContent.svelte";
  import BrandLogoSection from "$lib/components/organisms/BrandLogoSection/BrandLogoSection.svelte";
  import RegisterForm from "$lib/components/organisms/RegisterForm/RegisterForm.svelte";

  let { form } = $props();
</script>

<svelte:head>
  <title>Criar conta | UniLaunch</title>
</svelte:head>

<CenteredContent>
  <BrandLogoSection />
  <RegisterForm {form} />
</CenteredContent>
