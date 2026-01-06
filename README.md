# ml-serving-mlops-lite

Bu repoda, basit bir makine öğrenmesi modelini üretimde servis etmeye yönelik minimal bir MLOps örneğini uyguladım. Proje FastAPI ile API sunuyor, Prometheus uyumlu temel metrikleri topluyor ve modeli hafif bir servis mantığıyla yüklüyor/predikt yapıyor. Amacım hızlı bir prototip üzerinden model dağıtımı, izleme ve test akışı göstermekti.

## Özellikler
- FastAPI tabanlı HTTP API
- Basit model yükleme ve tahmin akışı (`app/services` altında)
- Prometheus metrikleri ve health check (`/metrics`, `/healthz`)
- Docker ve `docker-compose` ile kolay çalıştırma
- Basit testler (unit ve integration)

## Depo Yapısı (kısa)
- `app/` : Uygulama kodu (API, çekirdek konfigürasyon, middleware, monitoring, servisler)
- `models/` : Eğitilmiş/model dosyaları
- `scripts/` : Yardımcı scriptler (ör. `train_dummy_model.py`)
- `tests/` : Birim ve entegrasyon testleri

## Gereksinimler
- Python 3.10+ (venv kullanmanızı öneririm)
- `pip install -r requirements.txt`

## Lokal Çalıştırma
1. Sanal ortam oluşturup aktifleştir:

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Uvicorn ile başlat:

```bash
uvicorn app.main:app --reload --port 8000
```

API dokümantasyonuna `http://localhost:8000/docs` üzerinden ulaşabilirsiniz (eğer docs aktifse).

## Docker ile Çalıştırma
Docker yüklüyse, servisleri `docker-compose` ile ayağa kaldırıyorum:

```bash
docker-compose up --build
```

Bu, uygulamayı ve varsa yardımcı servisleri başlatır. Logları takip ederek işlemlerin başarılı olduğunu doğrulayabilirsiniz.

## API Kullanımı (kısa)
- `GET /healthz` : Uygulama sağlığı için basit kontrol ("ok" döner).
- `POST /predict` : Modelinize bağlı olarak giriş verisi alır ve tahmin döner. (Detaylı örnek request/response için `app/api/routes.py`'ye bakın.)
- `GET /metrics` : Prometheus uyumlu metrikler.

## Model Eğitimi
Repository içinde bir dummy eğitim script'i var: `scripts/train_dummy_model.py`. Gerçek kullanımda kendi eğitim hattınızı burada veya ayrı bir pipeline'da çalıştırıp `models/` altına konumlandırabilirsiniz.

## Testler
Testleri çalıştırmak için:

```bash
pytest -q
```

Projede hem birim hem entegrasyon testleri bulunmaktadır; yeni değişiklikler eklerken testleri çalıştırmayı unutmayın.

## Nasıl Katkıda Bulunurum
1. Fork.
2. Yeni feature veya düzeltme için branch açın.
3. Değişiklikleri test edin ve PR açın.

