import * as React from "react"
import {
    ColumnDef,
    ColumnFiltersState,
    VisibilityState,
    flexRender,
    getCoreRowModel,
    getFilteredRowModel,
    getSortedRowModel,
    useReactTable,
    SortingState,
    OnChangeFn,
} from "@tanstack/react-table"
import { ChevronDown, ChevronUp, ChevronsUpDown, Loader2, Search, SlidersHorizontal } from "lucide-react"

import { cn } from "@/lib/utils"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[]
    data: TData[]
    isLoading?: boolean
    hasMore?: boolean
    onLoadMore?: () => void
    searchPlaceholder?: string
    searchColumn?: string
    selectable?: boolean
    onRowClick?: (row: TData) => void
    expandedContent?: (row: TData) => React.ReactNode
    className?: string
    sorting?: SortingState
    onSortingChange?: OnChangeFn<SortingState>
}

export function DataTable<TData, TValue>({
    columns,
    data,
    isLoading = false,
    hasMore = false,
    onLoadMore,
    searchPlaceholder = "Search...",

    selectable = false,
    onRowClick,
    expandedContent,
    className,
    sorting: externalSorting,
    onSortingChange: externalOnSortingChange,
}: DataTableProps<TData, TValue>) {
    const [internalSorting, setInternalSorting] = React.useState<SortingState>([])
    const sorting = externalSorting ?? internalSorting
    const onSortingChange = externalOnSortingChange ?? setInternalSorting

    const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
    const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
    const [rowSelection, setRowSelection] = React.useState({})
    const [globalFilter, setGlobalFilter] = React.useState("")
    const [expandedRows, setExpandedRows] = React.useState<Record<string, boolean>>({})

    // Infinite scroll observer
    const loadMoreRef = React.useRef<HTMLDivElement>(null)

    React.useEffect(() => {
        if (!onLoadMore || !hasMore) return

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && !isLoading) {
                    onLoadMore()
                }
            },
            { threshold: 0.1 }
        )

        if (loadMoreRef.current) {
            observer.observe(loadMoreRef.current)
        }

        return () => observer.disconnect()
    }, [hasMore, isLoading, onLoadMore])

    // Add selection column if selectable
    const allColumns = React.useMemo(() => {
        if (!selectable) return columns

        const selectColumn: ColumnDef<TData, TValue> = {
            id: "select",
            header: ({ table }) => (
                <Checkbox
                    checked={table.getIsAllPageRowsSelected()}
                    onCheckedChange={(value: boolean) => table.toggleAllPageRowsSelected(!!value)}
                    aria-label="Select all"
                />
            ),
            cell: ({ row }) => (
                <Checkbox
                    checked={row.getIsSelected()}
                    onCheckedChange={(value: boolean) => row.toggleSelected(!!value)}
                    aria-label="Select row"
                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                />
            ),
            enableSorting: false,
            enableHiding: false,
        }

        return [selectColumn, ...columns]
    }, [columns, selectable])

    const table = useReactTable({
        data,
        columns: allColumns,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        onSortingChange: onSortingChange,
        onColumnFiltersChange: setColumnFilters,
        onColumnVisibilityChange: setColumnVisibility,
        onRowSelectionChange: setRowSelection,
        onGlobalFilterChange: setGlobalFilter,
        globalFilterFn: "includesString",
        manualSorting: !!externalSorting,
        state: {
            sorting,
            columnFilters,
            columnVisibility,
            rowSelection,
            globalFilter,
        },
    })

    const toggleRowExpanded = (rowId: string) => {
        setExpandedRows((prev) => ({
            ...prev,
            [rowId]: !prev[rowId],
        }))
    }

    return (
        <div className={cn("flex flex-col gap-4", className)}>
            {/* Toolbar */}
            <div className="flex items-center justify-between gap-4">
                <div className="relative flex-1 max-w-sm ml-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder={searchPlaceholder}
                        value={globalFilter}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGlobalFilter(e.target.value)}
                        className="pl-10 bg-white dark:bg-secondary/50 border-border focus:border-primary text-foreground"
                    />
                </div>
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <button className="flex items-center gap-2 px-3 py-2 bg-secondary/50 border border-border rounded-lg text-sm text-foreground hover:bg-secondary transition-colors">
                            <SlidersHorizontal className="h-4 w-4" />
                            Columns
                        </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="bg-popover border-border">
                        {table
                            .getAllColumns()
                            .filter((column) => column.getCanHide())
                            .map((column) => (
                                <DropdownMenuCheckboxItem
                                    key={column.id}
                                    className="text-foreground capitalize"
                                    checked={column.getIsVisible()}
                                    onCheckedChange={(value: boolean) => column.toggleVisibility(!!value)}
                                >
                                    {column.id}
                                </DropdownMenuCheckboxItem>
                            ))}
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>

            {/* Table */}
            <div className="glass-panel rounded-xl overflow-hidden">
                <div className="overflow-x-auto custom-scrollbar">
                    <Table className="table-fixed w-full">
                        <TableHeader>
                            {table.getHeaderGroups().map((headerGroup) => (
                                <TableRow key={headerGroup.id} className="border-b border-border bg-muted/5 hover:bg-muted/5">
                                    {headerGroup.headers.map((header) => (
                                        <TableHead
                                            key={header.id}
                                            className="text-xs font-bold uppercase tracking-widest text-muted-foreground"
                                            style={{ width: header.getSize() !== 150 ? header.getSize() : undefined }}
                                        >
                                            {header.isPlaceholder ? null : (
                                                <div
                                                    className={cn(
                                                        "flex items-center gap-2",
                                                        header.column.getCanSort() && "cursor-pointer select-none hover:text-foreground"
                                                    )}
                                                    onClick={header.column.getToggleSortingHandler()}
                                                >
                                                    {flexRender(header.column.columnDef.header, header.getContext())}
                                                    {header.column.getCanSort() && (
                                                        <span className="text-muted-foreground">
                                                            {{
                                                                asc: <ChevronUp className="h-4 w-4" />,
                                                                desc: <ChevronDown className="h-4 w-4" />,
                                                            }[header.column.getIsSorted() as string] ?? (
                                                                    <ChevronsUpDown className="h-4 w-4" />
                                                                )}
                                                        </span>
                                                    )}
                                                </div>
                                            )}
                                        </TableHead>
                                    ))}
                                </TableRow>
                            ))}
                        </TableHeader>
                        <TableBody>
                            {table.getRowModel().rows?.length ? (
                                table.getRowModel().rows.map((row) => {
                                    const rowId = (row.original as { id?: string })?.id || row.id
                                    const isExpanded = expandedRows[rowId]

                                    return (
                                        <React.Fragment key={row.id}>
                                            <TableRow
                                                data-state={row.getIsSelected() && "selected"}
                                                className={cn(
                                                    "border-b border-border/50 transition-colors",
                                                    (onRowClick || expandedContent) && "cursor-pointer hover:bg-muted/50",
                                                    isExpanded && "bg-muted/50 border-l-4 border-l-primary"
                                                )}
                                                onClick={() => {
                                                    if (expandedContent) {
                                                        toggleRowExpanded(rowId)
                                                    }
                                                    onRowClick?.(row.original)
                                                }}
                                            >
                                                {row.getVisibleCells().map((cell) => (
                                                    <TableCell key={cell.id} className="text-foreground">
                                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                            {expandedContent && isExpanded && (
                                                <TableRow className="bg-muted/30 hover:bg-muted/30">
                                                    <TableCell colSpan={allColumns.length} className="border-t border-border">
                                                        {expandedContent(row.original)}
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </React.Fragment>
                                    )
                                })
                            ) : (
                                <TableRow>
                                    <TableCell colSpan={allColumns.length} className="h-24 text-center text-muted-foreground">
                                        {isLoading ? "Loading..." : "No results."}
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>

                {/* Infinite scroll trigger */}
                {hasMore && (
                    <div ref={loadMoreRef} className="flex items-center justify-center py-4">
                        {isLoading && (
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Loading more...
                            </div>
                        )}
                    </div>
                )}

                {/* Stats footer */}
                <div className="border-t border-border bg-muted/5 px-6 py-3 flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                        {table.getFilteredRowModel().rows.length} row(s) displayed
                        {selectable && ` · ${table.getFilteredSelectedRowModel().rows.length} selected`}
                    </span>
                    {hasMore && !isLoading && (
                        <span className="text-xs text-muted-foreground">Scroll for more</span>
                    )}
                </div>
            </div>
        </div>
    )
}
