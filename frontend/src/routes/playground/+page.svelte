<script lang="ts">
  // Layouts
  import Card from "$lib/components/layouts/Card/Card.svelte";
  import CenteredContent from "$lib/components/layouts/CenteredContent/CenteredContent.svelte";

  // Átomos
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";
  import Button from "$lib/components/atoms/Button/Button.svelte";
  import Input from "$lib/components/atoms/Input/Input.svelte";
  import Checkbox from "$lib/components/atoms/Checkbox/Checkbox.svelte";

  // Moléculas
  import FormField from "$lib/components/molecules/FormField/FormField.svelte";
  import FormHeader from "$lib/components/molecules/FormHeader/FormHeader.svelte";
  import FormFooter from "$lib/components/molecules/FormFooter/FormFooter.svelte";
  import FormCheckbox from "$lib/components/molecules/FormCheckbox/FormCheckbox.svelte";

  // Organismos
  import LoginForm from "$lib/components/organisms/LoginForm.svelte";

  let checkboxState = $state(true);
  let formCheckboxState = $state(false);
  let inputValue = $state("Valor preenchido");
</script>

<svelte:head>
  <title>UI Playground | UniLaunch</title>
</svelte:head>

<div
  class="min-h-screen bg-background text-foreground p-8 space-y-12 max-w-5xl mx-auto"
>
  <!-- Cabeçalho da Rota Secreta -->
  <header class="border-b border-border pb-6">
    <Typography variant="h1">Design System Playground</Typography>
    <Typography variant="caption">
      Ambiente isolado para visualização de todos os tokens, componentes,
      estados e variações do UniLaunch.
    </Typography>
  </header>

  <!-- SEÇÃO 1: TYPOGRAPHY VARIANTS -->
  <section class="space-y-4">
    <div class="border-b border-border/50 pb-2">
      <Typography variant="h2">1. Typography</Typography>
    </div>

    <div class="grid gap-3 bg-card/40 p-6 rounded-xl border border-border">
      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >h1</span
        >
        <Typography variant="h1">Heading 1 — Unilaunch</Typography>
      </div>

      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >h2</span
        >
        <Typography variant="h2">Heading 2 — Seção Principal</Typography>
      </div>

      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >subtitle</span
        >
        <Typography variant="subtitle">Subtitle — Bem-vindo de volta</Typography
        >
      </div>

      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >body</span
        >
        <Typography variant="body"
          >Body — Texto padrão de leitura para parágrafos longos ou descrições
          principais no sistema.</Typography
        >
      </div>

      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >kicker</span
        >
        <Typography variant="kicker">Kicker — Categoria / Overline</Typography>
      </div>

      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >label</span
        >
        <Typography variant="label">Label — Nome de Campo</Typography>
      </div>

      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >caption</span
        >
        <Typography variant="caption"
          >Caption — Texto secundário ou de apoio para detalhes pequenos.</Typography
        >
      </div>

      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >link</span
        >
        <div>
          <Typography variant="link" href="https://youtu.be/dQw4w9WgXcQ?list=RDdQw4w9WgXcQ"
            >Link — Clique aqui para saber mais</Typography
          >
        </div>
      </div>

      <div>
        <span class="text-xs text-muted-foreground block mb-1 font-mono"
          >form-footer</span
        >
        <Typography variant="form-footer"
          >Form Footer — Já tem uma conta? <a
            href="https://youtu.be/dQw4w9WgXcQ?list=RDdQw4w9WgXcQ"
            class="underline font-bold">Entrar</a
          ></Typography
        >
      </div>
    </div>
  </section>

  <!-- SEÇÃO 2: BUTTONS -->
  <section class="space-y-4">
    <div class="border-b border-border/50 pb-2">
      <Typography variant="h2">2. Buttons</Typography>
    </div>

    <div
      class="flex flex-wrap gap-4 items-center bg-card/40 p-6 rounded-xl border border-border"
    >
      <div class="space-y-1">
        <span class="text-xs text-muted-foreground block font-mono"
          >default / lg</span
        >
        <Button size="lg">Entrar →</Button>
      </div>

      <div class="space-y-1">
        <span class="text-xs text-muted-foreground block font-mono"
          >disabled</span
        >
        <Button size="lg" disabled>Entrando...</Button>
      </div>

      <div class="space-y-1">
        <span class="text-xs text-muted-foreground block font-mono"
          >full width</span
        >
        <div class="w-64">
          <Button class="w-full">Botão Largura Total</Button>
        </div>
      </div>
    </div>
  </section>

  <!-- SEÇÃO 3: INPUTS & CHECKBOXES (ÁTOMOS) -->
  <section class="space-y-4">
    <div class="border-b border-border/50 pb-2">
      <Typography variant="h2">3. Átomos (Input & Checkbox)</Typography>
    </div>

    <div
      class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-card/40 p-6 rounded-xl border border-border"
    >
      <div class="space-y-2">
        <Typography variant="label">Input Text Padrão</Typography>
        <Input type="text" placeholder="Digite algo..." />
      </div>

      <div class="space-y-2">
        <Typography variant="label">Input com Bind Value</Typography>
        <Input type="text" bind:value={inputValue} />
      </div>

      <div class="space-y-2">
        <Typography variant="label">Input Password</Typography>
        <Input type="password" placeholder="••••••••" />
      </div>

      <div class="space-y-2">
        <Typography variant="label"
          >Input Estado de Erro (aria-invalid)</Typography
        >
        <Input type="email" placeholder="email@invalido" aria-invalid={true} />
      </div>

      <div class="space-y-2 col-span-full">
        <Typography variant="label">Checkbox Standalone</Typography>
        <div class="flex items-center gap-4">
          <Checkbox id="check-atom" bind:checked={checkboxState} />
          <Typography variant="caption"
            >Estado atual: {checkboxState
              ? "Marcado"
              : "Desmarcado"}</Typography
          >
        </div>
      </div>
    </div>
  </section>

  <!-- SEÇÃO 4: MOLÉCULAS -->
  <section class="space-y-4">
    <div class="border-b border-border/50 pb-2">
      <Typography variant="h2">4. Moléculas</Typography>
    </div>

    <div
      class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-card/40 p-6 rounded-xl border border-border"
    >
      <!-- FormHeader -->
      <div class="col-span-full border-b border-border/30 pb-4">
        <span class="text-xs text-muted-foreground block mb-2 font-mono"
          >FormHeader.svelte</span
        >
        <div class="border border-dashed border-border p-4 rounded-lg">
          <FormHeader
            title="Título da Molécula Header"
            description="Descrição complementar para orientar o usuário no formulário."
          />
        </div>
      </div>

      <!-- FormField - Padrão -->
      <div class="space-y-1">
        <span class="text-xs text-muted-foreground block font-mono"
          >FormField (Text + Required + Description)</span
        >
        <FormField
          id="demo-email"
          label="E-mail Acadêmico"
          type="email"
          placeholder="usuario@universidade.edu.br"
          description="Use o e-mail fornecido pela sua instituição."
          required
        />
      </div>

      <!-- FormField - Password com Toggle -->
      <div class="space-y-1">
        <span class="text-xs text-muted-foreground block font-mono"
          >FormField (Password + Forgot Link)</span
        >
        <FormField
          id="demo-pass"
          label="Sua Senha"
          type="password"
          placeholder="••••••••"
          forgotPasswordHref="https://youtu.be/dQw4w9WgXcQ?list=RDdQw4w9WgXcQ"
          required
        />
      </div>

      <!-- FormField - Estado de Erro -->
      <div class="space-y-1 col-span-full">
        <span class="text-xs text-muted-foreground block font-mono"
          >FormField (Com mensagem de erro tratada)</span
        >
        <FormField
          id="demo-error"
          label="E-mail de Acesso"
          type="email"
          value="email-invalido-sem-arroba"
          error="Formato de e-mail inválido. Certifique-se de incluir o '@'."
          required
        />
      </div>

      <!-- FormCheckbox -->
      <div class="space-y-1">
        <span class="text-xs text-muted-foreground block font-mono"
          >FormCheckbox</span
        >
        <FormCheckbox
          id="demo-form-check"
          label="Manter minha sessão ativa neste navegador"
          bind:checked={formCheckboxState}
        />
      </div>

      <!-- FormFooter -->
      <div class="space-y-1">
        <span class="text-xs text-muted-foreground block font-mono"
          >FormFooter</span
        >
        <FormFooter
          text="Ainda não possui cadastro?"
          linkLabel="Solicitar acesso"
          linkHref="https://youtu.be/dQw4w9WgXcQ?list=RDdQw4w9WgXcQ"
        />
      </div>
    </div>
  </section>

  <!-- SEÇÃO 5: LAYOUTS & ORGANISMS -->
  <section class="space-y-4 pb-12">
    <div class="border-b border-border/50 pb-2">
      <Typography variant="h2">5. Layouts & Organismos</Typography>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
      <!-- Layout: Card -->
      <div class="space-y-2">
        <span class="text-xs text-muted-foreground block font-mono"
          >Card Layout Container</span
        >
        <Card>
          <Typography variant="subtitle">Dentro de um Card</Typography>
          <Typography variant="caption" class="block mb-4">
            Este quadrado representa o container base reutilizável de layout.
          </Typography>
          <div
            class="h-20 w-full rounded bg-accent/20 border border-accent/40 flex items-center justify-center text-accent font-semibold text-xs"
          >
            Slot Content / Mock Element
          </div>
        </Card>
      </div>

      <!-- Layout: CenteredContent Preview -->
      <div class="space-y-2">
        <span class="text-xs text-muted-foreground block font-mono"
          >CenteredContent Wrapper Preview</span
        >
        <div
          class="min-h-[600px] h-auto w-full rounded-xl border border-dashed border-border flex flex-col items-center justify-center p-6 bg-card/20 overflow-visible"
        >
          <CenteredContent showBrandHeader={false} class="min-h-full w-full">
            <div
              class="text-center p-6 rounded bg-accent/10 border border-accent/30 w-full max-w-sm"
            >
              <Typography variant="label">Conteúdo Centralizado</Typography>
            </div>
          </CenteredContent>
        </div>
      </div>

      <!-- Organismo: LoginForm Completo -->
      <div class="col-span-full space-y-2">
        <span class="text-xs text-muted-foreground block font-mono"
          >LoginForm Organism</span
        >
        <div
          class="flex justify-center p-8 bg-background rounded-2xl border border-border"
        >
          <LoginForm form={null} />
        </div>
      </div>
    </div>
  </section>
</div>
