<script lang="ts">
  import Checkbox from "../../atoms/Checkbox/Checkbox.svelte";
  import Typography from "../../atoms/Typography/Typography.svelte";

  type FormCheckboxProps = {
    id: string;
    name?: string;
    label: string;
    checked?: boolean;
    disabled?: boolean;
    class?: string;
  };

  let {
    id,
    name,
    label,
    checked = $bindable(false),
    disabled = false,
    class: className = "",
  }: FormCheckboxProps = $props();
</script>

<div class="flex items-center gap-2 pt-1 {className}">
  <Checkbox {id} {name} bind:checked {disabled}>
    <Typography
      variant="caption"
      class="text-xs text-muted cursor-pointer select-none"
    >
      {label}
    </Typography>
  </Checkbox>
</div>
