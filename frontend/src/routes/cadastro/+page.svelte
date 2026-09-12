<script lang="ts">
  import CenteredContent from "$lib/components/layouts/CenteredContent/CenteredContent.svelte";
  import BrandLogoRegisterSection from "$lib/components/organisms/BrandLogoRegisterSection/BrandLogoRegisterSection.svelte";
  import RegisterForm from "$lib/components/organisms/RegisterForm/RegisterForm.svelte";

  let { form } = $props();
</script>

<svelte:head>
  <title>Criar conta | UniLaunch</title>
</svelte:head>

<CenteredContent>
  <BrandLogoRegisterSection />
  <RegisterForm {form} />
</CenteredContent>
