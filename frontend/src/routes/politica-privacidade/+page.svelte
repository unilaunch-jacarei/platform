<script lang="ts">
	import CenteredContent from '$lib/components/layouts/CenteredContent/CenteredContent.svelte';
	import BrandLogoSection from '$lib/components/organisms/BrandLogoSection/BrandLogoSection.svelte';
import Card from '$lib/components/layouts/Card/Card.svelte';
import Typography from '$lib/components/atoms/Typography/Typography.svelte';
</script>

<svelte:head>
	<title>Política de privacidade | UniLaunch</title>
</svelte:head>

<CenteredContent class="gap-6 py-10 sm:py-16">
	<BrandLogoSection subtitle="Política de privacidade" />
	<Card class="max-w-2xl">
		<Typography variant="h1" class="mb-5">Política de privacidade</Typography>
		<div class="flex flex-col gap-4">
			<Typography>Versão v1.0</Typography>
			<Typography>
				Ao enviar o formulário, coletamos seu nome, e-mail e informações profissionais para que a
				UniLaunch possa entrar em contato sobre seus produtos e serviços.
			</Typography>
			<Typography>
				Os dados são usados exclusivamente para contato comercial, protegidos contra acesso não
				autorizado e mantidos pelo período necessário para essa finalidade ou conforme obrigações
				legais aplicáveis.
			</Typography>
			<Typography>
				Para solicitar acesso, correção ou exclusão dos seus dados, entre em contato com a equipe
				UniLaunch.
			</Typography>
		</div>
	</Card>
</CenteredContent>
