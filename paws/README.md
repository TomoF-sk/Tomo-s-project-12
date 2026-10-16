# PAWS 平面図 — ドッグサロン兼カフェ（客席3案）

愛媛県西条市の PAWS 計画（クリニック / ドッグサロン兼カフェ / ドッグラン）のうち、**サロン兼カフェ棟**の客席バリエーションです。

## 共通条件

| 項目 | 内容 |
|------|------|
| 建築幅（横） | **11,500 mm（11.5 m）** |
| 建築奥行（縦） | **14,560 mm**（参考図据置） |
| 入口 | 風除室①② — 既存位置を維持 |
| トリミング | **5帖 × 2室**（シャンプー室 + トリミング室） |
| ゾーニング | 犬サロン（東）と保護猫エリア（北東）を分離 |
| 保護猫エリア | あり（北東） |
| 厨房 | 約 **10.0帖（16.2 ㎡）** — 概ね既存規模 |

## 3パターン

| 案 | 客席構成 | ファイル |
|----|----------|----------|
| **5席** | カウンター3 + 2人卓1 | `plans/paws-cafe-5seats.svg` |
| **10席** | カウンター4 + 4人卓1 + 2人卓1 | `plans/paws-cafe-10seats.svg` |
| **15席** | カウンター5 + 4人卓2 + 2人卓1 | `plans/paws-cafe-15seats.svg` |

- 比較ビューア: [`plans/index.html`](plans/index.html)
- 寸法付き正確図面: `.svg` / `.png`
- プレゼン用着色図: `*-presentation.jpg`

## 再生成

```bash
cd plans
python3 generate_floorplans.py
python3 -c "from pathlib import Path; import cairosvg
for p in Path('.').glob('paws-cafe-*.svg'):
    cairosvg.svg2png(url=str(p), write_to=str(p.with_suffix('.png')), scale=2.2)"
```

## 参考

添付の既存平面図（サロン兼カフェ詳細図 / サイト全体図）を基にした基本設計段階の図面です。実施設計では構造・設備・法規確認が別途必要です。
