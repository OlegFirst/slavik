"""
Standards Loader - Load ISO, BCI, WHO, NIST standards

Features:
- Version management
- Cache-based loading (MD5 hash)
- Automatic indexing (Vector DB + Knowledge Graph)
- Metadata tracking
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class StandardsLoader:
    """
    Load domain standards into Knowledge Graph

    Supports:
    - ISO standards (iso-22301, iso-27001, etc.)
    - BCI Good Practice Guidelines
    - WHO Framework
    - NIST frameworks
    """

    def __init__(
        self,
        data_path: Optional[Path] = None,
        cache_enabled: bool = True
    ):
        if data_path is None:
            # Default: project root /data/
            project_root = Path(__file__).parents[3]
            data_path = project_root / "data"

        self.data_path = Path(data_path)
        self.standards_path = self.data_path / "knowledge" / "standards"
        self.cache_path = self.data_path / "cache" / "parsed"
        self.cache_enabled = cache_enabled

        # Ensure paths exist
        self.cache_path.mkdir(parents=True, exist_ok=True)

    async def load_iso_standard(
        self,
        standard: str,
        version: str = "latest"
    ) -> Dict[str, Any]:
        """
        Load ISO standard with all associated data

        Args:
            standard: Standard ID (e.g., "iso-22301")
            version: Version year (e.g., "2019") or "latest"

        Returns:
            Dict with clauses, guides, mappings, metadata

        Example:
            >>> loader = StandardsLoader()
            >>> data = await loader.load_iso_standard("iso-22301")
            >>> print(data['metadata']['title'])
            'Business Continuity Management Systems'
        """

        standard_path = self.standards_path / "iso" / standard

        if not standard_path.exists():
            raise FileNotFoundError(f"Standard not found: {standard_path}")

        # Check cache
        if self.cache_enabled:
            cache_key = self._get_cache_key(standard_path)
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info(f"✅ Loaded {standard} from cache")
                return cached

        logger.info(f"📖 Loading {standard} from source files...")

        # Load metadata
        metadata = await self._load_metadata(standard_path)

        # Load clauses
        clauses = await self._parse_clauses(standard_path)

        # Load guides
        guides = await self._load_guides(standard_path)

        # Load mappings
        mappings = await self._load_mappings(standard_path)

        data = {
            "standard": standard,
            "version": version if version != "latest" else metadata.get("version", "unknown"),
            "metadata": metadata,
            "clauses": clauses,
            "guides": guides,
            "mappings": mappings,
            "loaded_at": datetime.utcnow().isoformat()
        }

        # Save to cache
        if self.cache_enabled:
            await self._save_to_cache(cache_key, data)

        logger.info(f"✅ Loaded {standard} successfully")

        return data

    async def load_bci_gpg(self, version: str = "2018") -> Dict[str, Any]:
        """Load BCI Good Practice Guidelines"""

        bci_path = self.standards_path / "bci" / f"gpg-{version}"

        if not bci_path.exists():
            raise FileNotFoundError(f"BCI GPG not found: {bci_path}")

        # Similar logic to ISO loading
        metadata = await self._load_metadata(bci_path)

        return {
            "framework": "bci-gpg",
            "version": version,
            "metadata": metadata,
            "loaded_at": datetime.utcnow().isoformat()
        }

    async def load_who_framework(self) -> Dict[str, Any]:
        """Load WHO Framework"""

        who_path = self.standards_path / "who"

        if not who_path.exists():
            raise FileNotFoundError(f"WHO Framework not found: {who_path}")

        metadata = await self._load_metadata(who_path)

        return {
            "framework": "who",
            "metadata": metadata,
            "loaded_at": datetime.utcnow().isoformat()
        }

    # ========== Helper Methods ==========

    async def _load_metadata(self, path: Path) -> Dict[str, Any]:
        """Load metadata.json from standard directory"""

        metadata_file = path / "metadata.json"

        if not metadata_file.exists():
            logger.warning(f"No metadata.json found in {path}")
            return {}

        return json.loads(metadata_file.read_text())

    async def _parse_clauses(self, standard_path: Path) -> List[Dict[str, Any]]:
        """Parse clauses from standards/ subdirectory"""

        clauses_dir = standard_path / "standards"

        if not clauses_dir.exists():
            logger.warning(f"No clauses directory found: {clauses_dir}")
            return []

        clauses = []

        # Look for clauses_breakdown.md
        clauses_file = clauses_dir / "clauses_breakdown.md"
        if clauses_file.exists():
            # Parse markdown file
            content = clauses_file.read_text()
            # TODO: Implement proper markdown parsing
            clauses.append({
                "source": "clauses_breakdown.md",
                "content": content[:1000]  # First 1000 chars as preview
            })

        return clauses

    async def _load_guides(self, standard_path: Path) -> List[Dict[str, Any]]:
        """Load implementation guides (PDFs)"""

        guides = []

        # Find all PDF files
        for pdf_file in standard_path.glob("*.pdf"):
            guides.append({
                "name": pdf_file.stem,
                "file": pdf_file.name,
                "size_mb": round(pdf_file.stat().st_size / 1024 / 1024, 2),
                "path": str(pdf_file)
            })

        return guides

    async def _load_mappings(self, standard_path: Path) -> Dict[str, Any]:
        """Load mapping files (e.g., iso_bci_platform_mapping.md)"""

        mappings = {}

        for mapping_file in standard_path.glob("*mapping*.md"):
            mappings[mapping_file.stem] = mapping_file.read_text()

        return mappings

    def _get_cache_key(self, path: Path) -> str:
        """Generate MD5 hash of all files for cache key"""

        hasher = hashlib.md5()

        # Hash all files in directory
        for file_path in sorted(path.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith('.'):
                hasher.update(file_path.name.encode())
                hasher.update(str(file_path.stat().st_mtime).encode())

        return hasher.hexdigest()

    async def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Retrieve from file cache"""

        cache_file = self.cache_path / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            return json.loads(cache_file.read_text())
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    async def _save_to_cache(self, cache_key: str, data: Dict):
        """Save to file cache"""

        cache_file = self.cache_path / f"{cache_key}.json"

        try:
            cache_file.write_text(json.dumps(data, indent=2, default=str))
            logger.debug(f"Cached to {cache_file}")
        except Exception as e:
            logger.error(f"Cache save error: {e}")

    # ========== Batch Operations ==========

    async def load_all_iso_standards(self) -> Dict[str, Dict]:
        """Load all available ISO standards"""

        iso_path = self.standards_path / "iso"

        if not iso_path.exists():
            return {}

        standards = {}

        for standard_dir in iso_path.iterdir():
            if standard_dir.is_dir():
                standard_name = standard_dir.name
                try:
                    standards[standard_name] = await self.load_iso_standard(standard_name)
                except Exception as e:
                    logger.error(f"Failed to load {standard_name}: {e}")

        return standards

    async def list_available_standards(self) -> Dict[str, List[str]]:
        """List all available standards by domain"""

        available = {}

        for domain_dir in self.standards_path.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                standards = [d.name for d in domain_dir.iterdir() if d.is_dir()]
                available[domain] = standards

        return available
