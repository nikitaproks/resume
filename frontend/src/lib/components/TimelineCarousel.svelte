<script>
    export let items;
    export let header;
    let currentIndex = 0;
  
    function scroll(direction) {
      if (direction === 'next') {
        currentIndex = (currentIndex + 1) % items.length;
      } else {
        currentIndex = (currentIndex - 1 + items.length) % items.length;
      }
    }
    $: counterText = `${currentIndex + 1}/${items.length}`;
  </script>
  

<div class="flex justify-between items-center mb-4">

    <h2 class="text-secondary">{header}</h2>
    <div>
      <button class="btn btn-circle shadow-none text-accent" on:click={() => scroll('prev')}>«</button>
      <span class="text-sm text-accent">{counterText}</span>
      <button class="btn btn-circle shadow-none text-accent" on:click={() => scroll('next')}>»</button>
    </div>
</div>

{#if items.length > 0}
    <div class="p-4 border border-secondary min-h-80">
      <div class="flex justify-between items-center">
        <h3 class=" text-secondary">
          {items[currentIndex].title}
        </h3>
        <p class="text-sm text-accent">{items[currentIndex].period}</p>
      </div>
      <h3 class="text-gray-500 my-2">{items[currentIndex].place}, {items[currentIndex].city}, {items[currentIndex].country}</h3>
      <hr class="border-secondary mb-4" />
      {#if items[currentIndex].description !== undefined}
      <p class="text-secondary text-sm">{items[currentIndex].description}</p>
      {/if}
      {#if items[currentIndex].achievements.length > 0}
        <ul class="mt-4">
          {#each items[currentIndex].achievements as achievement }
            <p class="text-secondary text-sm">• {achievement}</p>
          {/each}
        </ul>
      {/if}
    </div>
{/if}

  