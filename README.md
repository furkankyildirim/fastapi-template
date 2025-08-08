# FastAPI Template

Bu proje FastAPI kullanarak geliştirilmiş bir template projesidir.

## Kurulum

### Gereksinimler

- Python 3.8+
- uv (Python paket yöneticisi)

### uv Kurulumu

```bash
# uv'yi kur
pip install uv

# veya
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Proje Kurulumu

```bash
# Projeyi klonla
git clone <repository-url>
cd fastapi-template

# Sanal ortam oluştur ve bağımlılıkları kur
uv venv
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate  # Windows

# Projeyi geliştirme modunda kur
uv pip install -e .

# Geliştirme bağımlılıklarını kur
uv pip install -e ".[dev]"
```

## Çalıştırma

### Geliştirme Modu

```bash
# Sanal ortamı aktifleştir
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate  # Windows

# Uygulamayı çalıştır
uvicorn src:app --reload --host 0.0.0.0 --port 8000
```

### Docker ile

```bash
# Docker image'ını oluştur
docker build -t fastapi-template .

# Container'ı çalıştır
docker run -p 8000:8000 fastapi-template
```

## Geliştirme

### Kod Formatı

```bash
# Black ile kod formatı
uv run black .

# isort ile import sıralaması
uv run isort .
```

### Linting

```bash
# flake8 ile linting
uv run flake8 .

# mypy ile tip kontrolü
uv run mypy .
```

### Testler

```bash
# Testleri çalıştır
uv run pytest
```

## Paket Yönetimi

### Yeni Paket Ekleme

```bash
# Üretim bağımlılığı ekle
uv add package-name

# Geliştirme bağımlılığı ekle
uv add --dev package-name
```

### Paket Güncelleme

```bash
# Tüm paketleri güncelle
uv pip compile --upgrade
```

## Proje Yapısı

```
fastapi-template/
├── src/
│   ├── configs/
│   ├── controllers/
│   ├── database/
│   ├── errors/
│   ├── middlewares/
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── utils/
├── alembic/
├── logs/
├── media/
├── pyproject.toml
├── Dockerfile
└── README.md
```

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
