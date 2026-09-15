<script lang="ts">
	import { enhance } from '$app/forms';
	import Card from '$lib/components/layouts/Card/Card.svelte';
	import FormAlert from '$lib/components/molecules/FormAlert/FormAlert.svelte';
	import FormButton from '$lib/components/molecules/FormButton/FormButton.svelte';
	import FormCheckbox from '$lib/components/molecules/FormCheckbox/FormCheckbox.svelte';
	import FormField from '$lib/components/molecules/FormField/FormField.svelte';
	import Typography from '$lib/components/atoms/Typography/Typography.svelte';
	import { trackFormSubmission } from '$lib/forms';
	import type { LeadFormValues } from '$lib/lead-form';

	type LeadFormState = { error?: string; success?: boolean; values?: LeadFormValues } | null;
	let { form }: { form: LeadFormState } = $props();
	let submitting = $state(false);
	const handleSubmit = trackFormSubmission((value) => (submitting = value));
</script>

<Card style="max-width: min(68rem, 100%);" class="overflow-hidden border-primary/25 bg-card/95 p-0 shadow-[0_24px_80px_rgba(0,0,0,0.42),0_0_0_1px_rgba(124,58,237,0.06)] backdrop-blur-xl">
	<div class="grid lg:grid-cols-[0.9fr_1.1fr]">
		<section class="relative min-h-96 overflow-hidden border-b border-border bg-card lg:min-h-[46rem] lg:border-r lg:border-b-0">
			<img src="https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1200&q=85" alt="Equipe reunida em uma dinâmica de planejamento" class="absolute inset-0 size-full object-cover" />
			<div aria-hidden="true" class="absolute inset-0 bg-linear-to-t from-[#08091a] via-[#08091a]/35 to-primary/10"></div>
			<div class="absolute inset-x-0 bottom-0 p-6 sm:p-8 lg:p-10">
				<p class="mb-3 text-xs font-bold tracking-[0.18em] text-indigo-300 uppercase">Parcerias feitas por pessoas</p>
				<Typography variant="h1" class="max-w-md text-3xl leading-[1.08] text-white sm:text-4xl">
					Boas ideias crescem quando pessoas se encontram.
				</Typography>
				<p class="mt-4 max-w-md text-sm leading-6 text-slate-200">Queremos entender sua história, seu momento e o impacto que podemos construir juntos.</p>
				<a href="/captura-lead/aluno" class="mt-5 inline-flex w-fit items-center gap-2 text-sm font-semibold text-indigo-200 underline decoration-indigo-300/40 underline-offset-4 transition-colors hover:text-white">
					Procurando oportunidades como estudante? <span aria-hidden="true">→</span>
				</a>
			</div>
		</section>

		<section class="p-5 sm:p-8 lg:p-10">
			{#if form?.success}
				<div class="flex min-h-80 flex-col items-center justify-center text-center" role="status" tabindex="-1">
					<div class="mb-5 flex size-14 items-center justify-center rounded-full border border-emerald-400/25 bg-emerald-400/10 text-emerald-300 shadow-[0_0_30px_rgba(52,211,153,0.12)]">
						<svg class="size-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
							<path d="m5 12 4 4L19 6" />
						</svg>
					</div>
					<h2 class="text-xl font-bold text-foreground">Mensagem recebida</h2>
					<p class="mt-2 max-w-sm text-sm leading-6 text-muted">Obrigado pelo interesse. Nossa equipe entrará em contato em breve.</p>
				</div>
			{:else}
				<div class="mb-6 flex items-end justify-between gap-4">
					<div>
						<h2 class="text-xl font-bold tracking-tight text-foreground">Conte sobre você</h2>
						<p class="mt-1 text-sm text-muted">Leva menos de dois minutos.</p>
					</div>
					<span class="shrink-0 text-xs text-muted-foreground"><span class="text-destructive">*</span> obrigatórios</span>
				</div>

				<form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-5" aria-busy={submitting}>
					{#if form?.error}
						<div id="lead-form-error"><FormAlert message={form.error} class="p-4 text-sm" /></div>
					{/if}

					<div class="grid gap-4 sm:grid-cols-2">
						<FormField class="[&_input]:h-11" id="full_name" name="full_name" label="Nome completo" autocomplete="name" value={form?.values?.full_name ?? ''} required />
						<FormField class="[&_input]:h-11" id="email" name="email" label="E-mail profissional" type="email" autocomplete="email" value={form?.values?.email ?? ''} required />
						<FormField class="[&_input]:h-11" id="company_name" name="company_name" label="Empresa" autocomplete="organization" value={form?.values?.company_name ?? ''} required />
						<FormField class="[&_input]:h-11" id="job_title" name="job_title" label="Cargo" autocomplete="organization-title" value={form?.values?.job_title ?? ''} />

						<label class="flex flex-col gap-1.5" for="company_size">
							<span class="text-[0.92rem] font-semibold text-foreground">Tamanho da empresa</span>
							<select id="company_size" name="company_size" value={form?.values?.company_size ?? ''} class="h-11 rounded-md border border-border bg-input-background px-3 text-sm text-foreground outline-hidden transition-all duration-150 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
								<option value="">Selecione</option>
								<option value="1-10">1 a 10</option>
								<option value="11-50">11 a 50</option>
								<option value="51-200">51 a 200</option>
								<option value="201-500">201 a 500</option>
								<option value="501+">501 ou mais</option>
							</select>
						</label>

						<FormField class="[&_input]:h-11" id="website" name="website" label="Site" type="url" autocomplete="url" placeholder="https://" value={form?.values?.website ?? ''} />
					</div>

					<label class="flex flex-col gap-1.5" for="message">
						<span class="text-[0.92rem] font-semibold text-foreground">Como podemos ajudar?</span>
						<textarea id="message" name="message" rows="4" maxlength="2000" placeholder="Compartilhe seu desafio, objetivo ou ideia." class="min-h-28 resize-y rounded-md border border-border bg-input-background px-3 py-3 text-sm text-foreground outline-hidden transition-all duration-150 placeholder:text-muted-foreground focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">{form?.values?.message ?? ''}</textarea>
					</label>

					<FormCheckbox class="rounded-xl border border-border bg-input-background/50 p-4" id="privacy_consent" name="privacy_consent" checked={form?.values?.privacy_consent ?? false} required>
						<span class="text-sm leading-5 text-slate-300">Li e aceito a <a href="/politica-privacidade" target="_blank" rel="noreferrer" class="font-semibold text-indigo-300 underline decoration-indigo-300/40 underline-offset-2 transition-colors hover:text-indigo-200">política de privacidade</a>.</span>
					</FormCheckbox>
					<FormButton {submitting} loadingText="Enviando..." class="mt-0 h-12">Enviar para análise</FormButton>
				</form>
			{/if}
		</section>
	</div>
</Card>
