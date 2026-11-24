from typing import Dict, Any

class RankingService:
    """Multi-dimensional ranking engine for company intelligence signals.
    
    Weights:
    - Relevance to Company: 30%
    - Business Impact: 25%
    - Urgency: 20%
    - Source Credibility: 10%
    - Recency: 10%
    - Novelty: 5%
    """

    def calculate_scores(self, signal: Dict[str, Any], company_profile: Dict[str, Any], source_tier: str = "High") -> Dict[str, Any]:
        title = signal.get("title", "").lower()
        evidence = signal.get("evidence_snippet", "").lower()
        category = signal.get("category", "market").lower()

        # Base credibility from source
        credibility_map = {"High": 92.0, "Medium": 75.0, "Standard": 60.0}
        credibility_score = credibility_map.get(source_tier, 70.0)

        # Relevance scoring based on company keywords & category
        rel_boost = 0.0
        company_name = company_profile.get("name", "").lower()
        industry_words = [w.lower() for w in company_profile.get("industry", "").split()]
        if company_name in title or company_name in evidence:
            rel_boost += 25.0
        for w in industry_words:
            if len(w) > 4 and (w in title or w in evidence):
                rel_boost += 8.0

        base_relevance = 65.0 + min(rel_boost, 30.0)
        relevance_score = min(98.0, base_relevance)

        # Impact scoring
        high_impact_words = ["ban", "cap", "acquisition", "funding", "lawsuit", "zero-fee", "mandate", "surge", "collapse", "merger"]
        imp_hits = sum(1 for w in high_impact_words if w in title or w in evidence)
        impact_score = min(98.0, 60.0 + (imp_hits * 12.0))

        # Urgency scoring
        urgency_words = ["immediate", "deadline", "effective", "this week", "urgent", "breaking", "halt", "enacted"]
        urg_hits = sum(1 for w in urgency_words if w in title or w in evidence)
        urgency_score = min(95.0, 55.0 + (urg_hits * 15.0))

        # Recency and Novelty
        recency_score = 90.0
        novelty_score = 80.0

        # Composite Rank
        composite_rank = round(
            (relevance_score * 0.30) +
            (impact_score * 0.25) +
            (urgency_score * 0.20) +
            (credibility_score * 0.10) +
            (recency_score * 0.10) +
            (novelty_score * 0.05),
            1
        )

        # Explanation
        if composite_rank >= 80:
            rank_explanation = f"Critical priority ({composite_rank}/100): High business impact and direct relevance to core revenue channels."
        elif composite_rank >= 65:
            rank_explanation = f"Elevated priority ({composite_rank}/100): Notable competitor movement or regulatory shift requiring monitoring."
        else:
            rank_explanation = f"Standard priority ({composite_rank}/100): General contextual development."

        return {
            "relevance_score": relevance_score,
            "impact_score": impact_score,
            "urgency_score": urgency_score,
            "credibility_score": credibility_score,
            "recency_score": recency_score,
            "novelty_score": novelty_score,
            "composite_rank": composite_rank,
            "rank_explanation": rank_explanation
        }

ranking_service = RankingService()
