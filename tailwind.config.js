/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        hibp: {
          bg: "#0B0F19",       // Deep Charcoal/Obsidian background
          sidebar: "#0D1322",  // Slightly elevated sidebar tone
          card: "#111827",     // Card container fill
          border: "#1F293D",   // Subtle border divider
          active: "#00E5FF",   // Vivid Cyan accent
          hover: "#162032",
        }
      }
    },
  },
  plugins: [],
}