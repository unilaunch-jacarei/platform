<script lang="ts">
	import CenteredContent from '$lib/components/layouts/CenteredContent/CenteredContent.svelte';
	import BrandLogoSection from '$lib/components/organisms/BrandLogoSection/BrandLogoSection.svelte';
	import StudentLeadCaptureForm from '$lib/components/organisms/StudentLeadCaptureForm/StudentLeadCaptureForm.svelte';

	let { form } = $props();
</script>

<svelte:head>
	<title>Oportunidades para estudantes | UniLaunch</title>
	<meta name="description" content="Cadastre seu interesse em construir experiência com projetos reais." />
</svelte:head>

<CenteredContent class="justify-start overflow-y-auto px-4 py-8 sm:px-6 sm:py-12 lg:justify-center">
	<div aria-hidden="true" class="pointer-events-none absolute -top-40 left-1/2 size-96 -translate-x-1/2 rounded-full bg-accent/15 blur-3xl"></div>
	<div aria-hidden="true" class="pointer-events-none absolute right-0 bottom-0 size-80 translate-x-1/3 translate-y-1/3 rounded-full bg-cyan-400/10 blur-3xl"></div>
	<div class="relative z-10 flex w-full flex-col items-center">
		<BrandLogoSection subtitle="Experiência real para quem está começando" class="[&>div]:mb-6 sm:[&>div]:mb-8" />
		<StudentLeadCaptureForm {form} />
	</div>
</CenteredContent>
