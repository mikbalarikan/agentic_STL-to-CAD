# OD-H12 Pompa — STL → STEP tersine mühendislik

**Girdi:** `pipeline/tasks/OD-H12-Pump.stl` (979 819 üçgen, su geçirmez değil, tek kabuk tarama).
**Parça:** ULKA tipi titreşimli pompa (bobin + sac U-çerçeve + plastik gövde + çıkış borusu + hortum rakoru).
**Yöntem:** `stl2step-build123d` skill'i — trimesh ile datum/kesit analizi, build123d ile tasarım-niyeti
yeniden kurulum (revolve + extrude + boolean), bloklayıcı iki yönlü sapma kapısı. Kumpas ölçüsü yok;
tüm ölçüler taramadan (tek otorite tarama).

## Teslimatlar

| Dosya | Ne |
|---|---|
| `OD-H12-Pump.step` | **Ana teslim.** Tek kapalı katı gövde, orijinal STL koordinatlarında (taramanın üstüne birebir oturur). |
| `OD-H12-Pump_datum.step` | Aynı katı, datum çerçevesinde: pompa ekseni = +Z (çıkış −Z, giriş rakoru +Z), X = sac çerçeve yan plaka normali, orijin eksen üzerinde. |
| `OD-H12-Pump_cad.stl`, `OD-H12-Pump_datum.stl` | Karşılaştırma/önizleme için CAD'in mesh'i. |
| `report/` | Parametreler, kapı raporları, görseller, hizalama matrisi, kaynak kod. |

STEP yeniden içe aktarılıp doğrulandı (`report/export_check.json`): **1 katı, geçerli, kapalı (manifold), 213 yüz,
hacim 114 903 mm³**, datum bbox 54.05 × 55.15 × 121.95 mm. Model üçgen dikişli değil: düzlem/silindir/koni/torus yüzeyler.

## Sapma kapısı (CAD ↔ tarama, datum çerçevesi)

| Yön | RMS | p95 | p99 | max |
|---|---|---|---|---|
| tarama → CAD (493 060 tarama noktası) | 0.217 | **0.448** | 0.674 | 2.49 |
| CAD → tarama, görülebilir yüzeyler (n=14 870) | 0.354 | **0.567** | 1.56 | 8.65 |
| CAD → tarama, ham (tümü) | 1.61 | 3.43 | 5.45 | 9.03 |

Bölgesel tarama→CAD p95: çıkış borusu 0.39 · ön gövde/flanş 0.49 · bobin+çerçeve 0.45 · giriş rakoru 0.27 mm.
Orijinal STL çerçevesinde bağımsız tekrar: median 0.102 / p95 0.448 — hizalama kaybı yok.

**Hüküm (dürüst):** Skill'in tüketici-plastiği bandı p95 ≤ 0.30 / max ≤ 0.80 mm → **KARŞILANMADI**
(p95 0.448, max 2.49). Neden ve kalan farkın dağılımı:

- Tarama kendi içinde temiz bir silindirde bile p95 0.13 mm gürültü taşıyor; bobin yüzeyi ±0.1 mm hafif konik/dalgalı
  (r 23.50–23.84), bobine tek silindir oturttum (Ø47.30).
- 1.2 mm üstü sapma noktaların yalnızca **%0.16**'sı; kümeler: flanş cebinin gölgede kalan içi, terminal yuvasının
  içindeki bıçaklar, terminal bloğu üstündeki kabartma yazılar (ULKA / 230V 50Hz), sac yan plakalardaki küçük
  kabartmalar, vida yıldız yuvası detayı. Hepsi kozmetik/iç detay — kasıtlı olarak modellenmedi.
- CAD→tarama ham değerleri, tarayıcının fiziksel olarak göremeyeceği yüzeyleri içeriyor (sac plaka ile bobin arası
  boşluk, delik içleri, flanş cebi): CAD yüzeyinin %25.6'sı ışın testiyle "görülemez" sınıflandı; görülebilir kısım p95 0.567.

Daha sıkı bant gerekiyorsa sıradaki adımlar: bobini konik/loft yapmak, kabartma yazıları eklemek, terminal yuvasının
iç bıçaklarını modellemek — ama bunlar için kumpas/fotoğraf doğrulaması olmadan tahmin riskli.

## Model ağacı (tasarım niyeti)

1. **Dönel gövde (revolve):** çıkış ucu Ø14.0 (uç pah 0.4, Ø9.1×7 ağız) → Ø13.84 → Ø13.56 → Ø13.14 → Ø13.48 →
   z=−32.75'te Ø20.5 → koni → Ø24.0 gövde; borunun ±X'inde **A/F 11.6 anahtar düzlükleri** (z −53.7…−47.6).
   Arka: Ø15.7 pul → Ø13.0 boyun → Ø13.7 bilezik → Ø5.9 çift dişli hortum rakoru (diş Ø6.96), Ø3.0 iç delik.
2. **Bobin:** Ø47.30, z −8.8…34.5, uç radyüsü 1.0; merkez (−0.2, 0.1) — eksenden 0.2 mm kaçık (ölçülen, snap yapılmadı).
3. **Sac U-çerçeve:** dış 54.05 × 50.05 (XZ), genişlik 32.4 (Y), sac 3.1, dış büküm R4.5; yan plakalarda ön kenar
   çentikleri (6.6 geniş), ön plakada U-yuva, arka plakada iki U-cep (0.85 derin — bobin tırnakları dolduruyor).
4. **Çekirdek tüp (gizli):** Ø16 plaka-plaka; bobini çerçeveye bağlar (gerçek pompadaki solenoid tüpü; taramada görünmez).
5. **Elmas flanş:** Ø24.1 göbek + 2× R3.9 lob gövdesi (hull), z −12.4…−18.7; alt yüzde 1.2 kenarlı cep (2.2 derin),
   ±Y uçlarında 2.4 geniş U-pencereler; **2 yıldız başlı vida** (Ø7.7 kubbe başlık, yıldız yuvası).
6. **Terminal bloğu:** 45.7 × 22.4 × ~6, önde basamaklı zemin, üstte 0.48 mm alçak bölge; 2 faston dili
   (6.5 × 0.8, cep içinde), eğimli kaburga, 29.6° döndürülmüş yuva kutusu (11.5 × 5.0, üst yüz z=13.6).

Tüm değerler: `report/params.json` (104 parametre). Her ölçü taramadan: kesit/çember uydurma/normal histogramı.

## Varsayımlar ve sınırlar (operatör onayı gerekli)

- **Ölçek:** STL birimsiz; mm kabul edildi (gövde 122 mm boy, ULKA EX5 boyutlarıyla tutarlı). Kumpasla doğrulanmadı.
- **Görülemeyen iç geometri:** sac kalınlığı (3.1 — yalnızca kısmi iç yüzden), çekirdek tüp Ø16, flanş cebi derinliği,
  delik derinlikleri (çıkış ağzı 7 mm, rakor deliği 12 mm) — tarama bunları kanıtlamıyor; tasarım niyeti tahmini.
- **Montaj tek gövde:** kullanıcı "solid body" istedi → pompa parçaları (bobin, sac, plastik, vidalar, faston) tek katıda
  birleşik. Parça-parça (multi-body) STEP gerekiyorsa ayrı iş.
- Kabartma yazılar, kablo/bıçak iç detayları, vida yıldız yuvası geometrisi yaklaşık/atlandı.
- Validator (OGUZ ground truth) 13/13 PASS — ama beklenen değerler de taramadan geldi; bu bağımsız bir doğrulama değil,
  topoloji + ölçü tutarlılığı kontrolüdür. Bağımsız kanıt sapma kapısıdır.

## Yeniden üretim

```
cd report/src
%LOCALAPPDATA%\oguz-work\venv\Scripts\python.exe export_final.py out        # STEP/STL (T1.npy + pump.stl aynı klasörde)
%LOCALAPPDATA%\oguz-work\venv\Scripts\python.exe gate.py pump.stl T1.npy out/OD-H12-Pump_datum.stl out/gate
```
`T1.npy` / `report/alignment_T1.json`: orijinal STL → datum dönüşümü (4×4). Deterministik: tohumlar sabit.
