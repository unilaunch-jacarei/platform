<!-- src/lib/components/organisms/BrandLogoSection/BrandLogoSection.svelte -->
<script lang="ts">
  import BrandHeader from "$lib/components/molecules/BrandHeader/BrandHeader.svelte";

  type BrandLogoSectionProps = {
    title?: string;
    subtitle?: string;
    class?: string;
  };

  let {
    title = "Unilaunch",
    subtitle = "Plataforma de Colaboração Acadêmica",
    class: className = "",
  }: BrandLogoSectionProps = $props();
</script>

<section class="flex flex-col items-center justify-center w-full {className}">
  <BrandHeader {title} {subtitle} />
</section>
