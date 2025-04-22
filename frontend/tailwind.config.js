module.exports = {
  content: [
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4da3ff',
          DEFAULT: '#007bff',
          dark: '#0056b3'
        },
        secondary: {
          light: '#eaecef',
          DEFAULT: '#6c757d',
          dark: '#495057'
        }
      }
    }
  },
  plugins: [],
}
