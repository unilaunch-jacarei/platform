<script lang="ts">
  type FormAlertProps = {
    variant?: "error" | "success";
    message?: string;
    class?: string;
  };

  let {
    variant = "error",
    message,
    class: className = "",
  }: FormAlertProps = $props();

  const styles = {
    error: "bg-destructive/10 border-destructive/20 text-destructive",
    success: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400",
  };
</script>

{#if message}
  <div
    class="p-3 text-xs rounded-lg border font-medium {styles[
      variant
    ]} {className}"
    role={variant === "error" ? "alert" : "status"}
  >
    {message}
  </div>
{/if}
