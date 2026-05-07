import { create } from "zustand";

type Theme = "light" | "dark" | "auto";

type UIState = {
  theme: Theme;
  setTheme: (t: Theme) => void;
  language: "en" | "id";
  setLanguage: (l: "en" | "id") => void;
};

const storedTheme = (typeof localStorage !== "undefined" &&
  (localStorage.getItem("cognitia.theme") as Theme | null)) || "light";
const storedLang = ((typeof localStorage !== "undefined" &&
  (localStorage.getItem("cognitia.lang") as "en" | "id" | null)) || "en") as "en" | "id";

function applyTheme(t: Theme) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  const dark = t === "dark" || (t === "auto" && window.matchMedia?.("(prefers-color-scheme: dark)").matches);
  root.classList.toggle("dark", !!dark);
}

applyTheme(storedTheme);

export const useUI = create<UIState>((set) => ({
  theme: storedTheme,
  setTheme: (t) => {
    localStorage.setItem("cognitia.theme", t);
    applyTheme(t);
    set({ theme: t });
  },
  language: storedLang,
  setLanguage: (l) => {
    localStorage.setItem("cognitia.lang", l);
    set({ language: l });
  },
}));
