/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm editorial palette - 高对比度版本（大幅加深文字颜色）
        cream: {
          50: '#FDFCFA',
          100: '#FAF8F5',
          200: '#F5F1EB',
          300: '#EBE5DB',
          400: '#DDD4C6',
        },
        espresso: {
          50: '#F7F5F3',
          100: '#E8E3DD',
          200: '#C5B8A8', // 从 #D1C7BB 加深
          300: '#736049', // 从 #8B7862 再次加深
          400: '#5A4734', // 从 #6B5442 再次加深
          500: '#4A3A2A', // 从 #5A4737 再次加深
          600: '#3A2F20', // 从 #4A3C2E 再次加深
          700: '#2A2318', // 从 #3A2F22 大幅加深
          800: '#1A1510', // 从 #2A2118 大幅加深
          900: '#0F0C08', // 从 #1A150F 大幅加深
        },
        ink: {
          light: '#2A2A2A', // 从 #3A3A3A 再次加深到 #2A2A2A
          DEFAULT: '#0F0F0F', // 从 #1A1A1A 加深到接近纯黑
          dark: '#000000', // 纯黑
        },
        accent: {
          sage: '#8B9E8B',
          'sage-text': '#2A3A2A', // 从 #3A4A3A 加深，确保高对比度
          terracotta: '#C4876B',
          'terracotta-dark': '#8A4F35', // 从 #A0654A 再次加深
          gold: '#C9A962',
          'gold-dark': '#8A6F2A', // 从 #A88842 再次加深
        }
      },
      fontFamily: {
        'display': ['"Playfair Display"', 'Georgia', 'serif'],
        'body': ['"Source Serif 4"', 'Georgia', 'serif'],
        'sans': ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      animation: {
        'ink-spread': 'inkSpread 2s ease-out forwards',
        'fade-up': 'fadeUp 0.6s ease-out forwards',
        'slide-in': 'slideIn 0.4s ease-out forwards',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        inkSpread: {
          '0%': { transform: 'scale(0)', opacity: '1' },
          '100%': { transform: 'scale(1)', opacity: '0.8' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
      boxShadow: {
        'paper': '0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06)',
        'paper-hover': '0 2px 8px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.1)',
        'inner-soft': 'inset 0 2px 4px rgba(0,0,0,0.04)',
      },
    },
  },
  plugins: [],
}
