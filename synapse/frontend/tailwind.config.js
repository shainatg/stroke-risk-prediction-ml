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
        background: {
          DEFAULT: "#0a0b0e",
          secondary: "#101216",
          tertiary: "#16181f",
          card: "#12141a",
          elevated: "#1a1d26"
        },
        surface: {
          50: "#141720",
          100: "#1a1d28",
          200: "#222736",
          300: "#2d3345",
          border: "#232836",
          hover: "#2a3142"
        },
        cyan: {
          DEFAULT: "#06b6d4",
          glow: "rgba(6, 182, 212, 0.15)",
          muted: "#0891b2",
          dark: "#0e7490"
        },
        indigo: {
          DEFAULT: "#6366f1",
          glow: "rgba(99, 102, 241, 0.15)",
          muted: "#4f46e5",
          dark: "#3730a3"
        },
        lavender: {
          DEFAULT: "#a855f7",
          subtle: "#c084fc",
          dim: "#7e22ce"
        },
        slate: {
          850: "#141722",
          900: "#0e111a",
          950: "#080a0f"
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        display: ['Plus Jakarta Sans', 'Inter', 'sans-serif']
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.4)',
        'premium': '0 4px 20px -2px rgba(0, 0, 0, 0.5), 0 2px 6px -1px rgba(0, 0, 0, 0.3)',
        'glow-cyan': '0 0 25px -5px rgba(6, 182, 212, 0.25)',
        'glow-indigo': '0 0 25px -5px rgba(99, 102, 241, 0.25)'
      }
    },
  },
  plugins: [],
}
