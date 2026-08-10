<script lang="ts">
  import { enhance } from '$app/forms';

  let { form } = $props();
  let submitting = $state(false);

  function handleSubmit() {
    submitting = true;
    return async ({ update }: { update: () => Promise<void> }) => {
      await update();
      submitting = false;
    };
  }
</script>

<svelte:head>
  <title>Criar conta | UniLaunch</title>
</svelte:head>

<main class="page">
  <section class="card">
    <div class="brand-mark">U</div>

    <p class="eyebrow">UNILAUNCH</p>
    <h1>Criar sua conta</h1>
    <p class="subtitle">Comece sua jornada na plataforma.</p>

    <form method="POST" use:enhance={handleSubmit} aria-busy={submitting}>
      <label for="nome">Nome</label>
      <input
        id="nome"
        name="nome"
        type="text"
        value={form?.nome ?? ""}
        autocomplete="name"
        required
      />

      <label for="email">E-mail</label>
      <input
        id="email"
        name="email"
        type="email"
        value={form?.email ?? ""}
        autocomplete="email"
        required
      />

      <label for="password">Senha</label>
      <input
        id="password"
        name="password"
        type="password"
        minlength="8"
        autocomplete="new-password"
        required
      />

      {#if form?.error}
        <p class="error" role="alert">{form.error}</p>
      {/if}

      <button type="submit" disabled={submitting}>
        {#if submitting}<span class="spinner" aria-hidden="true"></span>{/if}
        {submitting ? 'Criando conta…' : 'Criar conta'}
      </button>
    </form>

    <p class="footer">
      Já possui uma conta?
      <a href="/login">Entrar</a>
    </p>
  </section>
</main>

<style>
  .page {
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 2rem;
    background: #f7f8f5;
  }

  .card {
    width: min(100%, 430px);
    padding: 2.5rem;
    border-radius: 16px;
    background: white;
    box-shadow: 0 20px 60px #173d3614;
  }

  .brand-mark {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: #d8eb63;
    color: #173d36;
    font-weight: 800;
    font-size: 1.35rem;
  }

  .eyebrow {
    margin: 1.5rem 0 1rem;
    color: #56806f;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.18em;
  }

  h1 {
    margin: 0;
    color: #17211f;
    font-size: 2.5rem;
    letter-spacing: -0.05em;
  }

  .subtitle,
  .footer {
    color: #71807b;
  }

  form {
    display: grid;
    gap: 0.7rem;
    margin-top: 2rem;
  }

  label {
    margin-top: 0.5rem;
    color: #33433e;
    font-size: 0.86rem;
    font-weight: 700;
  }

  input {
    width: 100%;
    border: 1px solid #d9e0da;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    font: inherit;
  }

  button {
    margin-top: 1rem;
    border: 0;
    border-radius: 10px;
    padding: 1rem;
    background: #173d36;
    color: white;
    cursor: pointer;
    font: inherit;
    font-weight: 700;
  }

  button:disabled { cursor: wait; opacity: 0.7; }

  .spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    margin-right: 0.5rem;
    border: 2px solid #ffffff66;
    border-top-color: #fff;
    border-radius: 50%;
    vertical-align: -0.15rem;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .error {
    color: #a33d38;
    font-size: 0.85rem;
  }

  a {
    color: #477665;
    font-weight: 700;
    text-decoration: none;
  }
</style>
