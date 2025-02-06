import typescriptEslint from "@typescript-eslint/eslint-plugin";
import react from "eslint-plugin-react";
import jsxA11Y from "eslint-plugin-jsx-a11y";
import tsParser from "@typescript-eslint/parser";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default [...compat.extends("next/core-web-vitals"), {
    plugins: {
        "@typescript-eslint": typescriptEslint,
        react,
        "jsx-a11y": jsxA11Y,
    },

    languageOptions: {
        parser: tsParser,
    },

    rules: {
        "@typescript-eslint/no-unused-vars": ["warn", {
            vars: "all",
            varsIgnorePattern: "^_",
            args: "after-used",
            argsIgnorePattern: "^_",
        }],

        "@next/next/no-html-link-for-pages": "warn",
        "@typescript-eslint/no-explicit-any": "warn",
        "react-hooks/exhaustive-deps": "warn",
        "jsx-a11y/alt-text": "warn",
        "prefer-const": "error",
        "react/no-unescaped-entities": "off",
    },
}];