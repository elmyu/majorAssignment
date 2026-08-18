module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2021: true,
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
  },
  extends: ['eslint:recommended', 'plugin:vue/recommended', 'prettier'],
  plugins: ['vue', 'prettier'],
  rules: {
    'prettier/prettier': ['error', { endOfLine: 'auto' }],
    'no-console': 'off',
    'no-unused-vars': 'off',
    'no-empty': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/attributes-order': 'off',
  },
};
