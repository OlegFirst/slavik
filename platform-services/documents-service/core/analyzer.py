"""
Document AI/NLP Analyzer
Advanced analysis using NLP and AI services

Features:
- Named Entity Recognition (spaCy)
- Key phrase extraction (TF-IDF)
- Summarization (OpenAI GPT)
- Sentiment analysis
- Readability metrics

Based on:
- BCM_1/document_processor/document_processor.py (lines 347-510)
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

# NLP Libraries (optional imports)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class DocumentAnalyzer:
    """
    Advanced document analysis using NLP and AI.

    Capabilities:
    - Named Entity Recognition (people, organizations, locations, dates)
    - Key phrase extraction
    - Text summarization
    - Readability metrics
    - Compliance gap analysis
    """

    def __init__(
        self,
        spacy_model: str = "en_core_web_sm",
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize analyzer with NLP models.

        Args:
            spacy_model: spaCy model name to load
            openai_api_key: OpenAI API key for summarization
        """
        # Load spaCy model if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(spacy_model)
            except OSError:
                # Model not found, analysis will be limited
                pass

        # Store OpenAI API key
        self.openai_api_key = openai_api_key
        if openai_api_key and OPENAI_AVAILABLE:
            openai.api_key = openai_api_key

    def analyze(
        self,
        text: str,
        extract_entities: bool = True,
        extract_keywords: bool = True,
        summarize: bool = False,
        analyze_readability: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive document analysis.

        Args:
            text: Document text to analyze
            extract_entities: Extract named entities
            extract_keywords: Extract key phrases
            summarize: Generate AI summary
            analyze_readability: Calculate readability metrics

        Returns:
            Analysis results dictionary
        """
        results = {
            'text_length': len(text),
            'word_count': len(text.split()),
        }

        # Named Entity Recognition
        if extract_entities and self.nlp:
            results['entities'] = self._extract_entities(text)

        # Key phrase extraction
        if extract_keywords:
            results['key_phrases'] = self._extract_keywords(text)

        # Summarization
        if summarize and self.openai_api_key:
            results['summary'] = self._generate_summary(text)

        # Readability metrics
        if analyze_readability:
            results['readability'] = self._calculate_readability(text)

        return results

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using spaCy.

        Based on: BCM_1/document_processor/document_processor.py lines 376-402

        Args:
            text: Text to extract entities from

        Returns:
            Dictionary of entity types to entity lists
        """
        if not self.nlp:
            return {}

        # Limit text length for performance (max 1M characters)
        text = text[:1000000]

        # Process text with spaCy
        doc = self.nlp(text)

        # Extract entities by type
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],  # Geo-political entities (countries, cities)
            'DATE': [],
            'TIME': [],
            'MONEY': [],
            'PERCENT': [],
            'FACILITY': [],
            'PRODUCT': [],
            'EVENT': [],
        }

        for ent in doc.ents:
            if ent.label_ in entities:
                # Deduplicate and clean
                entity_text = ent.text.strip()
                if entity_text and entity_text not in entities[ent.label_]:
                    entities[ent.label_].append(entity_text)

        # Remove empty categories
        entities = {k: v for k, v in entities.items() if v}

        # Limit to top 50 per category
        for category in entities:
            entities[category] = entities[category][:50]

        return entities

    def _extract_keywords(
        self,
        text: str,
        max_keywords: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Extract key phrases using TF-IDF.

        Based on: BCM_1/document_processor/document_processor.py lines 404-428

        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords

        Returns:
            List of keyword dictionaries with text and score
        """
        if not SKLEARN_AVAILABLE:
            # Fallback: simple word frequency
            return self._extract_keywords_simple(text, max_keywords)

        try:
            # Use TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=max_keywords,
                stop_words='english',
                ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
                min_df=1,
                max_df=0.8
            )

            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform([text])

            # Get feature names and scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            # Create keyword list with scores
            keywords = [
                {
                    'text': feature_names[i],
                    'score': float(scores[i]),
                    'type': 'tfidf'
                }
                for i in range(len(feature_names))
                if scores[i] > 0
            ]

            # Sort by score
            keywords.sort(key=lambda x: x['score'], reverse=True)

            return keywords[:max_keywords]

        except Exception:
            # Fallback to simple method
            return self._extract_keywords_simple(text, max_keywords)

    def _extract_keywords_simple(
        self,
        text: str,
        max_keywords: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Simple keyword extraction using word frequency.

        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords

        Returns:
            List of keyword dictionaries
        """
        # Clean text
        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)

        # Split into words
        words = text.split()

        # Remove common stop words
        stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        ])

        words = [w for w in words if w not in stop_words and len(w) > 3]

        # Count frequencies
        word_counts = Counter(words)

        # Create keyword list
        keywords = [
            {
                'text': word,
                'score': count / len(words) if len(words) > 0 else 0,
                'type': 'frequency'
            }
            for word, count in word_counts.most_common(max_keywords)
        ]

        return keywords

    def _generate_summary(
        self,
        text: str,
        max_length: int = 500
    ) -> Optional[str]:
        """
        Generate AI summary using OpenAI GPT.

        Based on: BCM_1/document_processor/document_processor.py lines 430-465

        Args:
            text: Text to summarize
            max_length: Maximum summary length in words

        Returns:
            Generated summary or None if failed
        """
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            return None

        # Truncate text if too long (max 12k characters for GPT-3.5)
        if len(text) > 12000:
            text = text[:12000] + "..."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business continuity expert. Summarize documents clearly and concisely."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize the following document in {max_length} words or less:\n\n{text}"
                    }
                ],
                max_tokens=max_length * 2,  # Rough token estimate
                temperature=0.3,
            )

            summary = response.choices[0].message.content.strip()
            return summary

        except Exception as e:
            # Return None on error (don't fail the whole analysis)
            return None

    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """
        Calculate readability metrics.

        Metrics:
        - Flesch Reading Ease
        - Flesch-Kincaid Grade Level
        - Average sentence length
        - Average word length
        - Complex word percentage

        Args:
            text: Text to analyze

        Returns:
            Dictionary of readability metrics
        """
        # Basic counts
        sentences = self._count_sentences(text)
        words = len(text.split())
        syllables = self._count_syllables(text)

        if sentences == 0 or words == 0:
            return {
                'error': 'Insufficient text for readability analysis'
            }

        # Flesch Reading Ease (0-100, higher = easier)
        # Formula: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
        flesch_reading_ease = 206.835 - (1.015 * words / sentences) - (84.6 * syllables / words)
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))  # Clamp 0-100

        # Flesch-Kincaid Grade Level
        # Formula: 0.39(words/sentences) + 11.8(syllables/words) - 15.59
        flesch_kincaid_grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
        flesch_kincaid_grade = max(0, flesch_kincaid_grade)

        # Average sentence length
        avg_sentence_length = words / sentences

        # Average word length
        total_chars = sum(len(word) for word in text.split())
        avg_word_length = total_chars / words if words > 0 else 0

        # Complex words (3+ syllables)
        complex_word_count = sum(1 for word in text.split() if self._count_word_syllables(word) >= 3)
        complex_word_percent = (complex_word_count / words * 100) if words > 0 else 0

        # Interpretation
        if flesch_reading_ease >= 90:
            difficulty = "Very Easy"
        elif flesch_reading_ease >= 70:
            difficulty = "Easy"
        elif flesch_reading_ease >= 60:
            difficulty = "Fairly Easy"
        elif flesch_reading_ease >= 50:
            difficulty = "Standard"
        elif flesch_reading_ease >= 30:
            difficulty = "Fairly Difficult"
        elif flesch_reading_ease >= 10:
            difficulty = "Difficult"
        else:
            difficulty = "Very Difficult"

        return {
            'flesch_reading_ease': round(flesch_reading_ease, 2),
            'flesch_kincaid_grade': round(flesch_kincaid_grade, 2),
            'difficulty_level': difficulty,
            'average_sentence_length': round(avg_sentence_length, 2),
            'average_word_length': round(avg_word_length, 2),
            'complex_word_percentage': round(complex_word_percent, 2),
            'total_sentences': sentences,
            'total_words': words,
            'total_syllables': syllables,
        }

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        # Simple sentence boundary detection
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)

    def _count_syllables(self, text: str) -> int:
        """Count total syllables in text."""
        words = text.split()
        return sum(self._count_word_syllables(word) for word in words)

    def _count_word_syllables(self, word: str) -> int:
        """
        Count syllables in a word (simplified algorithm).

        Based on: vowel groups count
        """
        word = word.lower().strip()

        # Remove non-alphabetic characters
        word = re.sub(r'[^a-z]', '', word)

        if len(word) == 0:
            return 0

        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1

        # Word must have at least one syllable
        if syllable_count == 0:
            syllable_count = 1

        return syllable_count


# ============================================================================
# COMPLIANCE ANALYSIS
# ============================================================================

def analyze_iso_compliance(
    text: str,
    iso_clauses: List[str]
) -> Dict[str, Any]:
    """
    Analyze ISO 22301 compliance coverage.

    Args:
        text: Document text
        iso_clauses: Mapped ISO clauses from classifier

    Returns:
        Compliance analysis results
    """
    # All ISO 22301 clauses
    all_clauses = [
        '4.1', '4.2', '4.3', '4.4',
        '5.1', '5.2', '5.3',
        '6.1', '6.2', '6.3',
        '7.1', '7.2', '7.3', '7.4', '7.5',
        '8.1', '8.2', '8.3', '8.4', '8.5',
        '9.1', '9.2', '9.3',
        '10.1', '10.2'
    ]

    covered_clauses = set(iso_clauses)
    all_clauses_set = set(all_clauses)

    # Calculate coverage
    coverage_percent = (len(covered_clauses) / len(all_clauses_set)) * 100 if all_clauses_set else 0

    # Identify gaps
    missing_clauses = sorted(all_clauses_set - covered_clauses)

    # Categorize coverage
    if coverage_percent >= 80:
        coverage_level = "Comprehensive"
    elif coverage_percent >= 50:
        coverage_level = "Partial"
    elif coverage_percent >= 25:
        coverage_level = "Limited"
    else:
        coverage_level = "Minimal"

    return {
        'coverage_percent': round(coverage_percent, 2),
        'coverage_level': coverage_level,
        'covered_clauses': sorted(list(covered_clauses)),
        'missing_clauses': missing_clauses,
        'clause_count': len(covered_clauses),
        'total_clauses': len(all_clauses),
    }
