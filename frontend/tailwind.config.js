

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {},
  },
  plugins:  [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["light"],
          primary: "E2E2E2",
          secondary: "black",
          accent: "0F866E",
          "base-100": "E2E2E2",
        },
        dark: {
          ...require("daisyui/src/theming/themes")["dark"],
          primary: "1D1D1D",
          secondary: "white",
          accent: "1ABC9C",
          "base-100": "1D1D1D",
        },
      }
    ],
  },
}

