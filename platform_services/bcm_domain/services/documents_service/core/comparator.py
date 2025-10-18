"""
Document Comparison Service
Compare document versions and detect changes

Features:
- Text similarity calculation
- Line-by-line diff
- Structural change detection
- Metadata comparison

Based on:
- BCM_1/document-processor/services/comparator.py (lines 45-187)
"""

import difflib
import re
from typing import Dict, List, Any, Optional, Tuple


class DocumentComparator:
    """
    Compare documents to detect changes between versions.

    Capabilities:
    - Calculate similarity scores
    - Generate line-by-line diffs
    - Detect structural changes
    - Compare metadata
    """

    def compare(
        self,
        source_text: str,
        target_text: str,
        source_metadata: Optional[Dict[str, Any]] = None,
        target_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive document comparison.

        Args:
            source_text: Original document text
            target_text: Modified document text
            source_metadata: Original document metadata
            target_metadata: Modified document metadata

        Returns:
            Comparison results dictionary
        """
        results = {}

        # Calculate similarity
        results['similarity_score'] = self._calculate_similarity(source_text, target_text)

        # Calculate text changes
        text_changes = self._calculate_text_changes(source_text, target_text)
        results['text_added'] = text_changes['added']
        results['text_removed'] = text_changes['removed']
        results['text_modified'] = text_changes['modified']

        # Generate diff
        results['diff'] = self._generate_diff(source_text, target_text)

        # Detect structural changes
        results['structural_changes'] = self._detect_structural_changes(source_text, target_text)

        # Compare metadata if provided
        if source_metadata and target_metadata:
            results['metadata_changes'] = self._compare_metadata(source_metadata, target_metadata)

        # Generate human-readable summary
        results['changes_summary'] = self._generate_summary(results)

        return results

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score using SequenceMatcher.

        Based on: BCM_1/document-processor/services/comparator.py lines 68-84

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        if not text1 and not text2:
            return 1.0

        if not text1 or not text2:
            return 0.0

        # Use difflib SequenceMatcher
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()

    def _calculate_text_changes(
        self,
        source_text: str,
        target_text: str
    ) -> Dict[str, int]:
        """
        Calculate character-level changes.

        Args:
            source_text: Original text
            target_text: Modified text

        Returns:
            Dictionary with added, removed, modified counts
        """
        # Use difflib opcodes
        matcher = difflib.SequenceMatcher(None, source_text, target_text)

        added = 0
        removed = 0
        modified = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Characters were changed
                removed += i2 - i1
                added += j2 - j1
                modified += min(i2 - i1, j2 - j1)
            elif tag == 'delete':
                # Characters were removed
                removed += i2 - i1
            elif tag == 'insert':
                # Characters were added
                added += j2 - j1

        return {
            'added': added,
            'removed': removed,
            'modified': modified,
        }

    def _generate_diff(
        self,
        source_text: str,
        target_text: str,
        context_lines: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate line-by-line diff.

        Based on: BCM_1/document-processor/services/comparator.py lines 86-125

        Args:
            source_text: Original text
            target_text: Modified text
            context_lines: Number of context lines around changes

        Returns:
            List of diff operations
        """
        # Split into lines
        source_lines = source_text.splitlines(keepends=True)
        target_lines = target_text.splitlines(keepends=True)

        # Generate unified diff
        diff = list(difflib.unified_diff(
            source_lines,
            target_lines,
            lineterm='',
            n=context_lines
        ))

        # Parse diff into structured format
        changes = []
        line_num = 0

        for line in diff:
            if line.startswith('@@'):
                # Parse hunk header
                match = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
                if match:
                    line_num = int(match.group(3))
                continue

            if line.startswith('---') or line.startswith('+++'):
                # Skip file headers
                continue

            # Determine operation
            if line.startswith('+'):
                changes.append({
                    'operation': 'add',
                    'line_number': line_num,
                    'text': line[1:],
                })
                line_num += 1
            elif line.startswith('-'):
                changes.append({
                    'operation': 'remove',
                    'line_number': line_num,
                    'text': line[1:],
                })
            elif line.startswith(' '):
                # Context line (unchanged)
                changes.append({
                    'operation': 'context',
                    'line_number': line_num,
                    'text': line[1:],
                })
                line_num += 1

        return changes

    def _detect_structural_changes(
        self,
        source_text: str,
        target_text: str
    ) -> Dict[str, Any]:
        """
        Detect structural changes (sections, headings).

        Args:
            source_text: Original text
            target_text: Modified text

        Returns:
            Dictionary with structural changes
        """
        # Extract sections from both texts
        source_sections = self._extract_sections(source_text)
        target_sections = self._extract_sections(target_text)

        # Compare section titles
        source_titles = set(s['title'] for s in source_sections)
        target_titles = set(s['title'] for s in target_sections)

        added_sections = sorted(list(target_titles - source_titles))
        removed_sections = sorted(list(source_titles - target_titles))
        common_sections = sorted(list(source_titles & target_titles))

        # Check for modified sections
        modified_sections = []
        for title in common_sections:
            source_section = next(s for s in source_sections if s['title'] == title)
            target_section = next(s for s in target_sections if s['title'] == title)

            # Compare content
            if source_section['content'] != target_section['content']:
                similarity = self._calculate_similarity(
                    source_section['content'],
                    target_section['content']
                )
                modified_sections.append({
                    'title': title,
                    'similarity': similarity,
                })

        return {
            'sections_added': added_sections,
            'sections_removed': removed_sections,
            'sections_modified': modified_sections,
            'total_sections_before': len(source_sections),
            'total_sections_after': len(target_sections),
        }

    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Extract sections from text.

        Based on numbered and capitalized headings.

        Args:
            text: Text to extract sections from

        Returns:
            List of section dictionaries
        """
        sections = []
        current_section = None

        lines = text.split('\n')

        # Patterns for section headers
        numbered_pattern = re.compile(r'^(\d+\.)+\s+(.+)$')
        caps_pattern = re.compile(r'^[A-Z][A-Z\s]{10,}$')

        for line in lines:
            line_stripped = line.strip()

            # Check for numbered section
            match = numbered_pattern.match(line_stripped)
            if match:
                if current_section:
                    sections.append(current_section)

                current_section = {
                    'title': line_stripped,
                    'content': '',
                }
                continue

            # Check for ALL CAPS heading
            if caps_pattern.match(line_stripped) and len(line_stripped) < 100:
                if current_section:
                    sections.append(current_section)

                current_section = {
                    'title': line_stripped,
                    'content': '',
                }
                continue

            # Add to current section
            if current_section:
                current_section['content'] += line + '\n'

        # Add final section
        if current_section:
            sections.append(current_section)

        # Clean content
        for section in sections:
            section['content'] = section['content'].strip()

        return sections

    def _compare_metadata(
        self,
        source_metadata: Dict[str, Any],
        target_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare metadata between documents.

        Args:
            source_metadata: Original metadata
            target_metadata: Modified metadata

        Returns:
            Dictionary of metadata changes
        """
        changes = {}

        # All keys from both metadata dicts
        all_keys = set(source_metadata.keys()) | set(target_metadata.keys())

        for key in all_keys:
            source_value = source_metadata.get(key)
            target_value = target_metadata.get(key)

            if source_value != target_value:
                changes[key] = {
                    'old': source_value,
                    'new': target_value,
                }

        return changes

    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """
        Generate human-readable summary of changes.

        Args:
            results: Comparison results

        Returns:
            Summary text
        """
        summary_parts = []

        # Similarity
        similarity = results.get('similarity_score', 0)
        if similarity >= 0.95:
            summary_parts.append(f"Documents are very similar ({similarity:.1%} match)")
        elif similarity >= 0.80:
            summary_parts.append(f"Documents are mostly similar ({similarity:.1%} match)")
        elif similarity >= 0.50:
            summary_parts.append(f"Documents have moderate changes ({similarity:.1%} match)")
        else:
            summary_parts.append(f"Documents are significantly different ({similarity:.1%} match)")

        # Text changes
        added = results.get('text_added', 0)
        removed = results.get('text_removed', 0)
        modified = results.get('text_modified', 0)

        if added > 0 or removed > 0 or modified > 0:
            change_parts = []
            if added > 0:
                change_parts.append(f"{added:,} characters added")
            if removed > 0:
                change_parts.append(f"{removed:,} characters removed")
            if modified > 0:
                change_parts.append(f"{modified:,} characters modified")

            summary_parts.append(", ".join(change_parts))

        # Structural changes
        structural = results.get('structural_changes', {})
        sections_added = len(structural.get('sections_added', []))
        sections_removed = len(structural.get('sections_removed', []))
        sections_modified = len(structural.get('sections_modified', []))

        if sections_added > 0 or sections_removed > 0:
            struct_parts = []
            if sections_added > 0:
                struct_parts.append(f"{sections_added} section(s) added")
            if sections_removed > 0:
                struct_parts.append(f"{sections_removed} section(s) removed")
            if sections_modified > 0:
                struct_parts.append(f"{sections_modified} section(s) modified")

            summary_parts.append(", ".join(struct_parts))

        # Metadata changes
        metadata_changes = results.get('metadata_changes', {})
        if metadata_changes:
            summary_parts.append(f"{len(metadata_changes)} metadata field(s) changed")

        return ". ".join(summary_parts) + "."


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def quick_similarity(text1: str, text2: str) -> float:
    """
    Quick similarity check for large texts.

    Uses sampling for performance.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    # For large texts, sample first 10k and last 10k characters
    if len(text1) > 20000 or len(text2) > 20000:
        sample1 = text1[:10000] + text1[-10000:]
        sample2 = text2[:10000] + text2[-10000:]
    else:
        sample1 = text1
        sample2 = text2

    matcher = difflib.SequenceMatcher(None, sample1, sample2)
    return matcher.ratio()
