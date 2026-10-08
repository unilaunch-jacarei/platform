<script lang="ts">
	import { enhance } from '$app/forms';
	import Typography from '$lib/components/atoms/Typography/Typography.svelte';
	import Card from '$lib/components/layouts/Card/Card.svelte';
	import FormAlert from '$lib/components/molecules/FormAlert/FormAlert.svelte';
	import FormButton from '$lib/components/molecules/FormButton/FormButton.svelte';
	import FormCheckbox from '$lib/components/molecules/FormCheckbox/FormCheckbox.svelte';
	import FormField from '$lib/components/molecules/FormField/FormField.svelte';
	import CreatableCombobox from '$lib/components/molecules/CreatableCombobox/CreatableCombobox.svelte';
	import InterestAreaMultiSelect from '$lib/components/molecules/InterestAreaMultiSelect/InterestAreaMultiSelect.svelte';
	import SemesterSelect from '$lib/components/molecules/SemesterSelect/SemesterSelect.svelte';
	import { trackFormSubmission } from '$lib/forms';
	import type { InterestAreaOption, StudentLeadFormValues } from '$lib/lead-form';

	type StudentLeadFormState = { error?: string; success?: boolean; values?: StudentLeadFormValues } | null;
	let {
		form,
		interestAreas = [],
		catalogError = ''
	}: { form: StudentLeadFormState; interestAreas?: InterestAreaOption[]; catalogError?: string } = $props();
	let submitting = $state(false);
	const handleSubmit = trackFormSubmission((value) => (submitting = value));
</script>

<Card style="max-width: min(64rem, 100%);" class="overflow-hidden border-primary/25 bg-card/95 p-0 shadow-[0_24px_80px_rgba(0,0,0,0.42),0_0_0_1px_rgba(124,58,237,0.06)] backdrop-blur-xl">
	<div class="grid lg:grid-cols-[0.72fr_1.28fr]">
		<section class="relative overflow-hidden border-b border-border bg-linear-to-br from-accent/20 via-card to-cyan-400/10 p-6 sm:p-8 lg:border-r lg:border-b-0 lg:p-10">
			<div aria-hidden="true" class="absolute -top-20 -left-20 size-56 rounded-full bg-accent/20 blur-3xl"></div>
			<div class="relative flex h-full flex-col">
				<p class="mb-4 text-xs font-bold tracking-[0.18em] text-cyan-300 uppercase">Comece construindo</p>
				<Typography variant="h1" class="max-w-sm text-3xl leading-[1.05] sm:text-4xl lg:text-[2.7rem]">
					Seu talento em projetos reais.
				</Typography>
				<p class="mt-4 max-w-sm text-sm leading-6 text-slate-300">
					Apresente sua jornada e seus interesses para conectarmos você às oportunidades certas.
				</p>
				<a href="/captura-lead" class="mt-5 inline-flex w-fit items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1.5 text-xs font-semibold text-cyan-100 transition-colors hover:border-cyan-300/40 hover:bg-cyan-300/15">
					Represento uma empresa <span aria-hidden="true">→</span>
				</a>

				<div class="mt-7 grid gap-3 sm:grid-cols-3 lg:mt-auto lg:grid-cols-1 lg:pt-10">
					<div class="flex items-center gap-3 text-sm text-slate-200"><span class="flex size-7 shrink-0 items-center justify-center rounded-full border border-cyan-300/30 bg-cyan-300/10 text-xs font-bold text-cyan-200">1</span><span>Compartilhe seu perfil</span></div>
					<div class="flex items-center gap-3 text-sm text-slate-200"><span class="flex size-7 shrink-0 items-center justify-center rounded-full border border-cyan-300/30 bg-cyan-300/10 text-xs font-bold text-cyan-200">2</span><span>Mapeamos seus interesses</span></div>
					<div class="flex items-center gap-3 text-sm text-slate-200"><span class="flex size-7 shrink-0 items-center justify-center rounded-full border border-cyan-300/30 bg-cyan-300/10 text-xs font-bold text-cyan-200">3</span><span>Conectamos oportunidades</span></div>
				</div>
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
						<CreatableCombobox id="institution" idName="institution_id" name="institution_name" label="Instituição de ensino" endpoint="/api/leads/catalog/institutions" value={form?.values?.institution_name_display || form?.values?.institution_name || ''} selectedId={form?.values?.institution_id || ''} placeholder="Digite para buscar" description="Se não encontrar, adicione o nome para revisão." required />
						<CreatableCombobox id="course" idName="course_id" name="course_name" label="Curso" endpoint="/api/leads/catalog/courses" value={form?.values?.course_name_display || form?.values?.course_name || ''} selectedId={form?.values?.course_id || ''} placeholder="Digite para buscar" description="Se não encontrar, adicione o nome para revisão." required />
						<SemesterSelect value={form?.values?.semester_number ?? ''} />
						<FormField class="[&_input]:h-11" id="linkedin_url" name="linkedin_url" label="LinkedIn" type="url" autocomplete="url" placeholder="https://linkedin.com/in/..." value={form?.values?.linkedin_url ?? ''} />
						<FormField class="[&_input]:h-11" id="github_url" name="github_url" label="GitHub" type="url" autocomplete="url" placeholder="https://github.com/..." value={form?.values?.github_url ?? ''} />
						<div class="sm:col-span-2">
							<InterestAreaMultiSelect name="interest_area_ids" options={interestAreas} selectedIds={form?.values?.interest_area_ids ?? []} />
							{#if catalogError}<p class="mt-2 text-xs text-destructive" role="status">{catalogError}</p>{/if}
						</div>
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
