<script lang="ts">
  import type { Snippet } from "svelte";
  import favicon from "$lib/assets/favicon.svg";
  import type { LayoutData } from "./$types";
  import "$lib/styles/globals.css";

  // Tipagem recomendada no Svelte 5 usando Snippet
  let { children, data }: { children: Snippet; data: LayoutData } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    rel="preconnect"
    href="https://fonts.gstatic.com"
    crossorigin="anonymous"
  />
  <link
    rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
  />
</svelte:head>

{#if data.userId}
  <header class="topbar">
    <a class="logo" href="/">UniLaunch</a>
    <form method="POST" action="/logout">
      <button type="submit" class="logout-btn">Sair</button>
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
    background: var(--topbar-bg, var(--surface));
    color: var(--foreground);
    border-bottom: 1px solid var(--border);
  }

  .logo {
    color: var(--primary);
    font-family: var(--font-display);
    font-weight: 800;
    text-decoration: none;
  }

  .logout-btn {
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.45rem 0.8rem;
    background: transparent;
    color: var(--foreground);
    cursor: pointer;
    font: inherit;
    font-size: 0.85rem;
    transition: background-color var(--transition);
  }

  .logout-btn:hover {
    background: var(--surface-soft);
  }
</style>
