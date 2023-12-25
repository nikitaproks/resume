<script>
    export let inverted = false;
    export let skill = '';
    export let level = ''; // Level as descriptive text (e.g., 'Advanced')
  </script>
  {#if inverted}
    <div class="flex items-center justify-between py-1">
      <span class="badge badge-outline badge-secondary p-4 rounded-none text-sm">{level}</span>
      <span class="font-medium text-accent">{skill}</span>
    </div>

  {:else}
    <div class="flex items-center justify-between py-1">
      <span class="font-medium text-accent">{skill}</span>
      <span class="badge badge-outline badge-secondary p-4 rounded-none text-sm">{level}</span>
    </div>

  {/if}