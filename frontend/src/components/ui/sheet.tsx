import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

interface SheetProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    children: React.ReactNode
    side?: "left" | "right"
}

interface SheetContentProps {
    children: React.ReactNode
    className?: string
    side?: "left" | "right"
    onClose?: () => void
}

const SheetContext = React.createContext<{
    open: boolean
    onOpenChange: (open: boolean) => void
    side: "left" | "right"
}>({ open: false, onOpenChange: () => { }, side: "left" })

export function Sheet({ open, onOpenChange, children, side = "left" }: SheetProps) {
    // Close on escape key
    React.useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape" && open) {
                onOpenChange(false)
            }
        }
        document.addEventListener("keydown", handleEscape)
        return () => document.removeEventListener("keydown", handleEscape)
    }, [open, onOpenChange])

    // Prevent body scroll when open
    React.useEffect(() => {
        if (open) {
            document.body.style.overflow = "hidden"
        } else {
            document.body.style.overflow = ""
        }
        return () => {
            document.body.style.overflow = ""
        }
    }, [open])

    return (
        <SheetContext.Provider value={{ open, onOpenChange, side }}>
            {children}
        </SheetContext.Provider>
    )
}

export function SheetTrigger({
    children,
    asChild,
    className,
}: {
    children: React.ReactNode
    asChild?: boolean
    className?: string
}) {
    const { onOpenChange } = React.useContext(SheetContext)

    if (asChild && React.isValidElement(children)) {
        return React.cloneElement(children as React.ReactElement<any>, {
            onClick: (e: React.MouseEvent) => {
                (children as React.ReactElement<any>).props.onClick?.(e)
                onOpenChange(true)
            },
        })
    }

    return (
        <button className={className} onClick={() => onOpenChange(true)}>
            {children}
        </button>
    )
}

export function SheetContent({ children, className, side, onClose }: SheetContentProps) {
    const { open, onOpenChange, side: contextSide } = React.useContext(SheetContext)
    const actualSide = side || contextSide

    if (!open) return null

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
                onClick={() => {
                    onOpenChange(false)
                    onClose?.()
                }}
            />

            {/* Sheet Panel */}
            <div
                className={cn(
                    "fixed inset-y-0 z-50 flex flex-col bg-background border-border shadow-2xl",
                    "animate-in duration-300 ease-out",
                    actualSide === "left" && "left-0 border-r slide-in-from-left",
                    actualSide === "right" && "right-0 border-l slide-in-from-right",
                    "w-[85vw] max-w-[320px]",
                    className
                )}
            >
                {/* Fixed Header with Close button */}
                <div className="flex-shrink-0 flex items-center justify-end p-4 border-b border-border/50 bg-background">
                    <button
                        onClick={() => {
                            onOpenChange(false)
                            onClose?.()
                        }}
                        className="p-1.5 rounded-lg bg-secondary/50 hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-4">
                    {children}
                </div>
            </div>
        </>
    )
}

export function SheetHeader({
    children,
    className,
}: {
    children: React.ReactNode
    className?: string
}) {
    return (
        <div className={cn("mb-4", className)}>
            {children}
        </div>
    )
}

export function SheetTitle({
    children,
    className,
}: {
    children: React.ReactNode
    className?: string
}) {
    return (
        <h2 className={cn("text-lg font-bold text-foreground", className)}>
            {children}
        </h2>
    )
}
