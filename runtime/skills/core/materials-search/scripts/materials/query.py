from .cif_export import export_cif
from .providers import aflow, cod, materials_project, oqmd

PROVIDERS = {"cod": cod, "oqmd": oqmd, "aflow": aflow, "mp": materials_project}
IDENTIFIERS = {"cod": "file", "oqmd": "entry_id", "aflow": "auid", "mp": "material_id"}


def collect(formula, sources, limit, directory):
    records, warnings, failures = [], [], []
    for source in dict.fromkeys(sources):
        provider = PROVIDERS[source]
        try:
            entries = provider.query(formula, limit)
        except Exception as exc:
            failures.append({"source": source, "message": str(exc)})
            continue
        for index, entry in enumerate(entries[:limit], 1):
            identifier = str(entry[IDENTIFIERS[source]])
            result = {
                "source": source, "source_id": identifier,
                "metadata": {key: value for key, value in entry.items()
                             if key not in {"structure", "sites", "positions_fractional"}},
            }
            file = directory / f"{source}-{index:03d}.cif"
            try:
                export_cif(source, provider, entry, formula, file)
                result["cif"] = file.relative_to(directory.parent).as_posix()
            except Exception as exc:
                warnings.append({"source": source, "source_id": identifier, "message": str(exc)})
            records.append(result)
    return records, failures, warnings
