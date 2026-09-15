<script lang="ts">
	type Props = {
		id?: string;
		name?: string;
		value?: string;
		label?: string;
	};

	let {
		id = 'semester_number',
		name = 'semester_number',
		value = $bindable(''),
		label = 'Semestre atual'
	}: Props = $props();
</script>

<label class="flex w-full flex-col gap-1.5" for={id}>
	<span class="text-[0.92rem] font-semibold text-foreground">{label}</span>
	<select
		{id}
		{name}
		bind:value
		class="h-11 rounded-md border border-border bg-input-background px-3 text-sm text-foreground outline-hidden transition-all duration-150 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
	>
		<option value="">Não informado</option>
		{#each Array.from({ length: 12 }, (_, index) => index + 1) as semester}
			<option value={String(semester)}>{semester}º semestre</option>
		{/each}
	</select>
</label>
