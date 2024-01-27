<script>
    import '../../app.css'
    import { Timeline, TimelineItem } from 'flowbite-svelte';
    import { CalendarWeekSolid } from 'flowbite-svelte-icons';

    export let items;
  </script>
  
<Timeline  order="vertical" class="border-l-1 border-secondary">
    {#each items as item}
        <TimelineItem class="font-extralight" title={item.title} date="{item.period} | {item.place}, {item.city}, {item.country}" classDiv="ring-none dark:ring-none" >
            <svelte:fragment slot="icon">
            <span class="flex absolute -start-3 justify-center items-center w-6 h-6 rounded-full ring-8  bg-secondary ring-secondary dark:ring-secondary">
                <CalendarWeekSolid class="w-4 h-4 text-accent" />
            </span>
            </svelte:fragment>
            {#if item.description}
            <p class="mb-4 text-base font-extralight text-secondary">{item.description}</p>
            {/if}
            {#if item.achievements}
                <ul class="list-disc list-inside ml-4">
                    {#each item.achievements as achievement}
                        <li class="mb-2 text-base font-normal text-secondary">{achievement}</li>
                    {/each}
                </ul>
            {/if}
        </TimelineItem>
    {/each}
</Timeline>