<script lang="ts">
  type BrandIconProps = {
    size?: "sm" | "md" | "lg";
    class?: string;
  };

  let { size = "md", class: className = "" }: BrandIconProps = $props();

  const sizeClasses = {
    sm: "size-10 rounded-xl",
    md: "size-14 rounded-2xl",
    lg: "size-16 rounded-2xl",
  };

  const iconSizes = {
    sm: "size-5",
    md: "size-6",
    lg: "size-8",
  };
</script>

<div
  class="flex items-center justify-center bg-gradient-to-br from-[#7C3AED] to-[#6366F1] text-white shadow-[0_0_25px_rgba(124,58,237,0.45)] transition-transform duration-300 hover:scale-105 {sizeClasses[
    size
  ]} {className}"
>
  <svg
    class="{iconSizes[size]}"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
</div>