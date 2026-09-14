<script lang="ts">
	import { enhance } from '$app/forms';
	import Card from '$lib/components/layouts/Card/Card.svelte';
	import FormAlert from '$lib/components/molecules/FormAlert/FormAlert.svelte';
	import FormButton from '$lib/components/molecules/FormButton/FormButton.svelte';
	import FormCheckbox from '$lib/components/molecules/FormCheckbox/FormCheckbox.svelte';
	import FormField from '$lib/components/molecules/FormField/FormField.svelte';
	import FormHeader from '$lib/components/molecules/FormHeader/FormHeader.svelte';
	import { trackFormSubmission } from '$lib/forms';
	import type { LeadFormValues } from '$lib/lead-form';

	type LeadFormState = { error?: string; success?: boolean; values?: LeadFormValues } | null;
	let { form }: { form: LeadFormState } = $props();
	let submitting = $state(false);
	const handleSubmit = trackFormSubmission((value) => (submitting = value));
</script>

<Card class="max-w-xl">
	<FormHeader title="Fale com a UniLaunch" description="Conte um pouco sobre você e sua empresa." />

	{#if form?.success}
		<FormAlert variant="success" message="Recebemos seus dados. Em breve entraremos em contato." />
	{:else}
		<form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-4">
			{#if form?.error}<FormAlert message={form.error} />{/if}

			<FormField id="full_name" name="full_name" label="Nome completo" autocomplete="name" value={form?.values?.full_name ?? ''} required />
			<FormField id="email" name="email" label="E-mail" type="email" autocomplete="email" value={form?.values?.email ?? ''} required />
			<FormField id="company_name" name="company_name" label="Empresa" autocomplete="organization" value={form?.values?.company_name ?? ''} required />
			<FormField id="job_title" name="job_title" label="Cargo" value={form?.values?.job_title ?? ''} />

			<label class="flex flex-col gap-1.5">
				<span class="text-[0.92rem] font-semibold text-foreground">Tamanho da empresa</span>
				<select name="company_size" class="h-9 rounded-md border border-border bg-input-background px-3 text-sm text-foreground">
					<option value="">Selecione</option>
					<option value="1-10">1 a 10</option>
					<option value="11-50">11 a 50</option>
					<option value="51-200">51 a 200</option>
					<option value="201-500">201 a 500</option>
					<option value="501+">501 ou mais</option>
				</select>
			</label>

			<FormField id="website" name="website" label="Site" type="url" value={form?.values?.website ?? ''} />
			<label class="flex flex-col gap-1.5">
				<span class="text-[0.92rem] font-semibold text-foreground">Mensagem</span>
				<textarea name="message" rows="4" class="rounded-md border border-border bg-input-background px-3 py-2 text-sm text-foreground">{form?.values?.message ?? ''}</textarea>
			</label>

			<FormCheckbox id="privacy_consent" name="privacy_consent" label="Aceito a política de privacidade." required />
			<FormButton {submitting} loadingText="Enviando...">Enviar meus dados</FormButton>
		</form>
	{/if}
</Card>
