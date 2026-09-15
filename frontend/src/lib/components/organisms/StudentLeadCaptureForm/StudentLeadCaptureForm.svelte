<script lang="ts">
	import { enhance } from '$app/forms';
	import Typography from '$lib/components/atoms/Typography/Typography.svelte';
	import Card from '$lib/components/layouts/Card/Card.svelte';
	import FormAlert from '$lib/components/molecules/FormAlert/FormAlert.svelte';
	import FormButton from '$lib/components/molecules/FormButton/FormButton.svelte';
	import FormCheckbox from '$lib/components/molecules/FormCheckbox/FormCheckbox.svelte';
	import FormField from '$lib/components/molecules/FormField/FormField.svelte';
	import { trackFormSubmission } from '$lib/forms';
	import type { StudentLeadFormValues } from '$lib/lead-form';

	type StudentLeadFormState = { error?: string; success?: boolean; values?: StudentLeadFormValues } | null;
	let { form }: { form: StudentLeadFormState } = $props();
	let submitting = $state(false);
	const handleSubmit = trackFormSubmission((value) => (submitting = value));
</script>

<Card style="max-width: min(68rem, 100%);" class="overflow-hidden border-primary/25 bg-card/95 p-0 shadow-[0_24px_80px_rgba(0,0,0,0.42),0_0_0_1px_rgba(124,58,237,0.06)] backdrop-blur-xl">
	<div class="grid lg:grid-cols-[0.9fr_1.1fr]">
		<section class="relative min-h-96 overflow-hidden border-b border-border bg-card lg:min-h-[53rem] lg:border-r lg:border-b-0">
			<img src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=85" alt="Estudantes sorrindo e colaborando em torno de uma mesa" class="absolute inset-0 size-full object-cover" />
			<div aria-hidden="true" class="absolute inset-0 bg-linear-to-t from-[#08091a] via-[#08091a]/35 to-accent/10"></div>
			<div class="absolute inset-x-0 bottom-0 p-6 sm:p-8 lg:p-10">
				<p class="mb-3 text-xs font-bold tracking-[0.18em] text-cyan-300 uppercase">Talento encontra oportunidade</p>
				<Typography variant="h1" class="max-w-md text-3xl leading-[1.08] text-white sm:text-4xl">
					Toda carreira começa com alguém acreditando no seu potencial.
				</Typography>
				<p class="mt-4 max-w-md text-sm leading-6 text-slate-200">Queremos conhecer o que move você e conectar essa vontade a experiências que importam.</p>
				<a href="/captura-lead" class="mt-5 inline-flex w-fit items-center gap-2 text-sm font-semibold text-cyan-100 underline decoration-cyan-300/40 underline-offset-4 transition-colors hover:text-white">
					Quer conversar sobre sua empresa? <span aria-hidden="true">→</span>
				</a>
			</div>
		</section>

		<section class="p-5 sm:p-8 lg:p-10">
			{#if form?.success}
				<div class="flex min-h-80 flex-col items-center justify-center text-center" role="status" tabindex="-1">
					<div class="mb-5 flex size-14 items-center justify-center rounded-full border border-emerald-400/25 bg-emerald-400/10 text-emerald-300 shadow-[0_0_30px_rgba(52,211,153,0.12)]">
						<svg class="size-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>
					</div>
					<h2 class="text-xl font-bold text-foreground">Perfil recebido</h2>
					<p class="mt-2 max-w-sm text-sm leading-6 text-muted">Obrigado pelo interesse. Avisaremos quando encontrarmos uma oportunidade compatível.</p>
				</div>
			{:else}
				<div class="mb-6 flex items-end justify-between gap-4">
					<div><h2 class="text-xl font-bold tracking-tight text-foreground">Conte sobre sua jornada</h2><p class="mt-1 text-sm text-muted">Leva menos de dois minutos.</p></div>
					<span class="shrink-0 text-xs text-muted-foreground"><span class="text-destructive">*</span> obrigatórios</span>
				</div>

				<form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-5" aria-busy={submitting}>
					{#if form?.error}<div id="student-lead-form-error"><FormAlert message={form.error} class="p-4 text-sm" /></div>{/if}
					<div class="grid gap-4 sm:grid-cols-2">
						<FormField class="[&_input]:h-11" id="full_name" name="full_name" label="Nome completo" autocomplete="name" value={form?.values?.full_name ?? ''} required />
						<FormField class="[&_input]:h-11" id="email" name="email" label="E-mail" type="email" autocomplete="email" value={form?.values?.email ?? ''} required />
						<FormField class="[&_input]:h-11" id="institution_name" name="institution_name" label="Instituição de ensino" autocomplete="organization" value={form?.values?.institution_name ?? ''} required />
						<FormField class="[&_input]:h-11" id="course_name" name="course_name" label="Curso" value={form?.values?.course_name ?? ''} required />
						<FormField class="[&_input]:h-11" id="semester" name="semester" label="Semestre ou período" placeholder="Ex.: 4º semestre" value={form?.values?.semester ?? ''} />
						<label class="flex flex-col gap-1.5" for="area_of_interest">
							<span class="text-[0.92rem] font-semibold text-foreground">Área de interesse</span>
							<select id="area_of_interest" name="area_of_interest" value={form?.values?.area_of_interest ?? ''} class="h-11 rounded-md border border-border bg-input-background px-3 text-sm text-foreground outline-hidden transition-all duration-150 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
								<option value="">Selecione</option><option value="Frontend">Frontend</option><option value="Backend">Backend</option><option value="Dados e IA">Dados e IA</option><option value="UX/UI">UX/UI</option><option value="Produto">Produto</option><option value="DevOps">DevOps</option><option value="Ainda estou explorando">Ainda estou explorando</option>
							</select>
						</label>
						<FormField class="[&_input]:h-11" id="linkedin_url" name="linkedin_url" label="LinkedIn" type="url" autocomplete="url" placeholder="https://linkedin.com/in/..." value={form?.values?.linkedin_url ?? ''} />
						<FormField class="[&_input]:h-11" id="github_url" name="github_url" label="GitHub" type="url" autocomplete="url" placeholder="https://github.com/..." value={form?.values?.github_url ?? ''} />
					</div>
					<label class="flex flex-col gap-1.5" for="message"><span class="text-[0.92rem] font-semibold text-foreground">O que você quer aprender ou construir?</span><textarea id="message" name="message" rows="4" maxlength="2000" placeholder="Conte seus objetivos, experiências ou ideias." class="min-h-28 resize-y rounded-md border border-border bg-input-background px-3 py-3 text-sm text-foreground outline-hidden transition-all duration-150 placeholder:text-muted-foreground focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">{form?.values?.message ?? ''}</textarea></label>
					<FormCheckbox class="rounded-xl border border-border bg-input-background/50 p-4" id="privacy_consent" name="privacy_consent" checked={form?.values?.privacy_consent ?? false} required>
						<span class="text-sm leading-5 text-slate-300">Li e aceito a <a href="/politica-privacidade" target="_blank" rel="noreferrer" class="font-semibold text-indigo-300 underline decoration-indigo-300/40 underline-offset-2 transition-colors hover:text-indigo-200">política de privacidade</a>.</span>
					</FormCheckbox>
					<FormButton {submitting} loadingText="Enviando..." class="mt-0 h-12">Quero participar</FormButton>
				</form>
			{/if}
		</section>
	</div>
</Card>
