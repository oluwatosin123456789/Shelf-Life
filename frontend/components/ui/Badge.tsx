type Status = "fresh" | "warning" | "spoiled" | "info";

interface BadgeProps {
  status: Status;
  label: string;
  size?: "sm" | "lg";
}

const statusStyles: Record<Status, string> = {
  fresh: "bg-safe text-white",
  warning: "bg-warning text-white",
  spoiled: "bg-danger text-white",
  info: "bg-border text-text",
};

const sizeStyles = {
  sm: "text-xs px-2.5 py-1 font-medium",
  lg: "text-xl px-6 py-2 font-bold uppercase tracking-wide",
};

export function Badge({ status, label, size = "sm" }: BadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center rounded-full
        ${statusStyles[status]}
        ${sizeStyles[size]}
      `}
    >
      {label}
    </span>
  );
}
