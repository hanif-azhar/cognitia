import { cn } from "@/lib/utils";

type ShapeProps = { className?: string; size?: number; filled?: boolean };

export function Triangle({ className, size = 18, filled = false }: ShapeProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={cn("text-triangle", className)}
      aria-hidden
    >
      <path
        d="M12 3 L21 20 L3 20 Z"
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Square({ className, size = 18, filled = false }: ShapeProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={cn("text-square", className)}
      aria-hidden
    >
      <rect
        x="4"
        y="4"
        width="16"
        height="16"
        rx="2"
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="2"
      />
    </svg>
  );
}

export function Circle({ className, size = 18, filled = false }: ShapeProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={cn("text-circle", className)}
      aria-hidden
    >
      <circle
        cx="12"
        cy="12"
        r="9"
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="2"
      />
    </svg>
  );
}

export function ShapeTrio({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <Circle size={20} />
      <Triangle size={20} />
      <Square size={20} />
    </div>
  );
}
