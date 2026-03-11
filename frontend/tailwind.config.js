/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'navy-header': '#ffffff',
        'navy-text': '#0f172a',
        'blue-accent': '#4f46e5',
        'blue-accent-hover': '#4338ca',
      }
    },
  },
  plugins: [],
}
