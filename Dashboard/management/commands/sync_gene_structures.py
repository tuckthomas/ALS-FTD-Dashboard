import requests
from django.core.management.base import BaseCommand
from Dashboard.models import Gene, GeneStructure

class Command(BaseCommand):
    help = 'Syncs gene structures with PDB and AlphaFold'

    def handle(self, *args, **kwargs):
        self.stdout.write("Syncing gene structures...")

        # Comprehensive gene structure mappings for Definitive ALS and Strong Evidence genes
        # PDB IDs come from experimental structures
        # UniProt accessions are used for AlphaFold predictions
        genes_to_sync = [
            # Definitive ALS genes
            {
                "symbol": "SOD1",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "1SPD", "title": "Human SOD1 dimer", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "FUS",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "5W3N", "title": "FUS LC domain fibrils", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "TARDBP",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "4IUF", "title": "TDP-43 RRM1 domain", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "C9orf72",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "Q96LT7", "title": "AlphaFold Predicted", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "TBK1",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "4IM0", "title": "TBK1 kinase domain", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "OPTN",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "5B83", "title": "Optineurin coiled-coil domain", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "VCP",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "5FTN", "title": "VCP/p97 hexamer", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "UBQLN2",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "Q9UHD9", "title": "Ubiquilin-2 AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "PFN1",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "1FIK", "title": "Profilin-1 structure", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "HNRNPA1",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "1HA1", "title": "hnRNP A1 UP1 domain", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "KIF5A",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "3KIN", "title": "Kinesin motor domain", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "NEK1",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "Q96PY6", "title": "NEK1 AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "VAPB",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "3IKK", "title": "VAPB MSP domain", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "CHCHD10",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "Q8WYQ3", "title": "CHCHD10 AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "ANXA11",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "P50995", "title": "Annexin A11 AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "EPHA4",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "2WO1", "title": "EphA4 kinase domain", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "UNC13A",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "Q9UPW8", "title": "UNC13A AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            # Strong Evidence genes
            {
                "symbol": "CCNF",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "P24864", "title": "Cyclin-F AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "HFE",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "1A6Z", "title": "HFE protein structure", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "NIPA1",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "Q7RTP0", "title": "NIPA1 AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "ATXN1",
                "structures": [
                    {"source": GeneStructure.SOURCE_PDB, "external_id": "2M41", "title": "Ataxin-1 AXH domain", "is_primary": True, "visual_style": "cartoon"}
                ]
            },
            {
                "symbol": "TUBA4A",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "P68366", "title": "Tubulin alpha-4A AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "CFAP410",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "Q8IYT1", "title": "CFAP410 AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
            {
                "symbol": "SCFD1",
                "structures": [
                    {"source": GeneStructure.SOURCE_ALPHAFOLD, "external_id": "Q8WVM8", "title": "SCFD1 AlphaFold", "is_primary": True, "alphafold_view": True}
                ]
            },
        ]

        for gene_data in genes_to_sync:
            symbol = gene_data["symbol"]
            try:
                gene = Gene.objects.get(gene_symbol__iexact=symbol)
            except Gene.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Gene {symbol} not found, skipping."))
                continue

            for struct_data in gene_data["structures"]:
                external_id = struct_data["external_id"]
                source_type = struct_data["source"]
                
                structure, created = GeneStructure.objects.update_or_create(
                    gene=gene,
                    source_type=source_type,
                    external_id=external_id,
                    defaults={
                        "title": struct_data.get("title", ""),
                        "is_primary": struct_data.get("is_primary", False),
                        "visual_style": struct_data.get("visual_style", "cartoon"),
                        "hide_controls": struct_data.get("hide_controls", True),
                        "alphafold_view": struct_data.get("alphafold_view", False),
                    }
                )

                if source_type == GeneStructure.SOURCE_ALPHAFOLD:
                    self.resolve_alphafold(structure)

                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"{action} structure {external_id} for {symbol}"))

    def resolve_alphafold(self, structure):
        """Fetches the AlphaFold API to get the mmCIF URL."""
        uniprot_acc = structure.external_id
        api_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_acc}"
        
        try:
            resp = requests.get(api_url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    model_data = data[0]
                    cif_url = model_data.get("cifUrl")
                    if cif_url:
                        structure.custom_data_url = cif_url
                        structure.custom_data_format = "cif"
                        structure.save()
                        self.stdout.write(f"  Resolved AlphaFold URL: {cif_url}")
            else:
                self.stdout.write(self.style.ERROR(f"  Failed to resolve AlphaFold for {uniprot_acc}: Status {resp.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error resolving AlphaFold for {uniprot_acc}: {e}"))
