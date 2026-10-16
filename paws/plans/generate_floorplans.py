#!/usr/bin/env python3
"""PAWS ドッグサロン兼カフェ — 横幅11.5m / 席数3パターン図面生成

参考図（横12,740×縦14,560）を横11,500に再配分。
縦寸法・入口位置・トリミング5帖×2・犬猫分離・保護猫・厨房規模は維持。
"""

from __future__ import annotations

import html
from pathlib import Path

# ---------------------------------------------------------------------------
# 寸法 (mm)
# 参考横: 3640+910+1365+2275+910+3640 = 12740
# 新横:   3185+910+1365+1945+910+3185 = 11500
# 縦:     4550+910+1820+3640+1820+1820 = 14560（据置）
# ---------------------------------------------------------------------------

W, H = 11500, 14560
SCALE = 0.052  # mm → px

X = [0, 3185, 4095, 5460, 7405, 8315, 11500]
Y = [0, 4550, 5460, 7280, 10920, 12740, 14560]

OUT = Path(__file__).resolve().parent


def mm(v: float) -> float:
    return v * SCALE


def jo(m2: float) -> str:
    return f"{m2 / 1.62:.1f}帖"


def area(x0, y0, x1, y1) -> float:
    return abs(x1 - x0) * abs(y1 - y0) / 1e6


def esc(s: str) -> str:
    return html.escape(s)


# --- 席配置 -----------------------------------------------------------------

def seats_5():
    items = []
    # サービスカウンター沿い 3席
    base_x, base_y = 2800, 6200
    items.append(("counter", base_x - 200, base_y - 500, 2200, 400))
    for i in range(3):
        items.append(("stool", base_x + 200 + i * 550, base_y + 200))
    # 2人テーブル 1
    items.append(("table2", 4200, 11800))
    return items


def seats_10():
    items = []
    base_x, base_y = 2600, 6000
    items.append(("counter", base_x - 100, base_y - 450, 2800, 400))
    for i in range(4):
        items.append(("stool", base_x + 250 + i * 550, base_y + 250))
    items.append(("table4", 3200, 11850))
    items.append(("table2", 5600, 12000))
    return items


def seats_15():
    items = []
    base_x, base_y = 2400, 5900
    items.append(("counter", base_x, base_y - 450, 3200, 400))
    for i in range(5):
        items.append(("stool", base_x + 300 + i * 550, base_y + 250))
    items.append(("table4", 2500, 11600))
    items.append(("table4", 4800, 11600))
    items.append(("table2", 6200, 13200))
    return items


SEAT_FN = {5: seats_5, 10: seats_10, 15: seats_15}


def draw_furniture(items) -> str:
    out = ['<g id="seating" fill="none" stroke="#222" stroke-width="1.15">']
    for it in items:
        kind = it[0]
        if kind == "stool":
            _, x, y = it
            out.append(
                f'<circle cx="{mm(x):.1f}" cy="{mm(y):.1f}" r="{mm(155):.1f}" fill="#faf6f0"/>'
            )
        elif kind == "counter":
            _, x, y, w, h = it
            out.append(
                f'<rect x="{mm(x):.1f}" y="{mm(y):.1f}" width="{mm(w):.1f}" height="{mm(h):.1f}" '
                f'fill="#e6dccf" stroke-width="1.4"/>'
            )
        elif kind == "table2":
            _, x, y = it
            out.append(
                f'<rect x="{mm(x-420):.1f}" y="{mm(y-320):.1f}" width="{mm(840):.1f}" '
                f'height="{mm(640):.1f}" rx="2" fill="#faf6f0"/>'
            )
            for sx in (x - 520, x + 520):
                out.append(
                    f'<circle cx="{mm(sx):.1f}" cy="{mm(y):.1f}" r="{mm(145):.1f}" fill="#faf6f0"/>'
                )
        elif kind == "table4":
            _, x, y = it
            out.append(
                f'<rect x="{mm(x-500):.1f}" y="{mm(y-500):.1f}" width="{mm(1000):.1f}" '
                f'height="{mm(1000):.1f}" rx="2" fill="#faf6f0"/>'
            )
            for sx, sy in ((x, y - 640), (x, y + 640), (x - 640, y), (x + 640, y)):
                out.append(
                    f'<circle cx="{mm(sx):.1f}" cy="{mm(sy):.1f}" r="{mm(145):.1f}" fill="#faf6f0"/>'
                )
    out.append("</g>")
    return "\n".join(out)


def room(x0, y0, x1, y1, name, fill, *, note=None, size=True, weight=600):
    a = area(x0, y0, x1, y1)
    cx, cy = mm((x0 + x1) / 2), mm((y0 + y1) / 2)
    # 狭い部屋は文字サイズを落とす
    tw, th = abs(x1 - x0), abs(y1 - y0)
    fs = 9 if min(tw, th) < 1500 else 10.5
    parts = [
        f'<rect x="{mm(x0):.1f}" y="{mm(y0):.1f}" width="{mm(x1-x0):.1f}" '
        f'height="{mm(y1-y0):.1f}" fill="{fill}" stroke="#1a1a1a" stroke-width="1.7"/>',
        f'<text x="{cx:.1f}" y="{cy - (8 if size or note else 0):.1f}" text-anchor="middle" '
        f'font-family="{JP}" '
        f'font-size="{fs}" font-weight="{weight}" fill="#1a1a1a">{esc(name)}</text>',
    ]
    if size:
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + 8:.1f}" text-anchor="middle" '
            f'font-family="{JP}" '
            f'font-size="8" fill="#555">{jo(a)}（{a:.1f}㎡）</text>'
        )
    if note:
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + (20 if size else 8):.1f}" text-anchor="middle" '
            f'font-family="{JP}" '
            f'font-size="7.5" fill="#666">{esc(note)}</text>'
        )
    return "\n".join(parts)


def open_zone(x0, y0, x1, y1, fill):
    return (
        f'<rect x="{mm(x0):.1f}" y="{mm(y0):.1f}" width="{mm(x1-x0):.1f}" '
        f'height="{mm(y1-y0):.1f}" fill="{fill}" stroke="#1a1a1a" stroke-width="1.7"/>'
    )


# 日本語レンダリング用（SVG表示／Cairo PNG両対応）
JP = "Droid Sans Fallback, WenQuanYi Micro Hei, Noto Sans CJK JP, Hiragino Sans, sans-serif"
MONO = "IBM Plex Mono, DejaVu Sans Mono, Menlo, monospace"


def label(x, y, text, *, fs=10.5, weight=600, fill="#1a1a1a"):
    return (
        f'<text x="{mm(x):.1f}" y="{mm(y):.1f}" text-anchor="middle" '
        f'font-family="{JP}" '
        f'font-size="{fs}" font-weight="{weight}" fill="{fill}">{esc(text)}</text>'
    )


def dim_h(x0, x1, y, text):
    mid = (x0 + x1) / 2
    return f'''<g stroke="#333" fill="#222" stroke-width="0.85">
  <line x1="{mm(x0):.1f}" y1="{mm(y):.1f}" x2="{mm(x0):.1f}" y2="{mm(y+70):.1f}"/>
  <line x1="{mm(x1):.1f}" y1="{mm(y):.1f}" x2="{mm(x1):.1f}" y2="{mm(y+70):.1f}"/>
  <line x1="{mm(x0):.1f}" y1="{mm(y+50):.1f}" x2="{mm(x1):.1f}" y2="{mm(y+50):.1f}"/>
  <text x="{mm(mid):.1f}" y="{mm(y+42):.1f}" text-anchor="middle"
    font-family="{MONO}" font-size="7.5" stroke="none">{esc(text)}</text>
</g>'''


def dim_v(y0, y1, x, text):
    mid = (y0 + y1) / 2
    return f'''<g stroke="#333" fill="#222" stroke-width="0.85">
  <line x1="{mm(x):.1f}" y1="{mm(y0):.1f}" x2="{mm(x+70):.1f}" y2="{mm(y0):.1f}"/>
  <line x1="{mm(x):.1f}" y1="{mm(y1):.1f}" x2="{mm(x+70):.1f}" y2="{mm(y1):.1f}"/>
  <line x1="{mm(x+50):.1f}" y1="{mm(y0):.1f}" x2="{mm(x+50):.1f}" y2="{mm(y1):.1f}"/>
  <text x="{mm(x+62):.1f}" y="{mm(mid):.1f}" text-anchor="middle"
    font-family="{MONO}" font-size="7.5" stroke="none"
    transform="rotate(-90 {mm(x+62):.1f} {mm(mid):.1f})">{esc(text)}</text>
</g>'''


def door(x, y, swing=850, mirror=False):
    if not mirror:
        return (
            f'<path d="M {mm(x):.1f} {mm(y):.1f} A {mm(swing):.1f} {mm(swing):.1f} 0 0 1 '
            f'{mm(x+swing):.1f} {mm(y+swing):.1f}" fill="none" stroke="#1a1a1a" stroke-width="1.1"/>'
            f'<line x1="{mm(x):.1f}" y1="{mm(y):.1f}" x2="{mm(x):.1f}" y2="{mm(y+swing):.1f}" '
            f'stroke="#1a1a1a" stroke-width="2.2"/>'
        )
    return (
        f'<path d="M {mm(x):.1f} {mm(y):.1f} A {mm(swing):.1f} {mm(swing):.1f} 0 0 0 '
        f'{mm(x-swing):.1f} {mm(y+swing):.1f}" fill="none" stroke="#1a1a1a" stroke-width="1.1"/>'
        f'<line x1="{mm(x):.1f}" y1="{mm(y):.1f}" x2="{mm(x):.1f}" y2="{mm(y+swing):.1f}" '
        f'stroke="#1a1a1a" stroke-width="2.2"/>'
    )


def deck(x0, y0, x1, y1):
    parts = [
        f'<rect x="{mm(x0):.1f}" y="{mm(y0):.1f}" width="{mm(x1-x0):.1f}" height="{mm(y1-y0):.1f}" '
        f'fill="#d4c4ae" stroke="#1a1a1a" stroke-width="1.5"/>'
    ]
    y = y0 + 140
    while y < y1 - 60:
        parts.append(
            f'<line x1="{mm(x0+50):.1f}" y1="{mm(y):.1f}" x2="{mm(x1-50):.1f}" y2="{mm(y):.1f}" '
            f'stroke="#b7a48c" stroke-width="1.1"/>'
        )
        y += 260
    for ox, oy in (
        (x0 + (x1 - x0) * 0.35, y0 + (y1 - y0) * 0.32),
        (x0 + (x1 - x0) * 0.68, y0 + (y1 - y0) * 0.68),
    ):
        parts.append(
            f'<circle cx="{mm(ox):.1f}" cy="{mm(oy):.1f}" r="{mm(380):.1f}" '
            f'fill="#b9c9a8" fill-opacity="0.5" stroke="#4f6b45" stroke-width="1"/>'
        )
        parts.append(
            f'<rect x="{mm(ox-260):.1f}" y="{mm(oy-220):.1f}" width="{mm(520):.1f}" '
            f'height="{mm(440):.1f}" fill="#efe6d8" stroke="#333"/>'
        )
    parts.append(label((x0 + x1) / 2, y0 + 320, "屋外デッキ", fs=10, weight=700, fill="#3a3228"))
    parts.append(
        label((x0 + x1) / 2, y0 + 520, "参考図どおり西側配置", fs=7.5, fill="#5a5248")
    )
    return "\n".join(parts)


def build_svg(n_seats: int) -> str:
    DECK_W = 2600
    pad = dict(l=20, t=62, r=100, b=100)
    vb_w = mm(W + DECK_W) + pad["l"] + pad["r"]
    vb_h = mm(H) + pad["t"] + pad["b"]

    # 色
    KIT, CAFE, DOG, CAT, ST, WET, ENT = (
        "#f1e7d8",
        "#faf7f1",
        "#e4edf5",
        "#eaf4e6",
        "#efece6",
        "#e7eef1",
        "#ebe6de",
    )

    # --- 部屋割り（非重複） ---
    # 厨房 ≈10帖: 幅 ~3640 × 奥行 ~4550 だと大きすぎるので
    # 幅 3640×奥行 2730 ≈ 9.9帖、または 3185×2730≈8.7帖
    # 参考図は10帖なので 4550× 幅で: 10*1.62/4.55 ≈ 3.56m → 3560×4550=16.2㎡=10.0帖
    KIT_X1 = 3560
    kitchen = room(0, 0, KIT_X1, Y[1], "厨房", KIT, note="概ね既存規模", weight=700)

    # 洗面・WC（厨房東〜中央上）
    wash = room(KIT_X1, 0, X[4], 1820, "洗面所", WET)
    toilet = room(KIT_X1, 1820, X[4], Y[1], "トイレ", WET, note="多目的")

    # 保護猫（北東・犬ゾーンから離隔）
    cat = room(X[4], 0, X[6], Y[2], "保護猫エリア", CAT, note="犬ゾーンと分離", weight=700)

    # スタッフ・洗濯（猫エリア南）
    staff = room(X[4], Y[2], (X[4] + X[6]) / 2, Y[3], "スタッフルーム", ST)
    laundry = room((X[4] + X[6]) / 2, Y[2], X[6], Y[3], "洗濯室", WET)

    # サロン翼: シャンプー5帖 + トリミング5帖
    # 3185 × 2555 ≈ 8.14㎡ = 5.0帖
    SH_H = 2555
    shampoo = room(X[5], Y[3], X[6], Y[3] + SH_H, "シャンプー室", DOG, note="5帖（必須）", weight=700)
    trimming = room(
        X[5], Y[3] + SH_H, X[6], Y[3] + 2 * SH_H, "トリミング室", DOG, note="5帖（必須）", weight=700
    )
    salon_buf_y0 = Y[3] + 2 * SH_H
    salon_buf = room(X[5], salon_buf_y0, X[6], Y[6], "待機・動線", DOG, note="サロン控え")

    # 風除室（既存位置）
    vest1 = room(0, Y[1], X[1], Y[2], "風除室①", ENT, note="入口・既存位置")
    vest2 = room(0, Y[5], X[1], Y[6], "風除室②", ENT, note="入口・既存位置")

    # カフェオープン空間（厨房南〜建物南、サロン西）
    cafe_fill = open_zone(X[1], Y[1], X[5], Y[6], CAFE)
    # 風除室①の東〜カフェ上段もオープンに含めるが、vest1は別描画で上書き済み
    # 左下デッキ側のカフェ延長（風除室②の北）
    cafe_west = open_zone(0, Y[2], X[1], Y[5], CAFE)

    cafe_a = area(X[1], Y[1], X[5], Y[6]) + area(0, Y[2], X[1], Y[5])
    cafe_labels = "\n".join(
        [
            label((X[1] + X[5]) / 2, Y[1] + 700, "カフェスペース", fs=12, weight=700),
            label(
                (X[1] + X[5]) / 2,
                Y[1] + 980,
                f"客席 {n_seats}席プラン　{jo(cafe_a)}",
                fs=9,
                fill="#555",
            ),
        ]
    )

    # キッチン設備
    equip = f'''<g fill="#ddd4c6" stroke="#555" stroke-width="1">
  <rect x="{mm(400):.1f}" y="{mm(600):.1f}" width="{mm(2400):.1f}" height="{mm(550):.1f}"/>
  <rect x="{mm(400):.1f}" y="{mm(1600):.1f}" width="{mm(900):.1f}" height="{mm(900):.1f}"/>
  <rect x="{mm(KIT_X1-850):.1f}" y="{mm(Y[1]-650):.1f}" width="{mm(700):.1f}" height="{mm(420):.1f}"/>
</g>
{label(1600, 950, "作業台", fs=7.5, fill="#555")}
{label(850, 2100, "シンク", fs=7.5, fill="#555")}
{label(KIT_X1-500, Y[1]-400, "提供口", fs=7.5, fill="#555")}'''

    # サービスカウンター（厨房南面）
    svc = f'''<g>
  <rect x="{mm(X[1]+150):.1f}" y="{mm(Y[1]+80):.1f}" width="{mm(X[4]-X[1]-300):.1f}"
    height="{mm(320):.1f}" fill="#e6dccf" stroke="#222" stroke-width="1.3"/>
  {label((X[1]+X[4])/2, Y[1]+290, "サービスカウンター", fs=7.5, fill="#555")}
</g>'''

    furniture = draw_furniture(SEAT_FN[n_seats]())

    doors = "\n".join(
        [
            door(0, Y[1] + 180),
            door(0, Y[5] + 350),
            door(X[5], Y[3] + 350),
            door(X[5], Y[3] + SH_H + 350),
            door(X[4], 350),
            door(KIT_X1, 400, swing=700),
        ]
    )

    # ゾーン帯
    bands = f'''<g opacity="0.9">
  <rect x="{mm(80):.1f}" y="{mm(80):.1f}" width="{mm(1100):.1f}" height="{mm(280):.1f}"
    fill="#e3d5bf" stroke="#1a1a1a" stroke-width="0.7"/>
  {label(630, 270, "カフェ／厨房", fs=8)}
  <rect x="{mm(X[5]+80):.1f}" y="{mm(Y[3]+80):.1f}" width="{mm(1100):.1f}" height="{mm(280):.1f}"
    fill="#c9d8e8" stroke="#1a1a1a" stroke-width="0.7"/>
  {label(X[5]+630, Y[3]+270, "犬サロン", fs=8)}
  <rect x="{mm(X[4]+80):.1f}" y="{mm(80):.1f}" width="{mm(1100):.1f}" height="{mm(280):.1f}"
    fill="#cce3c6" stroke="#1a1a1a" stroke-width="0.7"/>
  {label(X[4]+630, 270, "猫ゾーン", fs=8)}
</g>'''

    dims = "\n".join(
        [
            dim_h(0, W, H + 160, f"{W} mm = 11.5 m"),
            *[dim_h(X[i], X[i + 1], H + 480, str(X[i + 1] - X[i])) for i in range(6)],
            dim_v(0, H, W + 160, f"{H} mm"),
            *[dim_v(Y[i], Y[i + 1], W + 480, str(Y[i + 1] - Y[i])) for i in range(6)],
        ]
    )

    grid = "\n".join(
        [f'<line x1="{mm(x):.1f}" y1="0" x2="{mm(x):.1f}" y2="{mm(H):.1f}"/>' for x in range(0, W + 1, 910)]
        + [f'<line x1="0" y1="{mm(y):.1f}" x2="{mm(W):.1f}" y2="{mm(y):.1f}"/>' for y in range(0, H + 1, 910)]
    )

    title = f"PAWS ドッグサロン兼カフェ 平面図｜客席 {n_seats}席案"
    sub = "愛媛県西条市｜横 11,500 mm × 縦 14,560 mm｜910モジュール｜基本設計"

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{vb_w:.0f}" height="{vb_h:.0f}"
  viewBox="0 0 {vb_w:.1f} {vb_h:.1f}">
  <rect width="100%" height="100%" fill="#f4f0e8"/>
  <text x="{pad["l"]:.1f}" y="26"
    font-family="{JP}"
    font-size="15" font-weight="700" fill="#1a1a1a">{esc(title)}</text>
  <text x="{pad["l"]:.1f}" y="44"
    font-family="{JP}"
    font-size="9.5" fill="#555">{esc(sub)}</text>

  <g transform="translate({pad["l"] + mm(DECK_W):.1f},{pad["t"]:.1f})">
    <g stroke="#e0d8cc" stroke-width="0.35">{grid}</g>

    {deck(-DECK_W, Y[4], 0, Y[6])}

    {cafe_fill}
    {cafe_west}
    {kitchen}
    {wash}
    {toilet}
    {cat}
    {staff}
    {laundry}
    {vest1}
    {vest2}
    {shampoo}
    {trimming}
    {salon_buf}
    {equip}
    {svc}
    {cafe_labels}
    {furniture}
    {doors}
    {bands}
    {dims}

    <rect x="0" y="0" width="{mm(W):.1f}" height="{mm(H):.1f}"
      fill="none" stroke="#1a1a1a" stroke-width="2.5"/>

    <g transform="translate({mm(W)-36:.1f},28)">
      <circle r="15" fill="#fff" stroke="#1a1a1a"/>
      <polygon points="0,-11 3.5,4 0,1.5 -3.5,4" fill="#1a1a1a"/>
      <text y="26" text-anchor="middle" font-size="8"
        font-family="{JP}">北</text>
    </g>
  </g>

  <text x="{pad["l"]:.1f}" y="{vb_h - 36:.1f}"
    font-family="{JP}" font-size="8" fill="#666">
    固定条件: 入口位置維持 ／ トリミング室 5帖×2（シャンプー＋トリミング） ／ 犬と猫のゾーニング分離 ／ 保護猫エリア ／ 厨房は概ね既存規模
  </text>
  <text x="{pad["l"]:.1f}" y="{vb_h - 18:.1f}"
    font-family="{MONO}" font-size="7.5" fill="#888">
    PAWS / Saijo Ehime / {n_seats}-seat pattern / design-development drawing
  </text>
</svg>
'''


def build_index(files: dict[int, str]) -> str:
    cards = []
    notes = {
        5: "カウンター3＋テーブル2。ゆとりのあるラウンジ配置。",
        10: "カウンター4＋4人卓＋2人卓。標準稼働のバランス型。",
        15: "カウンター5＋4人卓×2＋2人卓。ピーク時の最大客席。",
    }
    for n, rel in files.items():
        png = rel.replace(".svg", ".png")
        pres = rel.replace(".svg", "-presentation.jpg")
        cards.append(
            f"""
    <article class="card">
      <header>
        <h2>{n}席プラン</h2>
        <p>{notes[n]}</p>
      </header>
      <a class="frame" href="{rel}" target="_blank" rel="noopener">
        <img src="{png}" alt="PAWS {n}席平面図（寸法図）"/>
      </a>
      <a class="frame alt" href="{pres}" target="_blank" rel="noopener">
        <img src="{pres}" alt="PAWS {n}席平面図（プレゼン）"/>
      </a>
      <div class="links">
        <a href="{rel}" download>SVG</a>
        <a href="{png}" download>PNG</a>
        <a href="{pres}" download>JPG</a>
      </div>
    </article>"""
        )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>PAWS 平面図 — 5 / 10 / 15席</title>
<style>
  :root {{
    --bg:#f2eee6; --ink:#1b1915; --muted:#5a544a; --line:#d2caba; --accent:#2c5c4e;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:"Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;
    background:var(--bg); color:var(--ink); }}
  .hero {{
    padding:44px 28px 22px; border-bottom:1px solid var(--line);
    background:
      radial-gradient(ellipse at 0% 0%, #e5dccb 0%, transparent 42%),
      radial-gradient(ellipse at 100% 0%, #d9e3db 0%, transparent 40%),
      var(--bg);
  }}
  .brand {{ color:var(--accent); font-weight:700; font-size:22px; letter-spacing:.08em; }}
  h1 {{ margin:8px 0; font-size:clamp(26px,4vw,40px); }}
  .hero p {{ margin:0; max-width:40rem; color:var(--muted); line-height:1.7; }}
  .tags {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }}
  .tags span {{ border:1px solid var(--line); background:#faf7f0; padding:5px 10px; font-size:12px; }}
  main {{ padding:24px; display:grid; gap:22px; }}
  @media(min-width:1100px){{ main {{ grid-template-columns:repeat(3,1fr); }} }}
  .card {{ background:#faf7f0; border:1px solid var(--line); display:flex; flex-direction:column; }}
  .card header {{ padding:14px 14px 10px; border-bottom:1px solid var(--line); }}
  .card h2 {{ margin:0 0 4px; font-size:18px; }}
  .card header p {{ margin:0; color:var(--muted); font-size:13px; line-height:1.5; }}
  .frame {{ display:block; padding:10px; background:#ebe5da; }}
  .frame.alt {{ border-top:1px solid var(--line); background:#e4ddd0; }}
  .frame img {{ width:100%; height:auto; display:block; background:#f4f0e8; }}
  .links {{ display:flex; border-top:1px solid var(--line); }}
  .links a {{ flex:1; text-align:center; padding:11px; text-decoration:none; color:var(--accent); font-weight:600; font-size:13px; }}
  .links a + a {{ border-left:1px solid var(--line); }}
  footer {{ padding:0 28px 36px; color:var(--muted); font-size:12px; }}
</style>
</head>
<body>
  <header class="hero">
    <div class="brand">PAWS</div>
    <h1>ドッグサロン兼カフェ 平面図</h1>
    <p>愛媛県西条市の計画建物のうち、サロン兼カフェ棟の客席バリエーション（5／10／15席）。
    建築幅を11.5mに抑え、入口・トリミング5帖×2・犬猫分離・保護猫エリア・厨房規模は維持しています。</p>
    <div class="tags">
      <span>横 11,500 mm</span><span>縦 14,560 mm</span><span>入口位置 維持</span>
      <span>トリミング 5帖×2</span><span>犬／猫 分離</span><span>保護猫エリア</span>
      <span>厨房 概ね既存</span>
    </div>
  </header>
  <main>{"".join(cards)}</main>
  <footer>参考添付図を基にした基本設計段階の図面です。実施設計では構造・設備・法規の確認が必要です。</footer>
</body>
</html>
"""


def main():
    files = {}
    for n in (5, 10, 15):
        svg = build_svg(n)
        name = f"paws-cafe-{n}seats.svg"
        (OUT / name).write_text(svg, encoding="utf-8")
        files[n] = name
        print("wrote", name)

    (OUT / "index.html").write_text(build_index(files), encoding="utf-8")

    # 面積検証
    kit = area(0, 0, 3560, 4550)
    sh = area(X[5], Y[3], X[6], Y[3] + 2555)
    print(f"kitchen={kit:.2f}m2 {jo(kit)}")
    print(f"shampoo={sh:.2f}m2 {jo(sh)}")
    print(f"trimming={sh:.2f}m2 {jo(sh)}")
    print(f"footprint {W} x {H}")


if __name__ == "__main__":
    main()
