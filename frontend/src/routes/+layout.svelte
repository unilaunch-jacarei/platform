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
    <strong class="topbar-title">Kanban</strong>
    <div class="profile-area">
      <span class="notifications" aria-label="4 notificações">♧<b>4</b></span>
      <form method="POST" action="/logout">
        <button type="submit" class="avatar" aria-label="Sair da conta" title="Sair">L</button>
      </form>
    </div>
  </header>
{/if}

{@render children()}

<style>
  .topbar {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 4.4rem;
    box-sizing: border-box;
    padding: 0.85rem 1.85rem;
    background: #090b1d;
    color: var(--foreground);
    border-bottom: 1px solid var(--border);
  }

  .logo {
    color: #dfe4f3;
    font-family: var(--app-font-display);
    font-weight: 800;
    text-decoration: none;
  }

  .topbar-title {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    color: #f2f3fb;
    font-family: var(--app-font-display);
    font-size: 0.95rem;
  }

  .profile-area { display: flex; align-items: center; gap: 0.65rem; }
  .notifications { position: relative; display: grid; width: 2.45rem; height: 2.45rem; place-items: center; border: 1px solid #2b315a; border-radius: 50%; color: #70809e; font-size: 1rem; }
  .notifications b { position: absolute; top: -0.3rem; right: -0.18rem; display: grid; width: 1.2rem; height: 1.2rem; place-items: center; border-radius: 50%; background: #744cf0; color: #fff; font-size: 0.63rem; }
  .avatar {
    display: grid;
    width: 2.5rem;
    height: 2.5rem;
    place-items: center;
    border: 0;
    border-radius: 50%;
    background: #7351ed;
    color: #fff;
    cursor: pointer;
    font: 800 .9rem var(--app-font-display);
  }
</style>
