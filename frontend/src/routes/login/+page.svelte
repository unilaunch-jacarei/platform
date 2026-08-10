<svelte:head>
	<title>Entrar | UniLaunch</title>
	<meta
		name="description"
		content="Entre na sua conta UniLaunch para continuar."
	/>
</svelte:head>

	<script lang="ts">
	import { enhance } from '$app/forms';

	let showPassword = $state(false);
	let submitting = $state(false);
	let { form } = $props();

	function handleSubmit() {
		submitting = true;
		return async ({ update }: { update: () => Promise<void> }) => {
			await update();
			submitting = false;
		};
	}
</script>

<div class="login-shell">
	<section class="brand-panel" aria-label="Sobre a UniLaunch">
		<div class="brand-mark">U</div>
		<p class="eyebrow">UNILAUNCH</p>
		<h1>Construa o próximo passo da sua jornada.</h1>
		<p class="brand-copy">
			Um espaço para transformar ideias em projetos, acompanhar seu progresso e crescer em
			comunidade.
		</p>
		<div class="brand-line"></div>
		<p class="quote">“Grandes projetos começam com um primeiro passo.”</p>
	</section>

	<main class="form-panel">
		<div class="form-wrap">
			<div class="mobile-mark">U</div>
			<p class="eyebrow form-eyebrow">BEM-VINDO DE VOLTA</p>
			<h2>Entrar na sua conta</h2>
			<p class="subtitle">Acesse seu workspace e continue de onde parou.</p>

			<form method="POST" use:enhance={handleSubmit} aria-busy={submitting}>
				<label for="email">E-mail</label>
				<input
					id="email"
					name="email"
					type="email"
					autocomplete="email"
					placeholder="voce@exemplo.com"
					required
				/>

				<div class="password-heading">
					<label for="password">Senha</label>
					<a href="/recuperar-senha">Esqueci minha senha</a>
				</div>
				<div class="password-input">
					<input
						id="password"
						name="password"
						type={showPassword ? 'text' : 'password'}
						autocomplete="current-password"
						placeholder="Digite sua senha"
						required
					/>
					<button
						type="button"
						class="password-toggle"
						aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
						onclick={() => (showPassword = !showPassword)}
					>
						{showPassword ? 'Ocultar' : 'Mostrar'}
					</button>
				</div>

				<label class="remember">
					<input type="checkbox" name="remember" />
					<span>Manter-me conectado</span>
				</label>

				<button class="submit" type="submit" disabled={submitting}>
					{#if submitting}<span class="spinner" aria-hidden="true"></span>{/if}
					{submitting ? 'Aguarde…' : 'Entrar'}
					<span aria-hidden="true">→</span>
				</button>
				{#if form?.error}<p class="form-error" role="alert">{form.error}</p>{/if}
			</form>

			<p class="signup">Ainda não tem uma conta? <a href="/cadastro">Criar conta</a></p>
		</div>
	</main>
</div>

<style>
	:global(*) { box-sizing: border-box; }
	:global(body) { margin: 0; font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #17211f; }
	.login-shell { min-height: 100vh; display: grid; grid-template-columns: minmax(360px, 0.9fr) minmax(480px, 1.1fr); background: #f7f8f5; }
	.brand-panel { display: flex; flex-direction: column; justify-content: center; padding: clamp(3rem, 8vw, 8rem); background: #173d36; color: #f4f5ed; }
	.brand-mark, .mobile-mark { display: grid; place-items: center; width: 42px; height: 42px; border-radius: 12px; background: #d8eb63; color: #173d36; font-weight: 800; font-size: 1.35rem; }
	.eyebrow { margin: 1.6rem 0 1.25rem; color: #d8eb63; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.18em; }
	.brand-panel h1 { max-width: 520px; margin: 0; font-size: clamp(2.5rem, 4vw, 4.6rem); line-height: 1.02; letter-spacing: -0.055em; }
	.brand-copy { max-width: 420px; margin: 2rem 0 0; color: #bdd1ca; font-size: 1.05rem; line-height: 1.65; }
	.brand-line { width: 72px; height: 2px; margin: 4rem 0 1.25rem; background: #d8eb63; }
	.quote { margin: 0; color: #dce8e3; font-size: 0.9rem; }
	.form-panel { display: grid; place-items: center; padding: 3rem 2rem; background: #f7f8f5; }
	.form-wrap { width: min(100%, 430px); }
	.mobile-mark { display: none; }
	.form-eyebrow { color: #56806f; margin-top: 0; margin-bottom: 1rem; }
	h2 { margin: 0; color: #17211f; font-size: clamp(2rem, 4vw, 3rem); line-height: 1.05; letter-spacing: -0.05em; }
	.subtitle { margin: 1rem 0 2.5rem; color: #71807b; line-height: 1.5; }
	form { display: grid; gap: 0.7rem; }
	label { color: #33433e; font-size: 0.86rem; font-weight: 700; }
	input:not([type='checkbox']) { width: 100%; border: 1px solid #d9e0da; border-radius: 10px; padding: 0.9rem 1rem; outline: none; background: #fff; color: #17211f; font: inherit; transition: border-color 0.2s, box-shadow 0.2s; }
	input:not([type='checkbox']):focus { border-color: #56806f; box-shadow: 0 0 0 3px #56806f22; }
	.password-heading { display: flex; align-items: center; justify-content: space-between; margin-top: 0.9rem; }
	a { color: #477665; font-size: 0.82rem; font-weight: 700; text-decoration: none; }
	a:hover { text-decoration: underline; }
	.password-input { position: relative; }
	.password-input input { padding-right: 5.2rem; }
	.password-toggle { position: absolute; top: 50%; right: 0.75rem; transform: translateY(-50%); border: 0; background: transparent; color: #477665; cursor: pointer; font-size: 0.75rem; font-weight: 700; }
	.remember { display: flex; align-items: center; gap: 0.55rem; margin: 0.65rem 0 1rem; color: #71807b; font-size: 0.82rem; font-weight: 500; cursor: pointer; }
	.remember input { accent-color: #477665; }
	.submit { display: flex; align-items: center; justify-content: space-between; border: 0; border-radius: 10px; padding: 1rem 1.15rem; background: #173d36; color: white; cursor: pointer; font: inherit; font-weight: 750; transition: background 0.2s, transform 0.2s; }
	.submit:hover:not(:disabled) { background: #285b4d; transform: translateY(-1px); }
	.submit:disabled { cursor: wait; opacity: 0.7; }
	.signup { margin: 2rem 0 0; color: #71807b; text-align: center; font-size: 0.85rem; }
	.signup a { color: #173d36; }
	.form-error { margin: 0.45rem 0 0; color: #a33d38; font-size: 0.82rem; }
	.spinner { width: 1rem; height: 1rem; border: 2px solid #ffffff66; border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	@media (max-width: 800px) { .login-shell { display: block; } .brand-panel { display: none; } .form-panel { min-height: 100vh; padding: 2rem 1.25rem; } .mobile-mark { display: grid; margin-bottom: 2.5rem; } }
</style>
