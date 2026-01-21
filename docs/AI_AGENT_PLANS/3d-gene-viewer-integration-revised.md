# Integration Guide (Revised): 3D Gene/Protein Structure Viewer for https://f-als.com

**Audience:** Agentic AI implementing this feature in a **React + Django** stack.  
**Goal:** Add an embeddable 3D structure viewer on gene pages (ALS/FTD genes) without hosting large structure files.

---

## 0) Design Constraints and Non‑Goals

### Constraints
- **Do not host** full PDB/mmCIF/PDB files in your infrastructure; **stream** from authoritative public sources.
- Support **multiple structures per gene** (different domains, mutants, assemblies, predicted vs experimental).

### Non‑Goals
- No clinical interpretation, pathogenicity scoring, or “variant effect” claims.
- Unless absolutely necessary, no custom 3D rendering engine; use Mol* via PDBe’s component.

---

## 1) Recommended Viewer Integration Strategy

Use **PDBe Mol* as a Web Component** (`<pdbe-molstar />`) because it:
- Is already a packaged, embeddable Mol* implementation.
- Supports either:
  - `molecule-id` (PDB ID), **or**
  - `custom-data-url` + `custom-data-format` (e.g., load AlphaFold mmCIF by URL).
- Can enable AlphaFold confidence coloring via `alphafold-view="true"` when loading predicted models.

This avoids coupling your UI to PDBe internals while retaining Mol* capabilities.

---

## 2) Data Sources (Free, Streamed)

### A) Experimental structures: RCSB PDB
- Use a **4-character PDB ID** (example: `1SPD`).
- When you need a direct file URL (for proxying or custom load), use RCSB file download services, e.g.:
  - mmCIF: `https://files.rcsb.org/download/<PDB_ID>.cif`

### B) Predicted structures: AlphaFold DB (EMBL‑EBI)
- Use the **UniProt accession** as the “lookup key” to retrieve model metadata and file URLs via the AlphaFold API:
  - `https://alphafold.ebi.ac.uk/api/prediction/<UNIPROT_ACCESSION>`
- The API response includes URLs for **mmCIF/PDB** model files and related artifacts (e.g., PAE).  
- Prefer mmCIF for better compatibility with confidence coloring themes.

### C) Optional: PDBe Model Server
- For some workflows you can load PDBe-provided mmCIF URLs (useful when you want consistent domain/annotation behavior).
- If you do, ensure the URL supports CORS (PDBe generally does).

---

## 3) Data Model (Django)

Your original `Gene.structure_id` approach is too limiting. Use a separate structure table so you can:
- store multiple structures per gene,
- designate a primary/default structure,
- track source, metadata, and fallback options.

### 3.1 Models

**File:** `genes/models.py`

```python
Exiting gene model already in palce. Add Gene Structure model...



class GeneStructure(models.Model):
    SOURCE_PDB = "pdb"
    SOURCE_ALPHAFOLD = "alphafold"
    SOURCE_CUSTOM = "custom"

    FOREIGN KEY TO GENE MODEL

    source_type = models.CharField(
        max_length=20,
        choices=[
            (SOURCE_PDB, "PDB"),
            (SOURCE_ALPHAFOLD, "AlphaFold"),
            (SOURCE_CUSTOM, "Custom URL"),
        ],
    )

    # For PDB: 4-char ID (e.g., 1SPD). For AlphaFold: UniProt accession (e.g., Q96LT7) or AF model id if you store it.
    external_id = models.CharField(max_length=64)

    # Optional display metadata
    title = models.CharField(max_length=255, blank=True, default="")
    is_primary = models.BooleanField(default=False)

    # Viewer options (store as explicit fields for safety; avoid arbitrary JSON if you can)
    assembly_id = models.CharField(max_length=32, blank=True, default="")  # e.g. "1" or "preferred"
    visual_style = models.CharField(max_length=64, blank=True, default="")  # e.g. "cartoon"
    hide_controls = models.BooleanField(default=True)
    alphafold_view = models.BooleanField(default=False)  # apply confidence coloring theme when using predicted models

    # For SOURCE_CUSTOM only (optional)
    custom_data_url = models.URLField(blank=True, default="")
    custom_data_format = models.CharField(max_length=16, blank=True, default="cif")  # "cif" or "pdb"

    class Meta:
        indexes = [
            models.Index(fields=["source_type", "external_id"]),
            models.Index(fields=["gene", "is_primary"]),
        ]

    def __str__(self) -> str:
        return f"{self.gene.symbol} [{self.source_type}:{self.external_id}]"
```

### 3.2 “Exactly one primary” guardrail
Implement an application-level rule:
- When saving a structure with `is_primary=True`, unset other primaries for that gene in the same transaction.

---

## 4) Backend API (Django Ninja / DRF)

Expose a clean API that **never** asks the browser to construct arbitrary external URLs.

### 4.1 Endpoints
- `GET /api/genes/<symbol>`  
  Returns gene info + a list of available structures + which is primary.
- `GET /api/genes/<symbol>/structure`  
  Returns a single “resolved viewer payload” for the chosen structure (default to primary).
- (Optional) `GET /api/structures/<id>/resolve`  
  Returns resolved URLs and component attributes, enforcing allowlists.

### 4.2 Output Shape (Viewer Payload)
Return an object the frontend can pass directly to `<pdbe-molstar>`:

```json
{
  "gene": {"symbol": "SOD1", "name": "..."},
  "structure": {
    "id": 123,
    "source_type": "pdb",
    "external_id": "1SPD",
    "componentProps": {
      "molecule-id": "1SPD",
      "hide-controls": "true",
      "bg-color-r": "255",
      "bg-color-g": "255",
      "bg-color-b": "255"
    }
  }
}
```

For AlphaFold (URL-based load):

```json
{
  "structure": {
    "source_type": "alphafold",
    "external_id": "Q96LT7",
    "componentProps": {
      "custom-data-url": "https://.../model.cif",
      "custom-data-format": "cif",
      "hide-controls": "true",
      "alphafold-view": "true"
    }
  }
}
```

### 4.3 AlphaFold URL resolution strategy (recommended)
1. Look up AlphaFold metadata via API:
   - `https://alphafold.ebi.ac.uk/api/prediction/<uniprot_accession>`
2. Extract **mmCIF URL** from response.
3. Cache it server-side (e.g., 24h) to avoid repeated calls.

**Important:** Don’t hardcode AlphaFold file version suffixes; let the API provide the canonical URLs.

---

## 5) Frontend (React)

### 5.1 Load the Web Component
If you want the most portable path (works without npm installs), load PDBe Mol* via CDN exactly once.

**Where:**
- Next.js: `_document.tsx` or a layout component that runs on the client.
- Vite/React SPA: `index.html`.
- Django templates: base template that wraps your React mount.

**Include:**
- CSS
- JS web component script



```

### 5.2 React wrapper component
Key points to get right:
- The custom element must only run on the client (guard SSR).
- Force a remount on structure change (Mol* instances don’t always hot-swap cleanly).
- Pass only server-resolved props (don’t build external URLs in the browser).

```tsx
import React, { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

declare global {
  namespace JSX {
    interface IntrinsicElements {
      "pdbe-molstar": any;
    }
  }
}

type ViewerPayload = {
  gene: { symbol: string; name?: string };
  structure: {
    id: number;
    source_type: "pdb" | "alphafold" | "custom";
    external_id: string;
    componentProps: Record<string, string>;
    title?: string;
  };
};

export function GeneStructureViewer({ payload }: { payload: ViewerPayload }) {
  const key = useMemo(() => {
    const p = payload.structure.componentProps;
    // Remount whenever the underlying load target changes
    return `${payload.structure.source_type}:${payload.structure.external_id}:${p["molecule-id"] || ""}:${p["custom-data-url"] || ""}`;
  }, [payload]);

  // SSR guard if needed (Next.js):
  if (typeof window === "undefined") return null;

  return (
    <Card className="w-full max-w-5xl mx-auto">
      <CardHeader>
        <CardTitle>
          {payload.gene.symbol} {payload.structure.title ? `— ${payload.structure.title}` : "— 3D Structure"}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 h-[560px] relative">
        <pdbe-molstar key={key} className="w-full h-full block" {...payload.structure.componentProps} />
      </CardContent>
    </Card>
  );
}
```

### 5.3 UI recommendations
- Add a structure selector (dropdown) when multiple are available:
  - “Experimental (PDB)”, “Predicted (AlphaFold)”, plus domain-specific structures.
- Show metadata under the viewer:
  - source, ID, and a “view on RCSB/AlphaFold” link.
- Provide a fallback empty state:
  - “No structure available yet” + instructions for maintainers to add one.

---

## 6) Bootstrap: Populate Initial Structures

Avoid hardcoding “one ID per gene” long-term. Use it only to seed the dataset.

### 6.1 Starter structures (validated examples)
These are reasonable initial seeds:

| Gene | Source | ID | Notes |
|---|---|---|---|
| SOD1 | PDB | 1SPD | Human SOD1 (ALS-related context) |
| FUS | PDB | 5W3N | FUS LC domain fibrils (solid-state NMR) |
| TARDBP (TDP-43) | PDB | 4IUF | TDP-43 RRM1 domain complex |
| C9orf72 | AlphaFold | Q96LT7 | Use AlphaFold API to resolve mmCIF URL (model id is AF-Q96LT7-F1 on the entry page) |

### 6.2 Sustainable approach (recommended)
Implement a management command:
- `python manage.py sync_gene_structures`
  - Ensures each gene has:
    - `uniprot_accession` (if known)
    - at least one `GeneStructure` record (if resolvable)
  - For AlphaFold: resolve via API (cache results)
  - For PDB: allow a curated mapping table to choose “best” entry per gene (don’t guess automatically unless you define strict rules)

---

## 7) CORS, CSP, and Proxying

### Preferred (simplest)
Load structures directly in the browser from trusted domains that already support CORS (AlphaFold/RCSB generally do).

### If you hit CORS or CSP restrictions
Add a **backend proxy endpoint**:
- `GET /api/structure-proxy?url=<encoded>`
- Enforce a strict **allowlist** of upstream hostnames:
  - `files.rcsb.org`
  - `models.rcsb.org`
  - `alphafold.ebi.ac.uk`
  - (optionally) `www.ebi.ac.uk` (PDBe resources)
- Stream the response, set correct content-type, and apply caching headers.

Never allow arbitrary, user-supplied URLs without an allowlist.

---

## 8) QA Checklist

1. **Smoke test**: load a known PDB ID using `molecule-id` (e.g., `1cbs`).
2. **AlphaFold test**: resolve a UniProt accession via AlphaFold API and load mmCIF via `custom-data-url`.
3. **Switching structures**: change dropdown selection and confirm the viewer remounts and renders the new structure.
4. **Mobile/low-power**: verify the page remains usable; offer “hide controls” and default to lighter visuals.
5. **Error states**:
   - API resolution failure (AlphaFold down): show “Predicted model temporarily unavailable”.
   - Missing structure mapping: show “No structure mapped”.
6. **Performance**:
   - Ensure the viewer only loads when visible (optional: IntersectionObserver + lazy mount).

---

## 9) Operational Notes

- Log structure resolution errors with:
  - gene symbol, source, external_id, upstream HTTP status, and timing.
- Cache resolved AlphaFold URLs and gene payloads to reduce latency and upstream load.
- Pin PDBe Mol* CDN version for deterministic behavior; bump on purpose after testing.

---

## References (for implementers)
- PDBe Component Library and `<pdbe-molstar>` usage (attributes, `custom-data-url`, `alphafold-view`)  
- RCSB PDB file download services (`files.rcsb.org/download/<id>.cif`)  
- AlphaFold DB API endpoint keyed by UniProt accession (`/api/prediction/<accession>`)  
