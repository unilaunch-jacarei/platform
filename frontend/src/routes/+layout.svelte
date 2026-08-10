<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import type { LayoutData } from './$types';

	let { children, data }: { children: any; data: LayoutData } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if data.userId}
	<header class="topbar">
		<a class="logo" href="/">UniLaunch</a>
		<form method="POST" action="/logout">
			<button type="submit">Sair</button>
		</form>
	</header>
{/if}

{@render children()}

<style>
	.topbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.85rem 1.5rem;
		background: #173d36;
		color: #fff;
	}

	.logo {
		color: #d8eb63;
		font-weight: 800;
		text-decoration: none;
	}

	button {
		border: 1px solid #ffffff66;
		border-radius: 8px;
		padding: 0.45rem 0.8rem;
		background: transparent;
		color: #fff;
		cursor: pointer;
		font: inherit;
		font-size: 0.85rem;
	}

	button:hover { background: #ffffff1a; }
</style>
