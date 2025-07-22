import { cn } from "@/lib/utils"

const Alert = ({ className, variant = "default", ...props }: any) => (
  <div
    role="alert"
    className={cn(
      "relative w-full rounded-lg border p-4",
      variant === "destructive" &&
        "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
      className
    )}
    {...props}
  />
)

const AlertDescription = ({ className, ...props }: any) => (
  <div
    className={cn("text-sm [&_p]:leading-relaxed", className)}
    {...props}
  />
)

const AlertTitle = ({ className, ...props }: any) => (
  <h5
    className={cn("mb-1 font-medium leading-none tracking-tight", className)}
    {...props}
  />
)

export { Alert, AlertDescription, AlertTitle }