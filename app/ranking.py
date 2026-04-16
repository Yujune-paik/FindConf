from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class SamplePaper:
    title: str
    publication_year: int | None
    cited_by_count: int
    doi: str | None


@dataclass
class VenueResult:
    source_id: str | None
    name: str
    venue_type: str | None
    is_oa: bool | None
    frequency: int = 0
    total_cited_by: int = 0
    sample_papers: list[SamplePaper] = field(default_factory=list)
    score: float = 0.0

    @property
    def avg_cited_by(self) -> float:
        return self.total_cited_by / self.frequency if self.frequency else 0.0

    # xlab用の追加フィールド
    xlab_match: dict | None = None

    def to_dict(self) -> dict:
        d = {
            "source_id": self.source_id,
            "name": self.name,
            "type": self.venue_type,
            "is_oa": self.is_oa,
            "frequency": self.frequency,
            "total_cited_by": self.total_cited_by,
            "avg_cited_by": round(self.avg_cited_by, 1),
            "score": round(self.score, 3),
            "sample_papers": [
                {
                    "title": p.title,
                    "publication_year": p.publication_year,
                    "cited_by_count": p.cited_by_count,
                    "doi": p.doi,
                }
                for p in self.sample_papers
            ],
        }
        if self.xlab_match:
            d["xlab"] = {
                "short": self.xlab_match["short"],
                "category": self.xlab_match["category"],
                "tier": self.xlab_match["tier"],
                "note": self.xlab_match["note"],
                "deadline_month": self.xlab_match.get("deadline_month"),
                "conf_month": self.xlab_match.get("conf_month"),
            }
        return d


def _extract_source_key(work: dict) -> tuple[str | None, dict | None]:
    """Extract a grouping key and source metadata from a work."""
    loc = work.get("primary_location") or {}
    source = loc.get("source")
    if not source:
        return None, None
    source_id = source.get("id")
    name = source.get("display_name")
    if not name:
        return None, None
    key = source_id or name.lower().strip()
    return key, source


def rank_venues(works: list[dict], top_n: int = 30) -> list[dict]:
    """Aggregate venues from similar works and rank them."""
    venues: dict[str, VenueResult] = {}

    for work in works:
        key, source = _extract_source_key(work)
        if key is None or source is None:
            continue

        source_type = source.get("type")
        if source_type == "repository":
            continue

        if key not in venues:
            venues[key] = VenueResult(
                source_id=source.get("id"),
                name=source.get("display_name", ""),
                venue_type=source_type,
                is_oa=source.get("is_oa"),
            )

        v = venues[key]
        v.frequency += 1
        v.total_cited_by += work.get("cited_by_count", 0) or 0

        if len(v.sample_papers) < 3:
            v.sample_papers.append(
                SamplePaper(
                    title=work.get("title", ""),
                    publication_year=work.get("publication_year"),
                    cited_by_count=work.get("cited_by_count", 0) or 0,
                    doi=work.get("doi"),
                )
            )

    venue_list = list(venues.values())

    if not venue_list:
        return []

    # Compute scores
    max_freq = max(v.frequency for v in venue_list)
    max_avg = max(v.avg_cited_by for v in venue_list) if venue_list else 1.0

    for v in venue_list:
        norm_freq = v.frequency / max_freq if max_freq > 0 else 0
        norm_cite = (
            math.log(1 + v.avg_cited_by) / math.log(1 + max_avg)
            if max_avg > 0
            else 0
        )
        v.score = 0.6 * norm_freq + 0.4 * norm_cite

    venue_list.sort(key=lambda v: v.score, reverse=True)
    return [v.to_dict() for v in venue_list[:top_n]]


def rank_venues_xlab(works: list[dict], top_n: int = 30) -> list[dict]:
    """xlabに特化したランキング。xlab学会リストとのマッチングとブーストを行う。"""
    from app.xlab import match_xlab_venue, XLAB_VENUES

    venues: dict[str, VenueResult] = {}

    for work in works:
        key, source = _extract_source_key(work)
        if key is None or source is None:
            continue

        source_type = source.get("type")
        if source_type == "repository":
            continue

        if key not in venues:
            v = VenueResult(
                source_id=source.get("id"),
                name=source.get("display_name", ""),
                venue_type=source_type,
                is_oa=source.get("is_oa"),
            )
            # xlabの学会リストとマッチング
            v.xlab_match = match_xlab_venue(v.name)
            venues[key] = v

        v = venues[key]
        v.frequency += 1
        v.total_cited_by += work.get("cited_by_count", 0) or 0

        if len(v.sample_papers) < 3:
            v.sample_papers.append(
                SamplePaper(
                    title=work.get("title", ""),
                    publication_year=work.get("publication_year"),
                    cited_by_count=work.get("cited_by_count", 0) or 0,
                    doi=work.get("doi"),
                )
            )

    venue_list = list(venues.values())

    if not venue_list:
        return []

    # Compute scores with xlab boost
    max_freq = max(v.frequency for v in venue_list)
    max_avg = max(v.avg_cited_by for v in venue_list) if venue_list else 1.0

    for v in venue_list:
        norm_freq = v.frequency / max_freq if max_freq > 0 else 0
        norm_cite = (
            math.log(1 + v.avg_cited_by) / math.log(1 + max_avg)
            if max_avg > 0
            else 0
        )

        # xlabブースト: マッチした学会はtierに応じてスコア加算
        xlab_boost = 0.0
        if v.xlab_match:
            tier = v.xlab_match["tier"]
            if tier == "top":
                xlab_boost = 0.4
            elif tier == "A":
                xlab_boost = 0.25
            elif tier in ("B", "国内主要"):
                xlab_boost = 0.15

        v.score = 0.4 * norm_freq + 0.3 * norm_cite + 0.3 * xlab_boost

    # xlabマッチしたものを優先表示
    venue_list.sort(key=lambda v: (v.xlab_match is not None, v.score), reverse=True)
    return [v.to_dict() for v in venue_list[:top_n]]
