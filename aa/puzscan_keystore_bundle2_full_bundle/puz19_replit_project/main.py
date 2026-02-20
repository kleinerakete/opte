
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import io

import numpy as np
from PIL import Image

app = FastAPI(
    title="Puz19 Analyzer",
    version="1.0.0",
    description=(
        "Demo-Backend für Puz19 Media & Gem Analyzer.\n"
        "Für Replit gedacht: starte mit `uvicorn main:app --reload`."
    ),
)

# ---------- Pydantic Models ----------

class Puz19Component(BaseModel):
    code: str
    name: str
    p19_value: float = Field(..., alias="p19")
    weight: float


class Puz19Internal(BaseModel):
    index: float
    label: str
    components: List[Puz19Component]
    score_internal_artifacts: int


class Puz19External(BaseModel):
    index: float
    label: str
    components: List[Puz19Component]
    score_external_physical: int


class Puz19Total(BaseModel):
    index: float
    label: str
    coherence_score: int


class Puz19Block(BaseModel):
    internal: Puz19Internal
    external: Puz19External
    total: Puz19Total


class DetectedModel(BaseModel):
    model_family: str
    confidence: float


class AIDetection(BaseModel):
    is_ai_generated_prob: float
    is_edited_prob: float
    is_camera_original_prob: float
    detected_models: List[DetectedModel] = []
    manipulation_flags: List[str] = []


class MetadataInfo(BaseModel):
    has_exif: bool
    camera_model: Optional[str] = None
    software: Optional[str] = None
    timestamp: Optional[datetime] = None


class CompressionInfo(BaseModel):
    codec: Optional[str] = None
    macroblocking_level: float
    ringing_level: float


class NoiseProfile(BaseModel):
    type: str
    sensor_like_probability: float
    synthetic_noise_probability: float


class Forensics(BaseModel):
    metadata: MetadataInfo
    compression: CompressionInfo
    noise_profile: NoiseProfile


class Explanation(BaseModel):
    summary: str
    reasons: List[str]
    confidence_level: Literal["low", "medium", "high"]


class DebugInfo(BaseModel):
    available: bool = False


class AnalyzeResult(BaseModel):
    request_id: str
    media_type: Literal["image", "video"]
    puz19: Puz19Block
    ai_detection: AIDetection
    forensics: Forensics
    explanation: Explanation
    debug: DebugInfo


class QuickOptions(BaseModel):
    deep_ai_check: bool = True
    save_to_db: bool = False
    return_debug: bool = False


# ---------- Hilfsfunktionen ----------

def _load_image_to_array(file_bytes: bytes) -> np.ndarray:
    """
    Lädt ein Bild in ein Numpy-Array.
    Falls es kein Bild ist, wird ein HTTP-Error geworfen.
    """
    try:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Datei ist kein gültiges Bild: {e}")
    return np.array(img)


def _dummy_internal_analysis(image: np.ndarray) -> Puz19Internal:
    # Platzhalter – hier würden echte Artefakt-Analysen laufen
    components = [
        Puz19Component(code="A1", name="ISO Noise", p19=1.2, weight=0.25),
        Puz19Component(code="A2", name="Chromatic Noise", p19=1.8, weight=0.25),
        Puz19Component(code="A3", name="Block Noise", p19=5.4, weight=0.35),
        Puz19Component(code="A4", name="Banding", p19=0.9, weight=0.15),
    ]
    index = float(sum(c.p19_value * c.weight for c in components))
    return Puz19Internal(
        index=index,
        label="Internal Sensor-Codec Composite (Demo)",
        components=components,
        score_internal_artifacts=82,
    )


def _dummy_external_analysis(image: np.ndarray) -> Puz19External:
    # Platzhalter – hier würden echte Kanten/Textur/Interferenz-Analysen laufen
    components = [
        Puz19Component(code="B1", name="Edge Stability", p19=4.2, weight=0.20),
        Puz19Component(code="B2", name="Embossed Structure", p19=7.1, weight=0.30),
        Puz19Component(code="C1", name="Spectral Phase Shift", p19=8.4, weight=0.30),
        Puz19Component(code="C2", name="Specular Highlights", p19=2.9, weight=0.10),
        Puz19Component(code="D1", name="Absorption Field", p19=3.3, weight=0.10),
    ]
    index = float(sum(c.p19_value * c.weight for c in components))
    return Puz19External(
        index=index,
        label="External Static Surface Composite (Demo)",
        components=components,
        score_external_physical=91,
    )


def _dummy_puz19_total(internal: Puz19Internal, external: Puz19External) -> Puz19Block:
    total_index = float((internal.index + external.index) / 2.0)
    total = Puz19Total(
        index=total_index,
        label="Composite Internal-External Field (Demo)",
        coherence_score=74,
    )
    return Puz19Block(internal=internal, external=external, total=total)


def _dummy_ai_detection(image: np.ndarray) -> AIDetection:
    # Platzhalter – hier würden echte KI-/Fake-Detection-Modelle laufen
    return AIDetection(
        is_ai_generated_prob=0.3,
        is_edited_prob=0.2,
        is_camera_original_prob=0.7,
        detected_models=[],
        manipulation_flags=[]
    )


def _dummy_forensics() -> Forensics:
    return Forensics(
        metadata=MetadataInfo(
            has_exif=False,
            camera_model=None,
            software=None,
            timestamp=None,
        ),
        compression=CompressionInfo(
            codec="jpeg",
            macroblocking_level=0.5,
            ringing_level=0.2,
        ),
        noise_profile=NoiseProfile(
            type="mixed",
            sensor_like_probability=0.6,
            synthetic_noise_probability=0.4,
        ),
    )


def _dummy_explanation() -> Explanation:
    return Explanation(
        summary="Demo-Auswertung: Puz19-Analyse mit Platzhalterwerten.",
        reasons=[
            "Interne Artefakte wurden mit Demo-Komponenten modelliert.",
            "Externe Strukturindikatoren sind momentan noch statisch.",
            "KI-/Fake-Erkennung ist hier nur symbolisch implementiert."
        ],
        confidence_level="low",
    )


# ---------- Media Analyzer Endpoint ----------

@app.post("/api/v1/analyze", response_model=AnalyzeResult)
async def analyze_media(
    file: UploadFile = File(...),
    media_type: Optional[Literal["image", "video"]] = "image",
    options: Optional[QuickOptions] = None,
):
    """
    Analysiert ein hochgeladenes Medium (derzeit: Bild) mit Puz19-Demo-Logik.
    Gibt ein strukturiertes JSON mit internen/externalen Puz19-Daten zurück.
    """
    file_bytes = await file.read()

    if media_type != "image":
        # Für Demo nur Bilder
        raise HTTPException(status_code=400, detail="Demo-Version unterstützt nur 'image' als media_type.")

    image = _load_image_to_array(file_bytes)

    internal = _dummy_internal_analysis(image)
    external = _dummy_external_analysis(image)
    puz19_block = _dummy_puz19_total(internal, external)
    ai_detection = _dummy_ai_detection(image)
    forensics = _dummy_forensics()
    explanation = _dummy_explanation()
    debug = DebugInfo(available=False)

    request_id = f"req_demo_{datetime.utcnow().timestamp()}"

    result = AnalyzeResult(
        request_id=request_id,
        media_type=media_type,
        puz19=puz19_block,
        ai_detection=ai_detection,
        forensics=forensics,
        explanation=explanation,
        debug=debug,
    )
    return result


# ---------- Gem / Mineral Analyzer (stark vereinfacht, Demo) ----------

class GemClassification(BaseModel):
    group: str
    main_species: str
    puz19_gem_index: float
    confidence: float


class MarketPriceRange(BaseModel):
    price_low: float
    price_high: float
    unit: str
    per: str
    confidence: float


class ObjectEstimate(BaseModel):
    input_weight: float
    weight_unit: str
    estimated_value_low: float
    estimated_value_high: float
    valuation_mode: str
    note: str


class MarketValue(BaseModel):
    base_currency: str
    retail: MarketPriceRange
    wholesale: MarketPriceRange
    object_estimate: Optional[ObjectEstimate] = None
    sources_used: List[dict]


class GemAnalyzeResult(BaseModel):
    stone_id: str
    classification: GemClassification
    market_value: MarketValue
    ai_bild_check: AIDetection
    authenticity: dict
    explanation: Explanation


@app.post("/api/v1/gem/analyze", response_model=GemAnalyzeResult)
async def analyze_gem(
    file: UploadFile = File(...),
    weight: Optional[float] = None,
    weight_unit: Optional[Literal["g", "ct"]] = "g",
    context: Optional[Literal["faceted_gem", "rough", "specimen"]] = "specimen",
):
    """
    Sehr vereinfachte Demo-Version eines Edelstein-/Mineral-Analyzers.
    Hier: keine echte mineralogische Erkennung, nur Struktur für dich zum Ausbau.
    """
    file_bytes = await file.read()
    image = _load_image_to_array(file_bytes)

    # Dummy-Klassifikation – später durch echte Modelle ersetzen
    classification = GemClassification(
        group="Carbonates",
        main_species="Rhodochrosite (Demo)",
        puz19_gem_index=6.4,
        confidence=0.75,
    )

    # Dummy-Marktpreisspanne (Euro pro Gramm)
    retail_range = MarketPriceRange(
        price_low=25.0,
        price_high=75.0,
        unit="EUR",
        per="g",
        confidence=0.6,
    )
    wholesale_range = MarketPriceRange(
        price_low=15.0,
        price_high=40.0,
        unit="EUR",
        per="g",
        confidence=0.5,
    )

    object_estimate = None
    if weight is not None:
        w_g = weight if weight_unit == "g" else weight * 0.2
        est_low = w_g * retail_range.price_low
        est_high = w_g * retail_range.price_high
        object_estimate = ObjectEstimate(
            input_weight=weight,
            weight_unit=weight_unit,
            estimated_value_low=est_low,
            estimated_value_high=est_high,
            valuation_mode=context,
            note="Wert basierend auf Demo-Marktpreisspanne und Gewicht.",
        )

    market_value = MarketValue(
        base_currency="EUR",
        retail=retail_range,
        wholesale=wholesale_range,
        object_estimate=object_estimate,
        sources_used=[
            {
                "name": "Demo-Source",
                "type": "synthetic_demo_data",
                "weight": 1.0,
            }
        ],
    )

    ai_check = _dummy_ai_detection(image)

    authenticity = {
        "is_natural_stone_prob": 0.7,
        "is_synthetic_prob": 0.2,
        "is_glass_or_plastic_prob": 0.1,
        "overall_label": "likely_natural_demo",
        "confidence": "medium",
    }

    explanation = Explanation(
        summary="Demo-Gem-Analyse. Struktur und Datenfelder sind vorbereitet für echte Modelle.",
        reasons=[
            "Mineralgruppe und Art sind hier nur Platzhalter.",
            "Marktpreise sind fiktive Demo-Werte.",
            "Die Struktur kann direkt mit echten Datenquellen verknüpft werden."
        ],
        confidence_level="low",
    )

    stone_id = f"gem_demo_{datetime.utcnow().timestamp()}"

    result = GemAnalyzeResult(
        stone_id=stone_id,
        classification=classification,
        market_value=market_value,
        ai_bild_check=ai_check,
        authenticity=authenticity,
        explanation=explanation,
    )
    return result
