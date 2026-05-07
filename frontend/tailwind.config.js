/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        triangle: "#A855F7",
        square: "#3B82F6",
        circle: "#EF4444",
        canvas: "#FBF8F3",
        ink: "#2A2A33",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["Lora", "ui-serif", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};
