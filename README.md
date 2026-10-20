# Exercise for My Programming Logic in "Python for AI Engineering"

## Logger & Debug Helper

```python
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)-7s %(name)s: %(message)s"))
logger.addHandler(_handler)

def dbg(label: str, obj) -> None:
    logger.debug("[%s] type=%r repr=%r", label, type(obj).__name__, obj)
```

## Custom Exception

```python
class FraudDetector(Exception):
  pass

class ConnectionError(Exception):
  pass
```

## Model Schema

```python
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
```

## Function

```python

async def simpan_ke_db(id_invoice: str):
  await asyncio.sleep(2)
  logger.info(f"Invoice berhasil disimpan: {id_invoice}")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def panggil_api_ekstraksi(raw_data: RawInvoice) -> dict:
  random_choice = choice([True, False])
  if random_choice == True:
    raise ConnectionError("API LLM Down")
  return raw_data


async def proses_satu_invoice(raw_data: RawInvoice):
  try:
    api_ekstraksi = await panggil_api_ekstraksi(raw_data)
    isvalid_invoice = InvoiceValid(**api_ekstraksi)
    word = "FAKE"
    if word in isvalid_invoice.id_invoice.upper():
      raise FraudDetector("Indikasi Penipuan Terdeteksi!")

  except ValidationError as e:
    logger.warning("Peringatan: LLM Format salah!", exc_info=True )
  except FraudDetector as e:
    logger.error(e)
  except Exception as e:
    logger.error(e)
  else:
    logger.info("Invoice Valid")
    asyncio.create_task(simpan_ke_db(id_invoice=isvalid_invoice.id_invoice))
    return isvalid_invoice
  finally:
    logger.info(f"Selesai memproses invoice: {raw_data['id_invoice']}")


async def stream_laporan(daftar_sukses: list[InvoiceValid]):
  for inv in daftar_sukses:
    list_kata = ["Berhasil", "memproses", inv.id_invoice]
    for kata in list_kata:
      await asyncio.sleep(0.3)
      yield kata
```

## Data Test

```python
data_test = [
    # Invoice Sempurna
    {"id_invoice": "INV-1001", "items": [{"nama": "Server", "harga": 5000}, {"nama": "Mouse", "harga": 1000}], "total_tagihan": 6000},

    # Invoice Halusinasi LLM, picu ValidationError
    {"id_invoice": "INV-1002", "items": [{"nama": "Keyboard", "harga": 2000}], "total_tagihan": 9999},

    # Invoice Penipuan, picu FraudDetection
    {"id_invoice": "FAKE-999", "items": [{"nama": "Hacker Tool", "harga": 1000}], "total_tagihan": 1000}
]

```

## Run Module

```python
async def main():
  hasil = await asyncio.gather(
    proses_satu_invoice(data_test[0]),
    proses_satu_invoice(data_test[1]),
    proses_satu_invoice(data_test[2])
  )

  daftar_sukses = [h for h in hasil if h is not None]

  async for token in stream_laporan(daftar_sukses):
    print(token, end=" ", flush=True)
  print()



asyncio.run(main())
```

## Setup

```Bash

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# On Git Bash Windows:
source .venv/Scripts/activate

# Install the required data science packages
pip install -r requirements.txt
```
