import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#FFFFFF",
          2: "#F9FAF9",
          3: "#F3F5F3",
          4: "#EAECEB",
          5: "#E1E3E1",
        },
        border: {
          DEFAULT: "rgba(15, 41, 22, 0.1)",
          2: "rgba(15, 41, 22, 0.2)",
        },
        ink: {
          DEFAULT: "#0F2916",
          2: "#1B3B22",
          3: "#3D5743",
          4: "#5B7361",
        },
        gold: {
          DEFAULT: "#2D6A4F",
          2: "#1B4332",
          3: "#74C69D",
          bg: "rgba(45, 106, 79, 0.08)",
          "bg-2": "rgba(45, 106, 79, 0.14)",
        },
        green: {
          DEFAULT: "#4A7C59",
          2: "#5E9E70",
          bg: "rgba(74,124,89,0.1)",
        },
        blue: {
          DEFAULT: "#3D6B8E",
          2: "#5A8FB5",
          bg: "rgba(61,107,142,0.1)",
        },
      },
      fontFamily: {
        sans: ["var(--font-syne)", "sans-serif"],
        serif: ["var(--font-libre-baskerville)", "serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      borderRadius: {
        DEFAULT: "10px",
        xl: "22px",
      },
      animation: {
        "fade-in-up": "fadeInUp 0.5s ease-out forwards",
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    }
  },
  plugins: []
};

export default config;
