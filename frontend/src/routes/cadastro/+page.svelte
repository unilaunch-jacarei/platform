<script lang="ts">
  import CenteredContent from "$lib/components/layouts/CenteredContent/CenteredContent.svelte";
  import RegisterForm from "$lib/components/organisms/RegisterForm.svelte";

  let { form } = $props();
</script>

<svelte:head>
  <title>Criar conta | UniLaunch</title>
</svelte:head>

<CenteredContent>
  <RegisterForm {form} />
</CenteredContent>
