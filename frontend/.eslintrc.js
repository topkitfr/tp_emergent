module.exports = {
  "parser": "@babel/eslint-parser",
  "parserOptions": {
    "requireConfigFile": false,
    "sourceType": "module",
    "ecmaVersion": 2020,
    "ecmaFeatures": {
      "jsx": true
    },
    "babelOptions": {
      "presets": ["@babel/preset-react"]
    }
  },
  "env": {
    "browser": true,
    "es6": true,
    "node": true
  },
  "extends": ["eslint:recommended"],
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "off"
  }
};