<script>
    import { onMount } from 'svelte';
    import "../app.css";
    import ToggleSwitch from "../lib/components/ToggleSwitch.svelte";
    let theme;
    let path;
    let activeLink = null;

    function setActive(link) {
        activeLink = link;
    }

    onMount(() => {
        path = window.location.pathname;
        activeLink = path === '/' ? 'home' : path.slice(1);
        theme = localStorage.getItem('theme') || 'light';
        window.document.body.setAttribute('data-theme', theme);
    });

    function handleToggle() {
        const currentTheme = localStorage.getItem('theme') || 'light';
        console.log(currentTheme);
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        localStorage.setItem('theme', newTheme);
        window.document.body.setAttribute('data-theme', newTheme);
    }

</script>

<header class="fixed top-0 w-full z-50">
    <nav class="bg-primary p-4 w-full">
        <div class="mx-auto flex justify-end w-full">
            <ul class="flex items-center">
                <li class="mx-5 {activeLink === 'home' ? 'nav-link-selected' : 'nav-link'}">
                    <a href="/" on:click={() => setActive('home')}>Home</a>
                </li>
                <li class="mx-5 {activeLink === 'resume' ? 'nav-link-selected' : 'nav-link'}">
                    <a href="/resume" on:click={() => setActive('resume')}>Resume</a>
                </li>
                <a href="/contact" on:click={() => setActive('contact')}>
                    <li class="{activeLink === 'contact' ? 'custom-btn-selected' : 'custom-btn'}">
                        Contact
                    </li>
                </a>
            </ul>
        </div>
    </nav>
</header>
  
<main class="flex flex-1 items-center justify-center bg-primary pb-6">
<slot />
</main>

<footer class="fixed bottom-0 w-full z-50 px-10 h-16 flex items-center justify-between bg-primary text-secondary">
    <ToggleSwitch on:toggle={handleToggle}  checked={theme === "dark" ? true: false} label="Dark mode" fontSize={15}/>
    <div class="flex items-center justify-between">
        <a href="https://github.com/nikitaproks" target="_blank" class="flex items-center px-3">
            <i class="fa-brands fa-github" style="font-size: 30px;"></i>
        </a>
        <a href="https://www.linkedin.com/in/mykyta-prokaiev/" target="_blank" class="flex items-center  px-3">
            <i class="fa-brands fa-linkedin" style="font-size: 30px;"></i>
        </a>
    </div>
</footer>

<style>
    .nav-link{
        @apply text-secondary;
    }
    .nav-link-selected{
        @apply text-accent;
    }
    .nav-link:hover{
        @apply text-accent;
    }
</style>