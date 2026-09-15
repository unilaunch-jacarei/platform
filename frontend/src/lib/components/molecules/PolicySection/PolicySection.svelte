<script lang="ts">
	import type { Snippet } from 'svelte';

	type PolicySectionProps = {
		id: string;
		number: string;
		title: string;
		children: Snippet;
	};

	let { id, number, title, children }: PolicySectionProps = $props();
</script>

<section {id} class="scroll-mt-24 border-t border-border py-8 first:border-t-0 first:pt-0 sm:py-10">
	<div class="mb-5 flex items-start gap-4">
		<span class="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full border border-primary/30 bg-primary/10 font-mono text-xs font-semibold text-indigo-300">{number}</span>
		<h2 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">{title}</h2>
	</div>
	<div class="space-y-4 pl-0 text-[0.95rem] leading-7 text-slate-300 sm:pl-12 [&_a]:font-semibold [&_a]:text-indigo-300 [&_a]:underline [&_a]:decoration-indigo-300/40 [&_a]:underline-offset-4 [&_li]:pl-1 [&_strong]:font-semibold [&_strong]:text-foreground [&_ul]:ml-5 [&_ul]:list-disc [&_ul]:space-y-2">
		{@render children()}
	</div>
</section>
