import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(d: string | Date, lang: string = "en"): string {
  const date = typeof d === "string" ? new Date(d) : d;
  return date.toLocaleDateString(lang === "id" ? "id-ID" : "en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}
