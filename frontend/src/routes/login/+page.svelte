<script lang="ts">
  import { enhance } from "$app/forms";
  import Typography from "$lib/components/atoms/Typography/Typography.svelte";
  import Input from "$lib/components/atoms/Input/Input.svelte";
  import Button from "$lib/components/atoms/Button/Button.svelte";
  import Checkbox from "$lib/components/atoms/Checkbox/Checkbox.svelte";
  import FormField from "$lib/components/molecules/FormField/FormField.svelte";
  import Card from "$lib/components/atoms/Card/Card.svelte";

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

<svelte:head>
  <title>Entrar | UniLaunch</title>
  <meta
    name="description"
    content="Entre na sua conta UniLaunch para continuar."
  />
</svelte:head>

<Card>
  <Typography variant="h1">Hello World — H1</Typography>

  <Typography variant="h2">Hello World — H2</Typography>

  <Typography variant="body">Hello World — Body</Typography>

  <Typography variant="caption">Hello World — Caption</Typography>

  <Typography variant="kicker">Hello World — Kicker</Typography>

  <Typography variant="label">Hello World — Label</Typography>

  <Typography variant="link">Hello World — Link</Typography>

  <Typography variant="form-footer">Hello World — Form Footer</Typography>

  <Typography variant="subtitle">Hello World — Subtitle</Typography>

  <Input type="email" placeholder="seu@email.com" />

  <Input type="password" placeholder="sua senha" />

  <Button type="submit" size="lg" class="w-full">Entrar →</Button>

  <Checkbox />

  <FormField
    id="email"
    label="E-mail profissional"
    placeholder="seu@email.com"
    description="Enviaremos um link de confirmação."
    required
  />

  <FormField
    id="password"
    label="Senha"
    type="password"
    placeholder="password"
    description="Não compartilhe sua senha com ninguém."
    required
  />
</Card>
