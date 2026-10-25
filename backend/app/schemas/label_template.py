"""Sheet layouts for custom label sheets, and the saved templates that hold
them (#3296)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.app.services.label_renderer import MAX_COLS, MAX_ROWS, MIN_LABEL_MM, PageSize, SheetLayout

# Longer than any real page side; the fit check against the page does the rest.
_MAX_LENGTH_MM = 300.0


class SheetLayoutSpec(BaseModel):
    """A sheet layout as a request carries it. Lengths are in millimetres."""

    model_config = ConfigDict(allow_inf_nan=False)

    page: PageSize
    label_w_mm: float = Field(ge=MIN_LABEL_MM, le=_MAX_LENGTH_MM)
    label_h_mm: float = Field(ge=MIN_LABEL_MM, le=_MAX_LENGTH_MM)
    cols: int = Field(ge=1, le=MAX_COLS)
    rows: int = Field(ge=1, le=MAX_ROWS)
    top_mm: float = Field(ge=0, le=_MAX_LENGTH_MM)
    left_mm: float = Field(ge=0, le=_MAX_LENGTH_MM)
    col_gap_mm: float = Field(default=0.0, ge=0, le=_MAX_LENGTH_MM)
    row_gap_mm: float = Field(default=0.0, ge=0, le=_MAX_LENGTH_MM)

    @model_validator(mode="after")
    def fits_on_page(self) -> "SheetLayoutSpec":
        problem = self.to_layout().problem()
        if problem:
            raise ValueError(problem)
        return self

    def to_layout(self) -> SheetLayout:
        return SheetLayout(**self.model_dump())


class SheetLayoutResponse(BaseModel):
    """A stored layout, returned as saved. Not re-validated, so a template saved
    under looser limits still lists rather than failing the whole response."""

    page: str
    label_w_mm: float
    label_h_mm: float
    cols: int
    rows: int
    top_mm: float
    left_mm: float
    col_gap_mm: float
    row_gap_mm: float


class LabelTemplateIn(BaseModel):
    """Create or replace a saved template: a name and the whole layout."""

    name: str = Field(..., min_length=1, max_length=100)
    layout: SheetLayoutSpec

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        return v


class LabelTemplateResponse(BaseModel):
    id: int
    name: str
    layout: SheetLayoutResponse
    created_at: datetime
    updated_at: datetime
