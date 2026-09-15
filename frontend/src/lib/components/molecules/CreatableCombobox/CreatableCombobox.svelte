<script lang="ts">
	export type CatalogOption = { id: string; name: string };

	type Props = {
		id: string;
		idName: string;
		name: string;
		label: string;
		endpoint: string;
		value?: string;
		selectedId?: string;
		initialOptions?: CatalogOption[];
		placeholder?: string;
		description?: string;
		required?: boolean;
	};

	let {
		id,
		idName,
		name,
		label,
		endpoint,
		value = $bindable(''),
		selectedId = $bindable(''),
		initialOptions = [],
		placeholder = '',
		description,
		required = false
	}: Props = $props();

	let searchResults = $state<CatalogOption[]>([]);
	let open = $state(false);
	let loading = $state(false);
	let searchError = $state('');
	let activeIndex = $state(-1);
	let requestNumber = 0;

	const listboxId = $derived(`${id}-listbox`);
	const helpId = $derived(`${id}-help`);
	const options = $derived(value.trim().length < 2 ? initialOptions : searchResults);
	const normalizedValue = $derived(value.trim().toLocaleLowerCase('pt-BR'));
	const hasExactOption = $derived(
		options.some((option) => option.name.trim().toLocaleLowerCase('pt-BR') === normalizedValue)
	);
	const canCreate = $derived(normalizedValue.length >= 2 && !hasExactOption && !loading);

	$effect(() => {
		const query = value.trim();
		if (selectedId || query.length < 2) {
			loading = false;
			searchError = '';
			return;
		}

		const currentRequest = ++requestNumber;
		const controller = new AbortController();
		const timer = window.setTimeout(async () => {
			loading = true;
			searchError = '';
			try {
				const response = await fetch(`${endpoint}?q=${encodeURIComponent(query)}`, {
					signal: controller.signal
				});
				if (!response.ok) throw new Error('catalog request failed');
				const result = (await response.json()) as CatalogOption[];
				if (currentRequest === requestNumber) {
					searchResults = result;
					activeIndex = result.length ? 0 : -1;
				}
			} catch (error) {
				if (!(error instanceof DOMException && error.name === 'AbortError') && currentRequest === requestNumber) {
					searchResults = [];
					searchError = 'Não foi possível carregar as opções.';
				}
			} finally {
				if (currentRequest === requestNumber) loading = false;
			}
		}, 250);

		return () => {
			window.clearTimeout(timer);
			controller.abort();
		};
	});

	function selectOption(option: CatalogOption) {
		value = option.name;
		selectedId = option.id;
		open = false;
		activeIndex = -1;
		searchError = '';
	}

	function createOption() {
		selectedId = '';
		value = value.trim();
		open = false;
		activeIndex = -1;
	}

	function handleInput(event: Event) {
		value = (event.currentTarget as HTMLInputElement).value;
		selectedId = '';
		open = true;
		activeIndex = -1;
	}

	function handleKeydown(event: KeyboardEvent) {
		const itemCount = options.length + (canCreate ? 1 : 0);
		if (event.key === 'ArrowDown' && itemCount) {
			event.preventDefault();
			open = true;
			activeIndex = (activeIndex + 1 + itemCount) % itemCount;
		} else if (event.key === 'ArrowUp' && itemCount) {
			event.preventDefault();
			open = true;
			activeIndex = (activeIndex - 1 + itemCount) % itemCount;
		} else if (event.key === 'Enter' && open && activeIndex >= 0) {
			event.preventDefault();
			if (activeIndex < options.length) selectOption(options[activeIndex]);
			else createOption();
		} else if (event.key === 'Escape') {
			open = false;
			activeIndex = -1;
		}
	}
</script>

<div class="relative flex w-full flex-col gap-1.5">
	<label for={id} class="inline-flex w-fit cursor-pointer items-center gap-1 text-[0.92rem] font-semibold text-foreground">
		{label}
		{#if required}<span class="text-xs font-bold text-destructive" title="Campo obrigatório">*</span>{/if}
	</label>
	{#if selectedId}
		<input type="hidden" name={idName} value={selectedId} />
		<input type="hidden" name={`${name}_display`} value={value} />
	{/if}
	<input
		{id}
		name={selectedId ? undefined : name}
		type="text"
		role="combobox"
		autocomplete="off"
		aria-autocomplete="list"
		aria-expanded={open}
		aria-controls={listboxId}
		aria-activedescendant={open && activeIndex >= 0 ? `${id}-option-${activeIndex}` : undefined}
		aria-describedby={description || searchError ? helpId : undefined}
		aria-invalid={searchError ? 'true' : undefined}
		{placeholder}
		{required}
		value={value}
		oninput={handleInput}
		onfocus={() => (open = !selectedId && (value.trim().length >= 2 || options.length > 0))}
		onblur={() => window.setTimeout(() => (open = false), 120)}
		onkeydown={handleKeydown}
		class="h-11 w-full rounded-md border border-border bg-input-background px-3 pr-10 text-sm text-foreground outline-hidden transition-all duration-150 placeholder:text-muted-foreground focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
	/>
	<span aria-hidden="true" class="pointer-events-none absolute right-3 top-10 text-xs text-muted-foreground">
		{loading ? '...' : '⌄'}
	</span>

	{#if open && (loading || options.length || canCreate || searchError)}
		<div id={listboxId} role="listbox" class="absolute top-full z-30 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-border bg-card p-1 shadow-2xl">
			{#if loading}
				<p class="px-3 py-2 text-sm text-muted" role="status">Buscando...</p>
			{:else}
				{#each options as option, index (option.id)}
					<button
						id={`${id}-option-${index}`}
						type="button"
						role="option"
						aria-selected={activeIndex === index}
						onmousedown={(event) => event.preventDefault()}
						onclick={() => selectOption(option)}
						class={`flex w-full rounded-md px-3 py-2 text-left text-sm text-foreground transition-colors hover:bg-primary/10 ${activeIndex === index ? '!bg-primary/15' : ''}`}
					>
						{option.name}
					</button>
				{/each}
				{#if canCreate}
					<button
						id={`${id}-option-${options.length}`}
						type="button"
						role="option"
						aria-selected={activeIndex === options.length}
						onmousedown={(event) => event.preventDefault()}
						onclick={createOption}
						class={`flex w-full flex-col rounded-md px-3 py-2 text-left text-sm text-cyan-200 transition-colors hover:bg-cyan-400/10 ${activeIndex === options.length ? '!bg-cyan-400/15' : ''}`}
					>
						<span>Adicionar “{value.trim()}”</span>
						<span class="text-xs text-muted">O nome será revisado pela UniLaunch.</span>
					</button>
				{/if}
			{/if}
		</div>
	{/if}

	{#if description || searchError}
		<p id={helpId} class:text-destructive={searchError} class="text-xs text-muted-foreground" aria-live="polite">
			{searchError || description}
		</p>
	{/if}
</div>
