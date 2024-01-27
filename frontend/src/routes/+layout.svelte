<script>
    import { page } from '$app/stores';
    import "../app.css";
    import { DarkMode, Navbar,NavBrand, NavLi, NavUl, NavHamburger } from 'flowbite-svelte';
    $: activeUrl = $page.url.pathname;
</script>

<Navbar class=" bg-primary px-2 sm:px-4 py-2.5 fixed w-full z-20 top-0 start-0" >
    <NavBrand href="/">
    </NavBrand>
    <NavHamburger  />
    <NavUl {activeUrl} >
      <NavLi href="/" 
        nonActiveClass="text-secondary hover:text-accent"
        activeClass="text-accent-dark"
      >Home</NavLi>
      <NavLi href="/resume" 
        nonActiveClass="text-secondary hover:text-accent"
        activeClass="text-accent-dark"
       >Resume</NavLi>
      <NavLi href="/contact" 
        nonActiveClass="text-secondary hover:text-accent"
        activeClass="text-accent-dark"
        >Contact</NavLi>
    </NavUl>
  </Navbar>
  
<main class="flex flex-1 items-center justify-center bg-primary pb-6">
<slot />
</main>

<footer class="fixed bottom-0 w-full z-50 px-10 h-16 flex items-center justify-between bg-primary text-secondary">
    <DarkMode />
    <div class="flex items-center justify-between">
        <a href="https://github.com/nikitaproks" target="_blank" class="flex items-center px-3">
            <i class="fa-brands fa-github" style="font-size: 30px;"></i>
        </a>
        <a href="https://www.linkedin.com/in/mykyta-prokaiev/" target="_blank" class="flex items-center  px-3">
            <i class="fa-brands fa-linkedin" style="font-size: 30px;"></i>
        </a>
    </div>
</footer>