<script lang="ts">
  import Typography from "../../atoms/Typography/Typography.svelte";

  type FormFooterProps = {
    text: string;
    linkLabel: string;
    linkHref: string;
    class?: string;
  };

  let {
    text,
    linkLabel,
    linkHref,
    class: className = "",
  }: FormFooterProps = $props();
</script>

<div class="mt-6 text-center {className}">
  <Typography variant="form-footer" class="text-xs">
    {text}
    <a
      href={linkHref}
      class="font-semibold text-foreground hover:underline ml-1"
    >
      {linkLabel}
    </a>
  </Typography>
</div>
