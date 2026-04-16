"""xlab (Yasuaki Kakehi Laboratory) に特化した学会・ジャーナル情報。

東京大学大学院学際情報学府 筧康明研究室
研究テーマ: Material Experience Design
- shape-changing interfaces, soft sensors, physical computing
- fabrication (3D printing, laser cutting, inflatable)
- interactive art, kinetic installations
- pneumatic/hydraulic systems, biosignals
- tangible interaction, HCI
"""

from __future__ import annotations

# xlabの研究に関連するキーワード群（OpenAlex検索の補助に使用）
XLAB_KEYWORDS: list[str] = [
    "shape-changing interface",
    "soft sensor fabrication",
    "tangible interaction 3D printing",
    "interactive art installation",
    "pneumatic inflatable interface",
    "capacitive sensing touch surface",
    "material interaction design",
    "kinetic sculpture computational",
]

# xlabの研究にフィットする学会・ジャーナルのキュレーションリスト
# OpenAlexの検索結果にこれらが含まれていたらスコアをブーストする
XLAB_VENUES: list[dict] = [
    # === HCI / Interaction Design ===
    {
        "name": "CHI Conference on Human Factors in Computing Systems",
        "short": "CHI",
        "patterns": ["chi conference", "human factors in computing"],
        "category": "HCI",
        "tier": "top",
        "note": "HCI最高峰。Tangible / Fabrication / Interaction Design 全般",
        "deadline_month": 9,
        "conf_month": 4,
    },
    {
        "name": "ACM Symposium on User Interface Software and Technology",
        "short": "UIST",
        "patterns": ["user interface software and technology", "uist"],
        "category": "HCI",
        "tier": "top",
        "note": "UIシステム・新しいインタラクション技術。xlabの中核",
        "deadline_month": 4,
        "conf_month": 10,
    },
    {
        "name": "ACM International Conference on Tangible, Embedded, and Embodied Interaction",
        "short": "TEI",
        "patterns": ["tangible, embedded", "tangible and embedded", "tangible embedded embodied"],
        "category": "HCI",
        "tier": "top",
        "note": "タンジブルインタラクション特化。xlabの研究に最もフィット",
        "deadline_month": 8,
        "conf_month": 2,
    },
    {
        "name": "ACM Designing Interactive Systems Conference",
        "short": "DIS",
        "patterns": ["designing interactive systems"],
        "category": "HCI / Design",
        "tier": "top",
        "note": "インタラクションデザイン。素材・体験デザイン系",
        "deadline_month": 1,
        "conf_month": 6,
    },
    {
        "name": "ACM International Conference on Interactive Surfaces and Spaces",
        "short": "ISS",
        "patterns": ["interactive surfaces and spaces", "interactive tabletops and surfaces"],
        "category": "HCI",
        "tier": "A",
        "note": "インタラクティブサーフェス。タッチ・形状変化系",
        "deadline_month": 6,
        "conf_month": 11,
    },
    {
        "name": "ACM International Conference on Multimodal Interaction",
        "short": "ICMI",
        "patterns": ["multimodal interaction"],
        "category": "HCI",
        "tier": "A",
        "note": "マルチモーダルインタラクション",
        "deadline_month": 5,
        "conf_month": 11,
    },
    {
        "name": "ACM Augmented Human International Conference",
        "short": "AH",
        "patterns": ["augmented human"],
        "category": "HCI",
        "tier": "B",
        "note": "人間拡張技術",
        "deadline_month": None,
        "conf_month": None,
    },
    # === Graphics / Fabrication ===
    {
        "name": "SIGGRAPH",
        "short": "SIGGRAPH",
        "patterns": ["siggraph"],
        "category": "Graphics / Fabrication",
        "tier": "top",
        "note": "CG・ファブリケーション最高峰。Emerging Technologies も注目",
        "deadline_month": 2,
        "conf_month": 8,
        "exclude_patterns": ["asia"],
    },
    {
        "name": "SIGGRAPH Asia",
        "short": "SIGGRAPH Asia",
        "patterns": ["siggraph asia"],
        "category": "Graphics / Fabrication",
        "tier": "top",
        "note": "SIGGRAPH のアジア版。E-Tech で展示も可能",
        "deadline_month": 6,
        "conf_month": 12,
    },
    {
        "name": "ACM Symposium on Computational Fabrication",
        "short": "SCF",
        "patterns": ["computational fabrication"],
        "category": "Fabrication",
        "tier": "A",
        "note": "コンピュテーショナルファブリケーション特化",
        "deadline_month": 8,
        "conf_month": 10,
    },
    # === Art / Media Art ===
    {
        "name": "Ars Electronica Festival",
        "short": "Ars Electronica",
        "patterns": ["ars electronica"],
        "category": "Art / Media Art",
        "tier": "top",
        "note": "メディアアートの世界的フェスティバル。展示・論文両方",
        "deadline_month": 3,
        "conf_month": 9,
    },
    {
        "name": "ISEA International Symposium on Electronic Arts",
        "short": "ISEA",
        "patterns": ["electronic arts", "isea international", "isea symposium"],
        "category": "Art / Media Art",
        "tier": "A",
        "note": "電子アート国際シンポジウム",
        "deadline_month": 10,
        "conf_month": 5,
    },
    {
        "name": "NIME International Conference on New Interfaces for Musical Expression",
        "short": "NIME",
        "patterns": ["new interfaces for musical expression", "nime"],
        "category": "Art / Music",
        "tier": "A",
        "note": "音楽×テクノロジー。サウンドインスタレーション系",
        "deadline_month": 1,
        "conf_month": 6,
    },
    # === Robotics / Soft Robotics ===
    {
        "name": "IEEE International Conference on Soft Robotics",
        "short": "RoboSoft",
        "patterns": ["robosoft", "conference on soft robotics"],
        "category": "Robotics",
        "tier": "A",
        "note": "ソフトロボティクス。ソフトセンサー・アクチュエータ系",
        "deadline_month": 10,
        "conf_month": 4,
    },
    {
        "name": "IEEE International Conference on Robotics and Automation",
        "short": "ICRA",
        "patterns": ["robotics and automation"],
        "category": "Robotics",
        "tier": "top",
        "note": "ロボティクス最高峰。ソフトロボティクス・ファブリケーション",
        "deadline_month": 9,
        "conf_month": 5,
    },
    # === VR / Mixed Reality ===
    {
        "name": "IEEE Conference on Virtual Reality and 3D User Interfaces",
        "short": "IEEE VR",
        "patterns": ["virtual reality and 3d user interfaces"],
        "category": "VR / MR",
        "tier": "top",
        "note": "VR/MR最高峰。触覚・物理インタフェース系",
        "deadline_month": 9,
        "conf_month": 3,
    },
    # === 国内学会 ===
    {
        "name": "日本バーチャルリアリティ学会大会",
        "short": "日本VR学会",
        "patterns": ["virtual reality society of japan", "日本バーチャルリアリティ"],
        "category": "国内",
        "tier": "国内主要",
        "note": "国内VR・インタラクション研究の主要学会",
        "deadline_month": 6,
        "conf_month": 9,
    },
    {
        "name": "インタラクション",
        "short": "インタラクション",
        "patterns": ["インタラクション", "interaction ipsj"],
        "category": "国内",
        "tier": "国内主要",
        "note": "情報処理学会インタラクション研究会",
        "deadline_month": 11,
        "conf_month": 3,
    },
    # === Journals ===
    {
        "name": "ACM Transactions on Computer-Human Interaction",
        "short": "TOCHI",
        "patterns": ["transactions on computer-human interaction"],
        "category": "Journal (HCI)",
        "tier": "top",
        "note": "HCI最高峰ジャーナル",
        "deadline_month": None,
        "conf_month": None,
    },
    {
        "name": "ACM Transactions on Graphics",
        "short": "TOG",
        "patterns": ["transactions on graphics"],
        "category": "Journal (Graphics)",
        "tier": "top",
        "note": "CG最高峰ジャーナル。SIGGRAPH論文が掲載",
        "deadline_month": None,
        "conf_month": None,
    },
    {
        "name": "International Journal of Human-Computer Studies",
        "short": "IJHCS",
        "patterns": ["human-computer studies", "human computer studies"],
        "category": "Journal (HCI)",
        "tier": "A",
        "note": "HCI系ジャーナル",
        "deadline_month": None,
        "conf_month": None,
    },
    {
        "name": "Personal and Ubiquitous Computing",
        "short": "PUC",
        "patterns": ["personal and ubiquitous computing"],
        "category": "Journal (HCI)",
        "tier": "A",
        "note": "ユビキタスコンピューティング",
        "deadline_month": None,
        "conf_month": None,
    },
    {
        "name": "IEEE Transactions on Haptics",
        "short": "ToH",
        "patterns": ["transactions on haptics"],
        "category": "Journal (Haptics)",
        "tier": "A",
        "note": "触覚技術ジャーナル",
        "deadline_month": None,
        "conf_month": None,
    },
    {
        "name": "Advanced Intelligent Systems",
        "short": "AIS",
        "patterns": ["advanced intelligent systems"],
        "category": "Journal (Materials)",
        "tier": "A",
        "note": "スマートマテリアル・インテリジェントシステム",
        "deadline_month": None,
        "conf_month": None,
    },
    {
        "name": "Soft Robotics",
        "short": "SoRo",
        "patterns": ["soft robotics"],
        "category": "Journal (Robotics)",
        "tier": "A",
        "note": "ソフトロボティクス専門ジャーナル",
        "deadline_month": None,
        "conf_month": None,
    },
]


def match_xlab_venue(source_name: str) -> dict | None:
    """OpenAlexのsource名がxlabの学会リストにマッチするか判定。"""
    name_lower = source_name.lower()

    # まず除外パターンがあるものを先にチェック（SIGGRAPH vs SIGGRAPH Asia）
    # より具体的なパターン（longer match）を先に
    sorted_venues = sorted(
        XLAB_VENUES,
        key=lambda v: max(len(p) for p in v["patterns"]),
        reverse=True,
    )

    for venue in sorted_venues:
        exclude = venue.get("exclude_patterns", [])
        for pattern in venue["patterns"]:
            if pattern.lower() in name_lower:
                # 除外パターンチェック
                if any(ep.lower() in name_lower for ep in exclude):
                    continue
                return venue
    return None
