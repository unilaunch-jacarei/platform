<script lang="ts">
	export type InterestAreaOption = { id: string; code: string; name: string };

	type Props = {
		name: string;
		options: InterestAreaOption[];
		selectedIds?: string[];
		max?: number;
		legend?: string;
		description?: string;
	};

	let {
		name,
		options,
		selectedIds = $bindable([]),
		max = 3,
		legend = 'Áreas de interesse',
		description = 'Escolha até três áreas.'
	}: Props = $props();

	const selected = $derived(new Set(selectedIds));
	const atLimit = $derived(selectedIds.length >= max);

	function toggle(optionId: string, checked: boolean) {
		if (checked && !selected.has(optionId) && selectedIds.length < max) {
			selectedIds = [...selectedIds, optionId];
		} else if (!checked) {
			selectedIds = selectedIds.filter((id) => id !== optionId);
		}
	}
</script>

<fieldset class="flex min-w-0 flex-col gap-2">
	<div class="flex items-end justify-between gap-3">
		<div>
			<legend class="text-[0.92rem] font-semibold text-foreground">{legend}</legend>
			<p class="text-xs text-muted-foreground">{description}</p>
		</div>
		<span class:text-cyan-200={atLimit} class="shrink-0 text-xs text-muted" aria-live="polite">
			{selectedIds.length}/{max}
		</span>
	</div>
	<div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
		{#each options as option (option.id)}
			<label class={`flex min-h-11 cursor-pointer items-center gap-2 rounded-lg border border-border bg-input-background/60 px-3 py-2 text-sm text-slate-200 transition-colors has-focus-visible:ring-2 has-focus-visible:ring-ring has-focus-visible:ring-offset-2 has-disabled:cursor-not-allowed has-disabled:opacity-45 ${selected.has(option.id) ? '!border-primary !bg-primary/10' : ''}`}>
				<input
					type="checkbox"
					{name}
					value={option.id}
					checked={selected.has(option.id)}
					disabled={atLimit && !selected.has(option.id)}
					onchange={(event) => toggle(option.id, event.currentTarget.checked)}
					class="size-4 shrink-0 accent-primary"
				/>
				<span>{option.name}</span>
			</label>
		{/each}
	</div>
	{#if !options.length}
		<p class="rounded-lg border border-dashed border-border px-3 py-3 text-sm text-muted">
			As áreas de interesse não estão disponíveis no momento.
		</p>
	{/if}
</fieldset>
