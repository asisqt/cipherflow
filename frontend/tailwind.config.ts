/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        cipher: {
          50:  '#eef5ff',
          100: '#d9e8ff',
          200: '#bcd8ff',
          300: '#8ec1ff',
          400: '#589fff',
          500: '#3380ff',
          600: '#1a5ef5',
          700: '#1349e1',
          800: '#163cb6',
          900: '#18378f',
          950: '#142357',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
