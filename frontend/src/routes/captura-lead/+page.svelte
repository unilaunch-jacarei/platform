<script lang="ts">
	import CenteredContent from '$lib/components/layouts/CenteredContent/CenteredContent.svelte';
	import BrandLogoSection from '$lib/components/organisms/BrandLogoSection/BrandLogoSection.svelte';
	import LeadCaptureForm from '$lib/components/organisms/LeadCaptureForm/LeadCaptureForm.svelte';

	let { form } = $props();
</script>

<svelte:head>
	<title>Fale com a UniLaunch</title>
	<meta name="description" content="Entre em contato com a UniLaunch." />
</svelte:head>

<CenteredContent class="gap-6 py-10 sm:py-16">
	<BrandLogoSection subtitle="Vamos conversar sobre sua empresa" />
	<LeadCaptureForm {form} />
</CenteredContent>
