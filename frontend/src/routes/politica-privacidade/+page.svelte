<script lang="ts">
	import BrandIcon from '$lib/components/atoms/BrandIcon/BrandIcon.svelte';
	import BackLink from '$lib/components/molecules/BackLink/BackLink.svelte';
	import PolicySection from '$lib/components/molecules/PolicySection/PolicySection.svelte';

	const sections = [
		{ id: 'escopo', label: 'Escopo' },
		{ id: 'dados-coletados', label: 'Dados coletados' },
		{ id: 'finalidades', label: 'Como usamos' },
		{ id: 'base-legal', label: 'Base legal' },
		{ id: 'compartilhamento', label: 'Compartilhamento' },
		{ id: 'retencao', label: 'Retenção' },
		{ id: 'seguranca', label: 'Segurança' },
		{ id: 'direitos', label: 'Seus direitos' },
		{ id: 'contato', label: 'Contato' }
	];
</script>

<svelte:head>
	<title>Política de privacidade | UniLaunch</title>
	<meta name="description" content="Entenda como a UniLaunch coleta, utiliza, protege e elimina seus dados pessoais." />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
	<header class="sticky top-0 z-30 border-b border-border bg-background/90 backdrop-blur-xl">
		<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
			<a href="/captura-lead" class="flex items-center gap-3 text-foreground no-underline">
				<BrandIcon size="sm" />
				<span class="text-lg font-bold tracking-tight">UniLaunch</span>
			</a>
			<span class="rounded-full border border-border bg-card px-3 py-1.5 text-xs font-semibold text-muted">Documento público</span>
		</div>
	</header>

	<section class="relative overflow-hidden border-b border-border">
		<div aria-hidden="true" class="pointer-events-none absolute top-0 left-1/3 size-96 -translate-y-1/2 rounded-full bg-primary/15 blur-3xl"></div>
		<div class="relative mx-auto max-w-6xl px-4 py-14 sm:px-6 sm:py-20 lg:px-8 lg:py-24">
			<BackLink href="/captura-lead" label="Voltar ao formulário" class="mb-10 mt-0" />
			<div class="max-w-3xl">
				<p class="mb-4 text-xs font-bold tracking-[0.2em] text-indigo-300 uppercase">Privacidade na UniLaunch</p>
				<h1 class="text-[clamp(2.5rem,7vw,5.25rem)] font-bold leading-[0.98] tracking-[-0.055em] text-foreground">Seus dados,<br /><span class="text-indigo-300">seus direitos.</span></h1>
				<p class="mt-7 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg sm:leading-8">Esta política explica, de forma direta, quais dados tratamos quando você demonstra interesse na UniLaunch e quais escolhas permanecem sob seu controle.</p>
			</div>
			<div class="mt-10 flex flex-wrap gap-x-8 gap-y-3 border-t border-border pt-6 text-sm text-muted">
				<p><span class="text-muted-foreground">Versão</span> <strong class="ml-2 text-foreground">v1.0</strong></p>
				<p><span class="text-muted-foreground">Atualizada em</span> <strong class="ml-2 text-foreground">15 de setembro de 2026</strong></p>
			</div>
		</div>
	</section>

	<section aria-label="Resumo da política" class="mx-auto grid max-w-6xl gap-px border-x border-b border-border bg-border sm:grid-cols-3">
		<div class="bg-card p-6 sm:p-7">
			<div class="mb-5 flex size-10 items-center justify-center rounded-xl bg-primary/10 text-indigo-300">
				<svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20 21a8 8 0 0 0-16 0" /><circle cx="12" cy="7" r="4" /></svg>
			</div>
			<h2 class="font-bold text-foreground">O que coletamos</h2>
			<p class="mt-2 text-sm leading-6 text-muted">Dados de contato e informações profissionais ou acadêmicas enviadas por você.</p>
		</div>
		<div class="bg-card p-6 sm:p-7">
			<div class="mb-5 flex size-10 items-center justify-center rounded-xl bg-accent/10 text-indigo-300">
				<svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" /><path d="m9 12 2 2 4-4" /></svg>
			</div>
			<h2 class="font-bold text-foreground">Por que usamos</h2>
			<p class="mt-2 text-sm leading-6 text-muted">Para avaliar seu interesse, responder ao contato e conectar oportunidades relevantes.</p>
		</div>
		<div class="bg-card p-6 sm:p-7">
			<div class="mb-5 flex size-10 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">
				<svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></svg>
			</div>
			<h2 class="font-bold text-foreground">Por quanto tempo</h2>
			<p class="mt-2 text-sm leading-6 text-muted">O período operacional padrão é de 365 dias, salvo obrigação legal ou exclusão antecipada.</p>
		</div>
	</section>

	<div class="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-6 sm:py-16 lg:grid-cols-[15rem_minmax(0,1fr)] lg:px-8 lg:py-20">
		<aside class="hidden lg:block">
			<nav aria-label="Nesta política" class="sticky top-24">
				<p class="mb-4 text-xs font-bold tracking-[0.16em] text-muted-foreground uppercase">Nesta política</p>
				<ul class="border-l border-border">
					{#each sections as section, index}
						<li><a href={`#${section.id}`} class="flex gap-3 border-l border-transparent px-4 py-2 text-sm text-muted no-underline transition-colors hover:border-indigo-400 hover:text-foreground"><span class="font-mono text-xs text-muted-foreground">{String(index + 1).padStart(2, '0')}</span>{section.label}</a></li>
					{/each}
				</ul>
			</nav>
		</aside>

		<article class="min-w-0 max-w-3xl">
			<PolicySection id="escopo" number="01" title="Escopo desta política">
				<p>Esta política se aplica aos formulários públicos de interesse da UniLaunch, tanto para <strong>representantes de empresas</strong> quanto para <strong>estudantes</strong>. O envio desses formulários não cria automaticamente uma conta na plataforma.</p>
				<p>A UniLaunch atua como controladora dos dados pessoais informados nesses fluxos e determina como eles serão utilizados para atender às finalidades descritas abaixo.</p>
			</PolicySection>

			<PolicySection id="dados-coletados" number="02" title="Dados que coletamos">
				<p>Coletamos somente as informações necessárias para compreender seu perfil e responder ao interesse manifestado:</p>
				<ul>
					<li><strong>Dados de contato:</strong> nome completo e endereço de e-mail.</li>
					<li><strong>Perfil empresarial:</strong> empresa, cargo, porte, site e mensagem opcional.</li>
					<li><strong>Perfil acadêmico:</strong> instituição de ensino, curso, semestre, área de interesse, LinkedIn, GitHub e mensagem opcional.</li>
					<li><strong>Dados do envio:</strong> origem da campanha, data, horário, versão da política aceita e registro do consentimento.</li>
				</ul>
				<p>Não solicitamos dados financeiros, documentos de identidade ou dados pessoais sensíveis nesses formulários.</p>
			</PolicySection>

			<PolicySection id="finalidades" number="03" title="Como usamos seus dados">
				<p>Utilizamos os dados para analisar a solicitação, entrar em contato, apresentar produtos, projetos ou oportunidades compatíveis e acompanhar o relacionamento iniciado por você.</p>
				<p>Também produzimos métricas agregadas de acesso e conversão para melhorar os formulários. Essas métricas não exibem publicamente o conteúdo enviado nem identificam uma pessoa individualmente.</p>
			</PolicySection>

			<PolicySection id="base-legal" number="04" title="Base legal e consentimento">
				<p>O tratamento realizado a partir dos formulários tem como base o <strong>consentimento</strong>, nos termos da Lei nº 13.709/2018, a Lei Geral de Proteção de Dados Pessoais (LGPD).</p>
				<p>Você pode retirar esse consentimento a qualquer momento. A retirada não invalida tratamentos realizados anteriormente de forma legítima, mas interrompe novos usos baseados nessa autorização, ressalvadas obrigações legais.</p>
			</PolicySection>

			<PolicySection id="compartilhamento" number="05" title="Compartilhamento e operadores">
				<p>Não vendemos seus dados pessoais. O acesso é restrito à equipe autorizada da UniLaunch e a fornecedores de infraestrutura essenciais para hospedagem, banco de dados, segurança e envio de comunicações.</p>
				<p>Esses fornecedores recebem apenas os dados necessários à execução de seus serviços e devem tratá-los de acordo com obrigações de confidencialidade e proteção de dados.</p>
			</PolicySection>

			<PolicySection id="retencao" number="06" title="Retenção e exclusão">
				<p>O período operacional padrão de retenção dos leads é de <strong>365 dias</strong> a partir da coleta. Os dados podem ser eliminados antes quando deixam de ser necessários ou quando você apresenta uma solicitação válida.</p>
				<p>Determinados registros poderão ser conservados pelo período exigido para cumprimento de obrigação legal, regulatória ou exercício regular de direitos.</p>
			</PolicySection>

			<PolicySection id="seguranca" number="07" title="Como protegemos as informações">
				<p>Adotamos controles técnicos e organizacionais para reduzir riscos de acesso não autorizado, perda, alteração ou divulgação indevida. Isso inclui restrição administrativa, comunicação autenticada entre os serviços, limites contra abuso e monitoramento operacional.</p>
				<p>Nenhum ambiente é completamente imune a incidentes. Caso ocorra um evento relevante envolvendo seus dados, adotaremos as medidas de contenção e comunicação previstas na legislação.</p>
			</PolicySection>

			<PolicySection id="direitos" number="08" title="Seus direitos pela LGPD">
				<p>Você pode solicitar, quando aplicável:</p>
				<ul>
					<li>confirmação da existência de tratamento e acesso aos dados;</li>
					<li>correção de informações incompletas, inexatas ou desatualizadas;</li>
					<li>anonimização, bloqueio ou eliminação de dados desnecessários;</li>
					<li>informações sobre compartilhamento e portabilidade;</li>
					<li>revogação do consentimento e eliminação dos dados tratados com essa base.</li>
				</ul>
				<p>Podemos solicitar informações adicionais para confirmar sua identidade antes de atender ao pedido e proteger seus dados contra solicitações indevidas.</p>
			</PolicySection>

			<PolicySection id="contato" number="09" title="Fale com a UniLaunch">
				<p>Para exercer seus direitos, esclarecer dúvidas ou comunicar uma preocupação sobre privacidade, escreva para <a href="mailto:unilaunchorg@gmail.com">unilaunchorg@gmail.com</a>.</p>
				<div class="mt-6 rounded-xl border border-primary/25 bg-primary/10 p-5">
					<p class="text-sm leading-6 text-slate-200"><strong>Para agilizar o atendimento:</strong> informe o e-mail utilizado no formulário e descreva objetivamente sua solicitação. Não envie senhas ou documentos pessoais no primeiro contato.</p>
				</div>
			</PolicySection>
		</article>
	</div>

	<footer class="border-t border-border">
		<div class="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-8 text-sm text-muted sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
			<p>© 2026 UniLaunch. Transparência faz parte do produto.</p>
			<div class="flex gap-5"><a href="/captura-lead" class="text-muted no-underline hover:text-foreground">Empresas</a><a href="/captura-lead/aluno" class="text-muted no-underline hover:text-foreground">Estudantes</a></div>
		</div>
	</footer>
</main>
