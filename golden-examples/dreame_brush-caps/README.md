# Dreame fırça kapakları — STL → STEP tersine mühendislik teslimi

Tarih: 2026-09-17 · Araç zinciri: trimesh (mesh analizi) + build123d 0.11 / OpenCascade (parametrik yeniden çizim) · Birim: mm (STL'deki gibi, ölçek uygulanmadı)

## Teslim edilen dosyalar

| Dosya | İçerik |
|---|---|
| `dreame_brush_screw_cap.step` | Tek solid body, **STL ile aynı koordinat çerçevesi** (STL'nin üstüne birebir biner) |
| `dreame_brush_screw_cap_datum_frame.step` | Aynı solid, parça datum çerçevesinde (üst düz yüz z=0, delik ekseni = Z, bir beşgen düz yüzeyin normali = +X) |
| `dreame_brush_screw_cap_cad.stl` | CAD'in mesh'i (STL çerçevesi, karşılaştırma için) |
| `dreame_brush_snap_cap.step` | Tek solid body, STL ile aynı çerçeve |
| `dreame_brush_snap_cap_datum_frame.step` | Datum çerçevesi (plaka üst yüzü z=0, delik ekseni = Z, düz kesimin normali = +X) |
| `dreame_brush_snap_cap_cad.stl` | CAD mesh'i |
| `report/` | Sapma raporları (JSON), parametre tabloları, hizalama matrisleri, kesit overlay/sapma haritaları, build123d kaynak kodu |

Her iki STEP tek, kapalı, geçerli (BRep check OK) solid: **screw cap 56 yüzey** (düzlem/silindir/koni/tor + 5 yuva silindiri), **snap cap 63 yüzey**. Yüzeyler dikilmiş üçgen yamalar değil; her biri bir sketch + extrude/revolve/boolean/fillet feature'ından geliyor. `report/source/build_screw.py` ve `build_snap.py` tam feature ağacıdır ve parametre sözlüğü `P` değiştirilerek yeniden üretilebilir.

## Yöntem (her iki parça)

1. **Datum (F00):** en büyük düz yüzeye RANSAC düzlem fit (screw: üst disk yüzü, rms 0.007 mm; snap: plaka üst yüzü, rms 0.029 mm) → Z ekseni. Delik ekseni: Z-kesitlerinde iç halkalara çember fit (merkez sapması <0.01 mm) → orijin. Saat açısı: screw'de beşgen düz yüzeyi, snap'te düz kesim normali +X'e alındı. Matrisler `report/*_alignment.json`.
2. **Kesitler:** Z boyunca 25 istasyon + eksen etrafında yarım-düzlem radyal kesitler; (r,z) ve (θ,r) yoğunluk haritaları; her primitif için en küçük kareler çember/doğru fit.
3. **Tasarım niyetine yuvarlama:** ölçülen → seçilen değerler aşağıdaki tablolarda. Kumpas ölçümü YOK; tüm boyutlar tarama otoritesiyle (yuvarlamalar 0.01–0.05 mm içinde).
4. **Yeniden çizim:** SolidWorks tarzı sıralı feature ağacı (aşağıda).
5. **Sapma kapısı:** iki yönlü (tarama→CAD ve CAD→tarama) mesafe; tam çözünürlüklü ham tarama (screw 1.8 M, snap 4.9 M üçgen) kullanıldı.

## Screw cap — feature ağacı ve parametreler

| # | Feature | Parametreler (ölçülen → seçilen) |
|---|---|---|
| F01 | Beşgen sketch + extrude (z −5.12 → −0.45) | apotem 4.48–4.52 → **4.50**; köşeler 36°+k·72° |
| F02 | Ø silindir ile kesişim (köşe tornası) | köşe yarıçapı 5.43–5.46 → **Ø10.90** |
| F03 | Alt pah: 5 düzlem, dikeyden 29–30° → **30°**, başlangıç z −2.93; pah köşe fillet | fillet ρ 1.05–1.19 → **R1.15** |
| F04 | Üst disk (revolve): taban r 4.36 → **4.38 @ z −0.45**, tepe r 3.90–3.95 → **3.95 @ z 0** (≈45° pah); tepe kenar fillet | **R0.25** |
| F05 | 5 parmak yuvası: R14 silindir kesimi, eksen dikeyden **5.15°** eğik | derinlik 0 @ z −0.45, 0.23 @ z −3.0 (ölçülen 0.06 @ −1.0, 0.19 @ −2.5, 0.23 @ −3.0) |
| F06 | Çift-D delik (z 0 → −2.60) | yay r 1.949 → **Ø3.90**; düzlemler ±1.63/1.65 → **3.28 A/F**, düzlemler beşgen düz yüzeye paralel |
| F07 | Gövde (web) deliği | r 1.04 → **Ø2.08**, web z **−2.60 … −4.05**, iç kenar fillet **R0.55 / R0.60** |
| F08 | Alttan havşa | r 2.04–2.05 → **Ø4.10**, z −4.05 → −5.12, alt kenar pah 0.15 |
| F09 | Alt dış kenar fillet | **R0.30** |

Toplam yükseklik 5.12, hacim 269.1 mm³.

## Snap cap — feature ağacı ve parametreler

| # | Feature | Parametreler (ölçülen → seçilen) |
|---|---|---|
| F01 | Revolve profili (plaka) | delik r 7.002 → **Ø14.00**; dış r 11.865 → **Ø23.73**; üst z 0; alt iç bant z **−1.53** (r < 9.58), 45° basamak → dış bant z **−1.84** (r > 9.85); delik altı **0.9 × 45°** pah |
| F02 | Alt rampa (+X sektörü) | düzlem z = −1.402 + 0.0835·(x − 7.714) (**4.77°**), altı kesildi; ölçüm rms 0.07 |
| F03 | Düz kesim + köşe fillet | x = **8.93** (rms 0.008); fillet 2.5–3.0 → **R2.75** ×2 |
| F04 | Ayak + kanca (tek profil, ±9.6° revolve, 3 kopya) | θ = **60°, 150°, −60°** (eşit aralıklı DEĞİL, ölçüldü); iç r **11.00**, dış r **11.90**; kanca dış r 12.43–12.55 → **12.48**; tutucu yüz z **5.25**; rampa (12.48, 5.62)→(11.78, 6.25); tepe z **6.25**; iç tepe fillet **R0.30**; rahatlatma oluğu r **11.73** (z 4.68–4.98) |
| F05 | 4 konik yuva | PCD r 8.81–9.02 → **8.90**; üst Ø3.04 → taban Ø2.76, derinlik **0.43**; θ = 60°, 150°, −60°, −140° |
| F06 | Kenar yuvarlatma | dış üst kenar **R0.20**, delik üst kenar **R0.15** |

Hacim 454.1 mm³.

## Sapma sonuçları (CAD vs ham tarama, mm)

Bantlar (repo `re-deviation` kapısı, tüketici plastiği): p95 ≤ 0.30, max ≤ 0.80.

| Parça | Yön | RMS | p95 | max | Karar |
|---|---|---|---|---|---|
| screw cap | tarama → CAD (50 k örnek) | 0.043 | 0.085 | 0.245 | PASS |
| screw cap | CAD → tarama (50 k) | 0.038 | 0.076 | 0.268 | PASS |
| snap cap | tarama → CAD (50 k, masa düzlemi hariç) | 0.085 | 0.157 | 1.226 | p95 PASS, **max FAIL** (aşağıdaki artefaktlar) |
| snap cap | CAD → tarama (50 k) | 0.045 | 0.087 | 0.273 | PASS |
| snap cap | tarama → CAD, artefakt bölgeleri hariç (%4.9 nokta) | 0.068 | 0.116 | p99 0.233 | — |

Hızlı KD-tree kapısı (600 k / 300 k örnek) aynı değerleri veriyor (`report/*_fastgate.json`). CAD→tarama yönü "CAD'de olup taramada olmayan malzeme"yi ölçer ve her iki parçada temiz: modelde uydurulmuş geometri yok.

**Snap cap taramasındaki, modellenmeyen artefaktlar** (tarama→CAD max'ı bunlardan gelir):
- Tarayıcı masası: z ≈ −1.83'te delik içinden dış çapın ötesine uzanan yatay levha (ham tepe noktalarının %9.3'ü) — ana gövdeye bağlı olduğu için tarama kesitlerinde parça gibi görünür; normali yukarı baktığı için kapıdan çıkarıldı.
- Delik üst kenarında içe eğik çapak/etek halkası (r 6.5–6.95, z −0.1…+0.2, tek bağlı yüzey, %1.4).
- Dış çap üst kenarında çapak, θ −150…−60° (r 12.0–12.3, %0.9).
- Kanca altındaki "köprü" yüzeyi (r > 11.95, z 4.3–5.2, %0.9): tarayıcı gölgesinden dolayı kanca altı ile ayak dış yüzü arası doldurulmuş; tasarım niyeti olarak yatay tutucu yüz + rahatlatma oluğu modellendi (ayak merkezindeki ham kesitle uyumlu).
- Kanca tepesi saçakları (%0.2), düz kesim köşelerinde masa–parça köprüleri (%0.2).
- 150° ayağının tepesinden içeri uzanan yüzen bir tarama kanadı (r 9.8–10.7, z ≈ 6.1; maskeleme sonrası kalan tek 1.2 mm'lik sapma bu, 570 k noktanın 315'i > 0.8 mm).

Screw cap'te tek dikkat çeken yer: üst yüzde θ≈70° civarında 0.2–0.25 mm'lik yerel çukur (parça hasarı/çapak), modellenmedi.

## Varsayımlar ve sınırlar
- Kumpas ölçümü olmadığı için tüm boyutlar tarama otoritesindedir; standart değerlere yuvarlama sadece tarama gürültüsü (≈0.02–0.05 mm) içinde yapıldı.
- Snap cap'in üç ayağı özdeş modellendi; ölçümde 150° ayağı diğerlerinden ~0.1 mm daha dışarıda.
- Dört yuva ortak PCD'ye (r 8.90) alındı; −60° yuvası ölçümde r 9.02.
- Screw cap düz yüzeylerindeki parmak yuvaları eğik eksenli silindir kesimi olarak modellendi (ölçülen içbükeylik profiline ≤0.05 mm hata).
- Snap cap düz kesim sektöründeki alt rampa tek düzlem; ölçümde ±0.07 mm dalgalanma var.
- Görsel kanıt: `report/views/*_overlay.png` (kesitlerde siyah = tarama, kırmızı = CAD), `*_dev_s2c.png` / `*_dev_c2s.png` (sapma haritaları).
