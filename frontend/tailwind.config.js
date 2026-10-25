/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sleuth: {
          950: '#060911',
          900: '#090D16',
          850: '#0D1424',
          800: '#111C32',
          700: '#1E2D4A',
          600: '#2A3F66',
          500: '#3D5A8A',
        },
        cyanAccent: {
          400: '#38BDF8',
          500: '#0EA5E9',
          600: '#0284C7',
        },
        verifiedGreen: {
          400: '#34D399',
          500: '#10B981',
          600: '#059669',
        },
        warningAmber: {
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
        },
        dangerRed: {
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
