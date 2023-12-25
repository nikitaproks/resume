<script>
  export let items;
</script>

<style>
  .timeline {
    display: flex;
    overflow-x: auto;
    gap: 1rem;
    scrollbar-width: none; /* For Firefox */
  }

  .timeline::-webkit-scrollbar {
    display: none; /* For WebKit browsers */
  }

  .timeline-item {
    min-width: 200px;
  }

  .icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }
</style>

<div class="timeline">
  {#each items as item}
    <div class="timeline-item bg-primary text-secondary border-2 border-secondary text-center p-4">
      <div class="icon">
        <i class={`${item.icon}`}></i>
      </div>
      <h3 class="mb-2 text-accent">{item.skill}</h3>
      <p class="text-secondary">{item.description}</p>
    </div>
  {/each}
</div>
