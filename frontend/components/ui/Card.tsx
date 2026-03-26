import { ReactNode } from "react";

type StatusBorder = "safe" | "warning" | "danger" | "none";

interface CardProps {
  children: ReactNode;
  statusBorder?: StatusBorder;
  className?: string;
  onClick?: () => void;
}

const borderStyles: Record<StatusBorder, string> = {
  safe: "border-l-[3px] border-l-safe",
  warning: "border-l-[3px] border-l-warning",
  danger: "border-l-[3px] border-l-danger",
  none: "",
};

export function Card({ children, statusBorder = "none", className = "", onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      className={`
        bg-surface border border-border rounded-xl p-4
        ${borderStyles[statusBorder]}
        ${onClick ? "cursor-pointer hover:translate-y-[-2px] transition-transform duration-150" : ""}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
