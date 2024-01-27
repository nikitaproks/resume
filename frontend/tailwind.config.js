/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}'],
  plugins:  [require('flowbite/plugin')],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#E2E2E2',
          dark: "#1D1D1D"
        },
        secondary: {
          light: 'black',
          dark: "white"
        },
        accent: {
          light: '#0F866E',
          dark: "#1ABC9C"
        },
      }
    }
  }
}
