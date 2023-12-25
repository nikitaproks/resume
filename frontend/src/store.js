import { writable } from 'svelte/store';

function getInitialTheme() {
    if (typeof window !== 'undefined') {
      // We're in the browser, safe to use localStorage
      return localStorage.getItem('theme') || 'light';
    }
    return 'light'; // Default theme if not in browser
  }
  
  export const theme = writable(getInitialTheme());