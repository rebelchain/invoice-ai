import logging
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field, ValidationError, ConfigDict, field_validator, ValidationInfo




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InvoiceAI")

def dbg(label: str, obj) -> None:
  logger.warning("[%s] type=%r repr=%r", label, type(obj).__name__, obj)

class FraudDetector(Exception):
  pass





class RawInvoice(TypedDict):
  id_invoice: str
  items: list[dict]
  total_tagihan: int

class ItemBarang(BaseModel):
  nama: Annotated[str, Field(description="Nama barang")]
  harga: Annotated[int, Field(description="Harga barang", ge=1000)]


class InvoiceValid(BaseModel):
  id_invoice: Annotated[str, Field(description="ID Invoice", min_length=5)]
  items: Annotated[list[ItemBarang], Field(description="Daftar item barang", min_length=1)]
  total_tagihan: Annotated[int, Field(description="Total tagihan")]

  model_config = ConfigDict(extra="forbid")

  @field_validator("total_tagihan")
  @classmethod
  def jumlahkan_semua_item(cls, value: int, info: ValidationInfo) -> int:
    items = info.data.get("items")
    if items is None: return value
    jumlah_harga = 0
    for item in items:
      jumlah_harga += item.harga
    if value != jumlah_harga:
      raise ValueError("Total tagihan tidak cocok dengan jumlah harga item!")
    return value