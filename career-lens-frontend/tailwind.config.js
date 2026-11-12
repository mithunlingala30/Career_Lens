/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#e6ebf7', navy: '#14204a', muted: '#5b6892',
        bright: { blue: '#2f6bff', violet: '#7a3cff', pink: '#ff3d95', orange: '#ff8a1f', teal: '#00c4a7', yellow: '#ffc226', green: '#22c55e' },
      },
      fontFamily: { sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'], display: ['"Sora"', '"Plus Jakarta Sans"', 'sans-serif'] },
    },
  },
  plugins: [],
};
