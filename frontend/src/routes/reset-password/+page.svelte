<svelte:head>
	<title>Nova senha | UniLaunch</title>
	<meta name="description" content="Crie uma nova senha para sua conta UniLaunch." />
</svelte:head>

<script lang="ts">
	import { enhance } from '$app/forms';

	let submitting = $state(false);
	let { data, form } = $props();

	function handleSubmit() {
		submitting = true;
		return async ({ update }: { update: () => Promise<void> }) => {
			await update();
			submitting = false;
		};
	}
</script>

<main class="page-shell">
	<section class="card" aria-labelledby="title">
		<a class="back" href="/login">← Voltar para o login</a>
		<div class="mark">U</div>
		<p class="eyebrow">RECUPERAÇÃO DE CONTA</p>
		<h1 id="title">Crie uma nova senha</h1>
		<p class="subtitle">Escolha uma senha forte para proteger seu workspace.</p>

		<form method="POST" use:enhance={handleSubmit} aria-busy={submitting}>
			<input type="hidden" name="token" value={data.token} />
			<label for="new_password">Nova senha</label>
			<input id="new_password" name="new_password" type="password" autocomplete="new-password" minlength="8" required />
			<label for="confirmation">Confirme sua senha</label>
			<input id="confirmation" name="confirmation" type="password" autocomplete="new-password" minlength="8" required />
			<p class="hint">Use pelo menos 8 caracteres. Evite senhas reutilizadas.</p>
			<button class="submit" type="submit" disabled={submitting || !data.token}>
				{#if submitting}<span class="spinner" aria-hidden="true"></span>{/if}
				{submitting ? 'Salvando…' : 'Salvar nova senha'}
				<span aria-hidden="true">→</span>
			</button>
			{#if !data.token}<p class="error" role="alert">O link de recuperação não contém um token válido.</p>{/if}
			{#if form?.error}<p class="error" role="alert">{form.error}</p>{/if}
		</form>
	</section>
</main>

<style>
	:global(*) { box-sizing: border-box; }
	:global(body) { margin: 0; font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #17211f; }
	.page-shell { min-height: 100vh; display: grid; place-items: center; padding: 2rem 1.25rem; background: #173d36; }
	.card { width: min(100%, 460px); padding: clamp(2rem, 6vw, 3.5rem); border-radius: 18px; background: #f7f8f5; box-shadow: 0 24px 70px #102c2655; }
	.back { display: inline-block; margin-bottom: 2.5rem; color: #477665; font-size: .82rem; font-weight: 700; text-decoration: none; }
	.back:hover { text-decoration: underline; }
	.mark { display: grid; place-items: center; width: 42px; height: 42px; border-radius: 12px; background: #d8eb63; color: #173d36; font-size: 1.35rem; font-weight: 800; }
	.eyebrow { margin: 1.6rem 0 1rem; color: #56806f; font-size: .72rem; font-weight: 800; letter-spacing: .18em; }
	h1 { margin: 0; font-size: clamp(2rem, 6vw, 3rem); line-height: 1.05; letter-spacing: -.05em; }
	.subtitle { margin: 1rem 0 2rem; color: #71807b; line-height: 1.55; }
	form { display: grid; gap: .7rem; }
	label { margin-top: .35rem; color: #33433e; font-size: .86rem; font-weight: 700; }
	input:not([type='hidden']) { width: 100%; border: 1px solid #d9e0da; border-radius: 10px; padding: .9rem 1rem; outline: none; background: #fff; color: #17211f; font: inherit; }
	input:not([type='hidden']):focus { border-color: #56806f; box-shadow: 0 0 0 3px #56806f22; }
	.hint { margin: .1rem 0 .8rem; color: #89948e; font-size: .78rem; }
	.submit { display: flex; align-items: center; justify-content: space-between; border: 0; border-radius: 10px; padding: 1rem 1.15rem; background: #173d36; color: white; cursor: pointer; font: inherit; font-weight: 750; }
	.submit:hover:not(:disabled) { background: #285b4d; }
	.submit:disabled { cursor: not-allowed; opacity: .65; }
	.error { color: #a33d38; font-size: .82rem; }
	.spinner { width: 1rem; height: 1rem; border: 2px solid #ffffff66; border-top-color: #fff; border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
</style>
