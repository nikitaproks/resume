<script>
    import { createEventDispatcher } from 'svelte';

    export let label = 'Toggle Switch'
	export let fontSize = 16;
    export let checked = false;

    const dispatch = createEventDispatcher();

    const uniqueID = Math.floor(Math.random() * 100)

    function handleClick() {
        const target = event.target

        const state = target.getAttribute('aria-checked')
        checked = state === 'true' ? false : true
        dispatch('toggle');
    }
	
</script>

<div class="slider" style="font-size:{fontSize}px">
    <span id={`switch-${uniqueID}`}>{label}</span>
    <button
        class="bg-primary focus:bg-primary "
        role="switch"
        aria-checked={checked}
        aria-labelledby={`switch-${uniqueID}`}
        on:click={handleClick}>
    </button>
</div>


<style>
	:root {
		--accent-color: theme('colors.accent');
		--gray: #ccc;
	}

    /* Slider Design Option */

    .slider {
        display: flex;
        align-items: center;
    }

    .slider button {
        width: 3em;
        height: 1.6em;
        position: relative;
        margin: 0 0 0 0.5em;
        background: var(--gray);
        border: none;
    }

    button::before {
        content: '';
        position: absolute;
        width: 1.3em;
        height: 1.3em;
        background: #fff;
        top: 0.13em;
        right: 1.5em;
        transition: transform 0.3s;
    }

    button[aria-checked='true']{
        background-color: var(--accent-color)
    }

    button[aria-checked='true']::before{
        transform: translateX(1.3em);
        transition: transform 0.3s;
    }

    button:focus {
        box-shadow: 0 0px 0px 1px var(--accent-color);
    }

    button:focus {
        box-shadow: 0 0px 8px var(--accent-color);
    }
   

</style>