"""
 Standards Monitor - Auto-update Standards from External Sources

Monitors external sources for updates to standards:
- ISO RSS feeds
- BCI website updates
- WHO framework changes
- NIST publications
- Regulatory changes (GDPR, HIPAA, SOX)

Architecture:
- Scheduled checks via Temporal workflows
- Event notifications via EventBus
- Automatic re-indexing after updates
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging
import asyncio
import hashlib

import aiohttp
import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# ============================================================================
# SOURCE MONITORS
# ============================================================================

class ISOMonitor:
    """Monitor ISO standard updates via RSS/API"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: ISO monitor configuration
        """
        self.config = config
        self.rss_url = config.get("rss_url", "https://www.iso.org/rss")
        self.check_interval = config.get("check_interval_hours", 24)

    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check ISO RSS feed for standard updates

        Returns:
            List of updated standards with metadata
        """
        updates = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.rss_url, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"ISO RSS feed returned {response.status}")
                        return updates

                    content = await response.text()

            # Parse RSS feed
            feed = await asyncio.to_thread(feedparser.parse, content)

            for entry in feed.entries[:10]:  # Check latest 10 entries
                # Check if it's a BCM-related standard
                if self._is_bcm_related(entry):
                    update = {
                        "source": "iso",
                        "standard": self._extract_standard_id(entry.title),
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.published,
                        "summary": entry.get("summary", ""),
                        "detected_at": datetime.utcnow().isoformat()
                    }
                    updates.append(update)

            logger.info(f"ISO Monitor: Found {len(updates)} potential updates")

        except Exception as e:
            logger.error(f"ISO Monitor failed: {e}", exc_info=True)

        return updates

    def _is_bcm_related(self, entry) -> bool:
        """Check if RSS entry is BCM-related"""
        bcm_keywords = [
            "22301", "27001", "31000",  # Standard numbers
            "business continuity", "risk management",
            "information security", "resilience"
        ]

        text = f"{entry.title} {entry.get('summary', '')}".lower()

        return any(keyword in text for keyword in bcm_keywords)

    def _extract_standard_id(self, title: str) -> Optional[str]:
        """Extract standard ID from title (e.g., 'ISO 22301:2019')"""
        import re

        # Pattern: ISO XXXXX:YYYY
        match = re.search(r'ISO\s+(\d+):(\d{4})', title, re.IGNORECASE)
        if match:
            return f"iso-{match.group(1)}"

        return None


class BCIMonitor:
    """Monitor BCI Good Practice Guidelines updates"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.url = config.get("url", "https://www.thebci.org/knowledge/good-practice-guidelines.html")
        self.check_interval = config.get("check_interval_hours", 168)  # Weekly

    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check BCI website for GPG updates"""
        updates = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"BCI website returned {response.status}")
                        return updates

                    html = await response.text()

            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')

            # Look for "Updated" or "New" indicators
            # This is a simplified example - actual implementation depends on BCI website structure
            for link in soup.find_all('a', href=True):
                if 'gpg' in link['href'].lower() or 'good-practice' in link['href'].lower():
                    # Check if there's a date or "updated" mention
                    parent_text = link.parent.get_text() if link.parent else ""

                    if any(keyword in parent_text.lower() for keyword in ['updated', 'new', '2024', '2025']):
                        update = {
                            "source": "bci",
                            "title": link.get_text().strip(),
                            "link": link['href'],
                            "detected_at": datetime.utcnow().isoformat(),
                            "context": parent_text[:200]
                        }
                        updates.append(update)

            logger.info(f"BCI Monitor: Found {len(updates)} potential updates")

        except Exception as e:
            logger.error(f"BCI Monitor failed: {e}", exc_info=True)

        return updates


class WHOMonitor:
    """Monitor WHO Emergency Risk Management Framework updates"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.url = config.get("url", "https://www.who.int/emergencies/emergency-risk-management")
        self.check_interval = config.get("check_interval_hours", 168)  # Weekly

    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check WHO website for framework updates"""
        # Similar to BCIMonitor
        # Implementation depends on WHO website structure
        logger.info("WHO Monitor: Checking for updates...")
        return []


class NISTMonitor:
    """Monitor NIST Cybersecurity Framework updates"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rss_url = config.get("rss_url", "https://www.nist.gov/news-events/cybersecurity/rss.xml")
        self.check_interval = config.get("check_interval_hours", 168)  # Weekly

    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check NIST RSS for framework updates"""
        # Similar to ISOMonitor
        logger.info("NIST Monitor: Checking for updates...")
        return []


# ============================================================================
# MAIN STANDARDS MONITOR
# ============================================================================

class StandardsMonitor:
    """
    Main standards monitor coordinating all source monitors

    Scheduled via Temporal workflows or cron
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        event_bus=None,
        vector_indexer=None
    ):
        """
        Args:
            config_path: Path to sources.yaml config
            event_bus: EventBus for notifications
            vector_indexer: VectorIndexer for re-indexing
        """
        # Load config
        if config_path is None:
            config_path = Path(__file__).parents[1] / "config" / "sources.yaml"

        self.config = self._load_config(config_path)
        self.event_bus = event_bus
        self.vector_indexer = vector_indexer

        # Initialize source monitors
        self.monitors = {
            "iso": ISOMonitor(self.config.get("iso", {})),
            "bci": BCIMonitor(self.config.get("bci", {})),
            "who": WHOMonitor(self.config.get("who", {})),
            "nist": NISTMonitor(self.config.get("nist", {}))
        }

        # State tracking
        self.data_path = Path(__file__).parents[3] / "data"
        self.updates_log_path = self.data_path / "external" / "updates_log.json"
        self.updates_log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("StandardsMonitor initialized")

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load sources.yaml configuration"""
        if not config_path.exists():
            logger.warning(f"Config not found: {config_path}, using defaults")
            return {}

        import yaml
        return yaml.safe_load(config_path.read_text())

    async def run_check_cycle(self) -> Dict[str, Any]:
        """
        Run one check cycle across all sources

        Returns:
            Summary of updates found
        """
        logger.info(" Starting standards update check cycle...")

        all_updates = []
        summary = {
            "checked_at": datetime.utcnow().isoformat(),
            "sources_checked": 0,
            "updates_found": 0,
            "by_source": {}
        }

        # Check each source
        for source_name, monitor in self.monitors.items():
            try:
                logger.info(f"Checking {source_name}...")
                updates = await monitor.check_for_updates()

                all_updates.extend(updates)
                summary["sources_checked"] += 1
                summary["by_source"][source_name] = len(updates)

                logger.info(f" {source_name}: {len(updates)} updates found")

            except Exception as e:
                logger.error(f"Failed to check {source_name}: {e}", exc_info=True)
                summary["by_source"][source_name] = f"error: {e}"

        summary["updates_found"] = len(all_updates)

        # Process updates
        if all_updates:
            await self._process_updates(all_updates)

        # Log results
        await self._log_check_results(summary)

        logger.info(
            f" Check cycle complete: {summary['updates_found']} updates "
            f"from {summary['sources_checked']} sources"
        )

        return summary

    async def _process_updates(self, updates: List[Dict[str, Any]]):
        """
        Process detected updates

        - Filter duplicates
        - Notify via EventBus
        - Download new versions (if configured)
        - Re-index
        """

        # Load previous updates to filter duplicates
        previous_updates = await self._load_previous_updates()

        new_updates = []

        for update in updates:
            # Create update hash
            update_hash = hashlib.md5(
                f"{update['source']}-{update.get('standard', '')}-{update.get('title', '')}".encode()
            ).hexdigest()

            if update_hash not in previous_updates:
                new_updates.append(update)
                previous_updates[update_hash] = {
                    "detected_at": update["detected_at"],
                    "source": update["source"]
                }

        logger.info(f"Filtered to {len(new_updates)} new updates (from {len(updates)} total)")

        # Process each new update
        for update in new_updates:
            await self._process_single_update(update)

        # Save updated log
        await self._save_updates_log(previous_updates)

    async def _process_single_update(self, update: Dict[str, Any]):
        """Process a single update notification"""

        logger.info(f"Processing update: {update['source']} - {update.get('title', 'unknown')}")

        # Publish event
        if self.event_bus:
            try:
                await self.event_bus.publish(
                    topic="knowledge.standard.update_detected",
                    data=update
                )
                logger.info(f"Published update event for {update['source']}")
            except Exception as e:
                logger.error(f"Failed to publish event: {e}")

        # TODO: Automatic download if configured
        # TODO: Re-index if vectorizer available

    async def _load_previous_updates(self) -> Dict[str, Any]:
        """Load previous updates log"""
        if not self.updates_log_path.exists():
            return {}

        import json
        try:
            return json.loads(self.updates_log_path.read_text())
        except Exception as e:
            logger.error(f"Failed to load updates log: {e}")
            return {}

    async def _save_updates_log(self, updates_log: Dict[str, Any]):
        """Save updates log"""
        import json
        try:
            self.updates_log_path.write_text(
                json.dumps(updates_log, indent=2, default=str)
            )
        except Exception as e:
            logger.error(f"Failed to save updates log: {e}")

    async def _log_check_results(self, summary: Dict[str, Any]):
        """Log check results to file"""
        log_file = self.data_path / "external" / "check_history.json"

        import json

        # Load existing history
        history = []
        if log_file.exists():
            try:
                history = json.loads(log_file.read_text())
            except:
                pass

        # Add this check
        history.append(summary)

        # Keep last 100 checks
        history = history[-100:]

        # Save
        try:
            log_file.write_text(json.dumps(history, indent=2, default=str))
        except Exception as e:
            logger.error(f"Failed to save check history: {e}")


# ============================================================================
# SCHEDULER INTEGRATION
# ============================================================================

async def schedule_standards_monitoring(monitor: StandardsMonitor):
    """
    Schedule periodic monitoring

    This would typically be integrated with Temporal workflows,
    but can also run as a simple async loop for development.
    """

    logger.info(" Starting scheduled standards monitoring...")

    # TODO: Integrate with Temporal
    # For now: simple loop

    while True:
        try:
            await monitor.run_check_cycle()
        except Exception as e:
            logger.error(f"Check cycle failed: {e}", exc_info=True)

        # Wait 24 hours
        logger.info("Sleeping for 24 hours until next check...")
        await asyncio.sleep(86400)


# ============================================================================
# CLI FOR TESTING
# ============================================================================

async def main():
    """Test the monitor"""
    monitor = StandardsMonitor()

    # Run one check cycle
    summary = await monitor.run_check_cycle()

    print("\n" + "="*60)
    print("STANDARDS UPDATE CHECK RESULTS")
    print("="*60)
    print(f"Checked at: {summary['checked_at']}")
    print(f"Sources checked: {summary['sources_checked']}")
    print(f"Total updates found: {summary['updates_found']}")
    print("\nBy source:")
    for source, count in summary['by_source'].items():
        print(f"  - {source}: {count}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
