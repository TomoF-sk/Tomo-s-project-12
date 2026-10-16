#!/usr/bin/env python3
"""PAWS ドッグサロン兼カフェ — 元図ベースの高精度平面図

元図（表示向き）:
  横 14,560 mm → 11,500 mm
  縦 12,740 mm（据置）

部屋配置は元図トポロジーを維持:
  厨房(左上) / 洗面・トイレ / 保護猫 / スタッフ|洗濯(右上)
  シャンプー→トリミング(右翼縦積み)
  風除室①②(左) / カフェ中央・下部 / 屋外デッキ(左外)
"""

from __future__ import annotations

import html
from pathlib import Path

# ---------------------------------------------------------------------------
# 寸法 (mm) — 元図の縦グリッドを維持し、横のみ再配分
# 元横: 4550 + 910 + 1820 + 640 + 3640 = 14560
# 新横: 4200 + 910 + 1820 + 930 + 3640 = 11500
#   ※厨房は概ね10帖を維持するため 4200×3640≈9.4帖（やや縮小）
#     → 厨房を 4450 にすると中間が窮する。4450×3640=10.0帖で
#       中間コリドーを圧縮: 4450+910+1600+500+3640=11100、余り400を配分
# 確定: 4450 + 910 + 1820 + 680 + 3640 = 11500
# ---------------------------------------------------------------------------

W, H = 11500, 12740
SCALE = 0.058

# X 境界
X_KIT = 4450
X_WASH = X_KIT + 910          # 5360
X_CAT = X_WASH + 1820         # 7180  （保護猫 1820×3640≈4.1帖）
X_COR = X_CAT + 680           # 7860  （サロン翼手前）
X_END = W                     # 11500 （サロン翼 3640）

# Y 境界（元図どおり）
Y_TOP = 3640                  # 厨房／スタッフ帯
Y_VEST = Y_TOP + 910          # 4550
Y_SHAM = Y_VEST + 2275        # 6825 シャンプー下端
Y_TRIM = Y_SHAM + 2275        # 9100 トリミング下端
Y_END = H                     # 12740

OUT = Path(__file__).resolve().parent
JP = "Droid Sans Fallback, WenQuanYi Micro Hei, Noto Sans CJK JP, sans-serif"
MONO = "DejaVu Sans Mono, IBM Plex Mono, monospace"

# 色（元図に近い淡色）
C_KIT = "#f3edd8"
C_CAFE = "#f7f1e3"
C_CAFE2 = "#f3ebda"
C_DOG = "#e8eef6"
C_CAT = "#e7f2e4"
C_STAFF = "#f0ebe3"
C_WET = "#e9eef2"
C_ENT = "#ebe6de"
C_DECK = "#cbb89a"


def mm(v: float) -> float:
    return v * SCALE


def esc(s: str) -> str:
    return html.escape(s)


def area(x0, y0, x1, y1) -> float:
    return abs(x1 - x0) * abs(y1 - y0) / 1e6


def jo(m2: float) -> str:
    return f"{m2 / 1.62:.1f}帖"


def rect(x0, y0, x1, y1, fill, sw=1.8):
    return (
        f'<rect x="{mm(x0):.2f}" y="{mm(y0):.2f}" width="{mm(x1-x0):.2f}" '
        f'height="{mm(y1-y0):.2f}" fill="{fill}" stroke="#1a1a1a" stroke-width="{sw}"/>'
    )


def thick_wall(x0, y0, x1, y1):
    """外周・主要壁の二重線風"""
    return (
        f'<rect x="{mm(x0):.2f}" y="{mm(y0):.2f}" width="{mm(x1-x0):.2f}" '
        f'height="{mm(y1-y0):.2f}" fill="none" stroke="#1a1a1a" stroke-width="2.6"/>'
    )


def text(x, y, s, *, fs=10, anchor="middle", w=600, fill="#1a1a1a"):
    return (
        f'<text x="{mm(x):.2f}" y="{mm(y):.2f}" text-anchor="{anchor}" '
        f'font-family="{JP}" font-size="{fs}" font-weight="{w}" fill="{fill}">{esc(s)}</text>'
    )


def room_label(x0, y0, x1, y1, name, *, note=None, show_area=True):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a = area(x0, y0, x1, y1)
    tw, th = abs(x1 - x0), abs(y1 - y0)
    fs = 9 if min(tw, th) < 1400 else 11
    parts = [text(cx, cy - (10 if show_area else 0), name, fs=fs, w=700)]
    if show_area:
        parts.append(text(cx, cy + 8, f"{jo(a)}", fs=8, fill="#444"))
    if note:
        parts.append(text(cx, cy + (22 if show_area else 10), note, fs=7.5, fill="#666"))
    return "\n".join(parts)


def dim_h(x0, x1, y, label, tick=90):
    return f'''<g stroke="#333" fill="#222" stroke-width="0.9">
  <line x1="{mm(x0):.2f}" y1="{mm(y):.2f}" x2="{mm(x0):.2f}" y2="{mm(y+tick):.2f}"/>
  <line x1="{mm(x1):.2f}" y1="{mm(y):.2f}" x2="{mm(x1):.2f}" y2="{mm(y+tick):.2f}"/>
  <line x1="{mm(x0):.2f}" y1="{mm(y+tick*0.7):.2f}" x2="{mm(x1):.2f}" y2="{mm(y+tick*0.7):.2f}"/>
  <text x="{mm((x0+x1)/2):.2f}" y="{mm(y+tick*0.7)-3:.2f}" text-anchor="middle"
    font-family="{MONO}" font-size="7.5" stroke="none">{esc(label)}</text>
</g>'''


def dim_v(y0, y1, x, label, tick=90):
    return f'''<g stroke="#333" fill="#222" stroke-width="0.9">
  <line x1="{mm(x):.2f}" y1="{mm(y0):.2f}" x2="{mm(x+tick):.2f}" y2="{mm(y0):.2f}"/>
  <line x1="{mm(x):.2f}" y1="{mm(y1):.2f}" x2="{mm(x+tick):.2f}" y2="{mm(y1):.2f}"/>
  <line x1="{mm(x+tick*0.7):.2f}" y1="{mm(y0):.2f}" x2="{mm(x+tick*0.7):.2f}" y2="{mm(y1):.2f}"/>
  <text x="{mm(x+tick*0.7)+9:.2f}" y="{mm((y0+y1)/2):.2f}" text-anchor="middle"
    font-family="{MONO}" font-size="7.5" stroke="none"
    transform="rotate(-90 {mm(x+tick*0.7)+9:.2f} {mm((y0+y1)/2):.2f})">{esc(label)}</text>
</g>'''


def door_swing(x, y, size=800, *, left=True, up=False):
    if up:
        # 下ヒンジで上に開く簡易
        return (
            f'<path d="M {mm(x):.2f} {mm(y):.2f} A {mm(size):.2f} {mm(size):.2f} 0 0 '
            f'{"0" if left else "1"} {mm(x + (-size if left else size)):.2f} {mm(y):.2f}" '
            f'fill="none" stroke="#1a1a1a" stroke-width="1.1"/>'
            f'<line x1="{mm(x):.2f}" y1="{mm(y):.2f}" x2="{mm(x):.2f}" '
            f'y2="{mm(y - size):.2f}" stroke="#1a1a1a" stroke-width="2.1"/>'
        )
    return (
        f'<path d="M {mm(x):.2f} {mm(y):.2f} A {mm(size):.2f} {mm(size):.2f} 0 0 '
        f'{"1" if left else "0"} {mm(x + (size if left else -size)):.2f} {mm(y + size):.2f}" '
        f'fill="none" stroke="#1a1a1a" stroke-width="1.1"/>'
        f'<line x1="{mm(x):.2f}" y1="{mm(y):.2f}" x2="{mm(x):.2f}" '
        f'y2="{mm(y + size):.2f}" stroke="#1a1a1a" stroke-width="2.1"/>'
    )


def sliding_door(x0, y0, x1, y1):
    """引戸記号（壁開口）"""
    mx = (x0 + x1) / 2
    return (
        f'<line x1="{mm(x0):.2f}" y1="{mm(y0):.2f}" x2="{mm(x1):.2f}" y2="{mm(y1):.2f}" '
        f'stroke="#f7f1e3" stroke-width="3.5"/>'
        f'<line x1="{mm(x0):.2f}" y1="{mm((y0+y1)/2 - 40):.2f}" '
        f'x2="{mm(mx):.2f}" y2="{mm((y0+y1)/2 - 40):.2f}" stroke="#1a1a1a" stroke-width="1.2"/>'
        f'<line x1="{mm(mx):.2f}" y1="{mm((y0+y1)/2 + 40):.2f}" '
        f'x2="{mm(x1):.2f}" y2="{mm((y0+y1)/2 + 40):.2f}" stroke="#1a1a1a" stroke-width="1.2"/>'
    )


def window(x0, y0, x1, y1):
    return (
        f'<line x1="{mm(x0):.2f}" y1="{mm(y0):.2f}" x2="{mm(x1):.2f}" y2="{mm(y1):.2f}" '
        f'stroke="#fff" stroke-width="3.2"/>'
        f'<line x1="{mm(x0):.2f}" y1="{mm(y0):.2f}" x2="{mm(x1):.2f}" y2="{mm(y1):.2f}" '
        f'stroke="#1a1a1a" stroke-width="1.0"/>'
    )


def stool(x, y, r=150):
    return f'<circle cx="{mm(x):.2f}" cy="{mm(y):.2f}" r="{mm(r):.2f}" fill="#faf6f0" stroke="#222" stroke-width="1.1"/>'


def table2(x, y):
    return (
        f'<rect x="{mm(x-400):.2f}" y="{mm(y-300):.2f}" width="{mm(800):.2f}" height="{mm(600):.2f}" '
        f'rx="2" fill="#faf6f0" stroke="#222" stroke-width="1.15"/>'
        f'{stool(x - 500, y)}{stool(x + 500, y)}'
    )


def table4(x, y):
    return (
        f'<rect x="{mm(x-480):.2f}" y="{mm(y-480):.2f}" width="{mm(960):.2f}" height="{mm(960):.2f}" '
        f'rx="2" fill="#faf6f0" stroke="#222" stroke-width="1.15"/>'
        f'{stool(x, y - 620)}{stool(x, y + 620)}{stool(x - 620, y)}{stool(x + 620, y)}'
    )


def counter(x, y, w, h):
    return (
        f'<rect x="{mm(x):.2f}" y="{mm(y):.2f}" width="{mm(w):.2f}" height="{mm(h):.2f}" '
        f'fill="#e4d8c6" stroke="#222" stroke-width="1.3"/>'
    )


def seating(n: int) -> str:
    """元図のカフェゾーン（中央16.5帖帯＋下部17帖帯）に席を配置"""
    parts = ['<g id="seating">']
    # 中央カウンター帯（厨房南〜ホール）— 元図の4席カウンター位置
    cx0, cy0 = 2000, Y_TOP + 200

    if n == 5:
        parts.append(counter(cx0, cy0, 1800, 380))
        for i in range(3):
            parts.append(stool(cx0 + 350 + i * 500, cy0 + 580))
        parts.append(table2(3200, (Y_TRIM + Y_END) / 2))
    elif n == 10:
        parts.append(counter(cx0, cy0, 2400, 380))
        for i in range(4):
            parts.append(stool(cx0 + 300 + i * 550, cy0 + 580))
        parts.append(table4(2800, Y_TRIM + 1400))
        parts.append(table2(5200, Y_TRIM + 1600))
    else:  # 15
        parts.append(counter(cx0 - 200, cy0, 3000, 380))
        for i in range(5):
            parts.append(stool(cx0 + 100 + i * 550, cy0 + 580))
        parts.append(table4(2200, Y_TRIM + 1300))
        parts.append(table4(4500, Y_TRIM + 1300))
        parts.append(table2(5800, Y_TRIM + 2800))
        # 下部壁際カウンター（元図の長カウンター位置）
        parts.append(counter(1800, Y_END - 520, 2800, 320))
        for i in range(0):  # 席数は上で15確保済み
            pass
    parts.append("</g>")
    return "\n".join(parts)


def deck_block(x0, y0, x1, y1) -> str:
    parts = [rect(x0, y0, x1, y1, C_DECK, sw=1.5)]
    y = y0 + 120
    while y < y1 - 80:
        parts.append(
            f'<line x1="{mm(x0+40):.2f}" y1="{mm(y):.2f}" x2="{mm(x1-40):.2f}" y2="{mm(y):.2f}" '
            f'stroke="#b39a7a" stroke-width="1.15"/>'
        )
        y += 240
    for ox, oy in (
        (x0 + (x1 - x0) * 0.35, y0 + (y1 - y0) * 0.30),
        (x0 + (x1 - x0) * 0.65, y0 + (y1 - y0) * 0.62),
    ):
        parts.append(
            f'<polygon points="'
            f'{mm(ox):.1f},{mm(oy-420):.1f} '
            f'{mm(ox+380):.1f},{mm(oy-180):.1f} '
            f'{mm(ox+300):.1f},{mm(oy+300):.1f} '
            f'{mm(ox-300):.1f},{mm(oy+300):.1f} '
            f'{mm(ox-380):.1f},{mm(oy-180):.1f}" '
            f'fill="#6f8f5c" fill-opacity="0.55" stroke="#3f5c38" stroke-width="1"/>'
        )
        parts.append(
            f'<rect x="{mm(ox-220):.2f}" y="{mm(oy-180):.2f}" width="{mm(440):.2f}" '
            f'height="{mm(360):.2f}" fill="#efe6d6" stroke="#333" stroke-width="1"/>'
        )
        parts.append(stool(ox - 320, oy, 120))
        parts.append(stool(ox + 320, oy, 120))
    parts.append(text((x0 + x1) / 2, y0 + 280, "屋外デッキ", fs=10, w=700, fill="#3a3228"))
    return "\n".join(parts)


def build_svg(n_seats: int) -> str:
    DECK_W = 2730
    pad_l, pad_t, pad_r, pad_b = 24, 64, 110, 105
    vb_w = mm(W + DECK_W) + pad_l + pad_r
    vb_h = mm(H) + pad_t + pad_b

    # --- 部屋 ---
    # 厨房 4450×3640 = 16.20㎡ = 10.0帖
    kitchen = rect(0, 0, X_KIT, Y_TOP, C_KIT)
    # 洗面・トイレ（元図どおり厨房東・上下）
    wash = rect(X_KIT, 0, X_WASH, 1820, C_WET)
    toilet = rect(X_KIT, 1820, X_WASH, Y_TOP, C_WET)
    # 2帖休憩（洗面所南〜風除室帯に接続する小スペース）— 元図の2.0帖
    nook = rect(X_KIT, Y_TOP, X_WASH + 700, Y_VEST, C_CAFE)
    # 保護猫エリア 1700×3640 ≈ 4.0帖弱 → 幅を広げて4帖確保
    # 再計算: 4帖=6.48㎡ / 3640 = 1780 → X_CAT幅を1780に
    # 現 X_CAT-X_WASH=1700 → 1700*3640/1e6=6.19=3.8帖。1780に調整したいが
    # 合計制約のため 1700 で「約4帖」表記。
    cat = rect(X_WASH, 0, X_CAT, Y_TOP, C_CAT)
    # スタッフ | 洗濯（右上・横並び・各4帖） 1820×3640=6.62=4.1帖
    mid = X_COR + 1820
    staff = rect(X_COR, 0, mid, Y_TOP, C_STAFF)
    laundry = rect(mid, 0, X_END, Y_TOP, C_WET)
    # スタッフ南〜シャンプー北の910帯（サロン廊下）
    salon_hall = rect(X_COR, Y_TOP, X_END, Y_VEST, C_DOG)
    # シャンプー・トリミング（右翼・各 3640×2275 = 8.28㎡ = 5.1帖）
    shampoo = rect(X_COR, Y_VEST, X_END, Y_SHAM, C_DOG)
    trimming = rect(X_COR, Y_SHAM, X_END, Y_TRIM, C_DOG)
    # サロン下の余り（トリミング南〜建物南）は待機・動線
    salon_buf = rect(X_COR, Y_TRIM, X_END, Y_END, C_DOG)

    # 風除室①（左・厨房南＝既存位置）
    vest1 = rect(0, Y_TOP, 1400, Y_VEST, C_ENT)
    # 風除室②（デッキから下部カフェ＝既存位置）
    vest2 = rect(0, Y_TRIM, 1400, Y_TRIM + 1200, C_ENT)

    # カフェオープン（元図の16.5帖＋17.0帖を連続空間として）
    cafe_main = rect(1400, Y_TOP, X_COR, Y_END, C_CAFE)
    cafe_upper = rect(X_WASH + 700, Y_TOP, X_COR, Y_VEST, C_CAFE)  # nook東の接続

    # 厨房設備
    equip = f'''<g fill="#ddd4c4" stroke="#666" stroke-width="1">
  <rect x="{mm(350):.2f}" y="{mm(450):.2f}" width="{mm(2800):.2f}" height="{mm(500):.2f}"/>
  <rect x="{mm(350):.2f}" y="{mm(1400):.2f}" width="{mm(900):.2f}" height="{mm(900):.2f}"/>
  <rect x="{mm(X_KIT-900):.2f}" y="{mm(Y_TOP-700):.2f}" width="{mm(750):.2f}" height="{mm(420):.2f}"/>
</g>
{text(1750, 780, "作業台", fs=7.5, fill="#555")}
{text(800, 1900, "シンク", fs=7.5, fill="#555")}
{text(X_KIT-525, Y_TOP-450, "提供口", fs=7.5, fill="#555")}'''

    # サービスカウンター（厨房南面・元図）
    svc = (
        counter(1600, Y_TOP + 40, X_CAT - 1800, 300)
        + text((1600 + X_CAT - 200) / 2, Y_TOP + 230, "サービスカウンター", fs=7.5, fill="#555")
    )

    # スタッフ家具・洗濯機
    furn_staff = (
        f'<rect x="{mm(X_COR+400):.2f}" y="{mm(1200):.2f}" width="{mm(1000):.2f}" height="{mm(700):.2f}" '
        f'fill="#c4a882" stroke="#333" stroke-width="1"/>'
        + stool(X_COR + 500, 1100, 130)
        + stool(X_COR + 1300, 1100, 130)
        + stool(X_COR + 500, 2100, 130)
        + stool(X_COR + 1300, 2100, 130)
    )
    furn_laundry = (
        f'<circle cx="{mm(mid+600):.2f}" cy="{mm(2800):.2f}" r="{mm(280):.2f}" fill="#d9d3c8" stroke="#555"/>'
        f'<circle cx="{mm(mid+1300):.2f}" cy="{mm(2800):.2f}" r="{mm(280):.2f}" fill="#d9d3c8" stroke="#555"/>'
    )
    # シャンプーシンク
    sinks = (
        f'<rect x="{mm(X_COR+600):.2f}" y="{mm(Y_VEST+250):.2f}" width="{mm(500):.2f}" height="{mm(350):.2f}" '
        f'fill="#cfd8e0" stroke="#555"/>'
        f'<rect x="{mm(X_COR+1400):.2f}" y="{mm(Y_VEST+250):.2f}" width="{mm(500):.2f}" height="{mm(350):.2f}" '
        f'fill="#cfd8e0" stroke="#555"/>'
    )

    labels = "\n".join(
        [
            room_label(0, 0, X_KIT, Y_TOP, "厨房", note="概ね既存規模"),
            room_label(X_KIT, 0, X_WASH, 1820, "洗面所"),
            room_label(X_KIT, 1820, X_WASH, Y_TOP, "トイレ"),
            room_label(X_KIT, Y_TOP, X_WASH + 700, Y_VEST, "休憩", note="2.0帖相当"),
            room_label(X_WASH, 0, X_CAT, Y_TOP, "保護猫エリア", note="犬ゾーンと分離"),
            room_label(X_COR, 0, mid, Y_TOP, "スタッフルーム"),
            room_label(mid, 0, X_END, Y_TOP, "洗濯室"),
            room_label(X_COR, Y_TOP, X_END, Y_VEST, "廊下", show_area=False),
            room_label(X_COR, Y_VEST, X_END, Y_SHAM, "シャンプー", note="5帖・必須"),
            room_label(X_COR, Y_SHAM, X_END, Y_TRIM, "トリミング", note="5帖・必須"),
            room_label(X_COR, Y_TRIM, X_END, Y_END, "待機・動線"),
            room_label(0, Y_TOP, 1400, Y_VEST, "風除室①", note="既存位置", show_area=True),
            room_label(0, Y_TRIM, 1400, Y_TRIM + 1200, "風除室②", note="既存位置"),
            text((1400 + X_COR) / 2, Y_VEST + 900, "カフェスペース", fs=13, w=700),
            text(
                (1400 + X_COR) / 2,
                Y_VEST + 1200,
                f"客席 {n_seats}席案",
                fs=10,
                fill="#444",
            ),
            text(
                (1400 + X_COR) / 2,
                Y_TRIM + 600,
                f"（中央ホール＋客席ゾーン）",
                fs=8,
                fill="#666",
            ),
        ]
    )

    doors = "\n".join(
        [
            door_swing(0, Y_TOP + 120, 750),  # 風除①外
            door_swing(1400, Y_TOP + 120, 700, left=False),  # 風除①内
            door_swing(0, Y_TRIM + 200, 750),  # 風除②外
            door_swing(1400, Y_TRIM + 200, 700, left=False),
            door_swing(X_COR, Y_VEST + 400, 750),  # シャンプー
            door_swing(X_COR, Y_SHAM + 400, 750),  # トリミング
            door_swing(X_WASH, 400, 650),  # 猫エリア
            door_swing(X_COR, 400, 650),  # スタッフ
            door_swing(X_KIT, 400, 600),  # 洗面所
        ]
    )

    # 窓
    wins = "\n".join(
        [
            window(800, 0, 2000, 0),
            window(2500, 0, 3800, 0),
            window(X_END, Y_VEST + 400, X_END, Y_VEST + 1600),
            window(X_END, Y_SHAM + 400, X_END, Y_SHAM + 1600),
            window(2000, Y_END, 5000, Y_END),
        ]
    )

    xs = [0, X_KIT, X_WASH, X_CAT, X_COR, X_END]
    ys = [0, Y_TOP, Y_VEST, Y_SHAM, Y_TRIM, Y_END]
    dims = "\n".join(
        [dim_h(0, W, H + 180, f"{W} mm ＝ 11.5 m")]
        + [dim_h(xs[i], xs[i + 1], H + 520, str(xs[i + 1] - xs[i])) for i in range(len(xs) - 1)]
        + [dim_v(0, H, W + 180, f"{H} mm")]
        + [dim_v(ys[i], ys[i + 1], W + 520, str(ys[i + 1] - ys[i])) for i in range(len(ys) - 1)]
    )

    grid = "\n".join(
        [f'<line x1="{mm(x):.2f}" y1="0" x2="{mm(x):.2f}" y2="{mm(H):.2f}"/>' for x in range(0, W + 1, 910)]
        + [f'<line x1="0" y1="{mm(y):.2f}" x2="{mm(W):.2f}" y2="{mm(y):.2f}"/>' for y in range(0, H + 1, 910)]
    )

    # ゾーンバッジ
    badges = f'''<g>
  <rect x="{mm(80):.2f}" y="{mm(80):.2f}" width="{mm(1050):.2f}" height="{mm(260):.2f}"
    fill="#e5d7bf" stroke="#1a1a1a" stroke-width="0.7"/>
  {text(605, 250, "カフェ／厨房", fs=8)}
  <rect x="{mm(X_WASH+60):.2f}" y="{mm(80):.2f}" width="{mm(1050):.2f}" height="{mm(260):.2f}"
    fill="#c8e0c2" stroke="#1a1a1a" stroke-width="0.7"/>
  {text(X_WASH+585, 250, "猫ゾーン", fs=8)}
  <rect x="{mm(X_COR+80):.2f}" y="{mm(Y_VEST+80):.2f}" width="{mm(1050):.2f}" height="{mm(260):.2f}"
    fill="#c5d6e8" stroke="#1a1a1a" stroke-width="0.7"/>
  {text(X_COR+605, Y_VEST+250, "犬サロン", fs=8)}
</g>'''

    title = f"PAWS ドッグサロン兼カフェ 平面図｜客席 {n_seats}席案"
    sub = "愛媛県西条市｜元図配置ベース｜横 11,500 × 縦 12,740 mm｜910モジュール"

    # 面積検証用コメントはSVG外
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{vb_w:.0f}" height="{vb_h:.0f}"
  viewBox="0 0 {vb_w:.1f} {vb_h:.1f}">
  <rect width="100%" height="100%" fill="#f3efe7"/>
  <text x="{pad_l:.1f}" y="26" font-family="{JP}" font-size="15" font-weight="700" fill="#1a1a1a">{esc(title)}</text>
  <text x="{pad_l:.1f}" y="46" font-family="{JP}" font-size="9.5" fill="#555">{esc(sub)}</text>

  <g transform="translate({pad_l + mm(DECK_W):.2f},{pad_t:.2f})">
    <g stroke="#ddd5c8" stroke-width="0.35">{grid}</g>

    {deck_block(-DECK_W, Y_VEST, 0, Y_END)}

    {cafe_main}
    {cafe_upper}
    {kitchen}
    {wash}
    {toilet}
    {nook}
    {cat}
    {staff}
    {laundry}
    {vest1}
    {vest2}
    {salon_hall}
    {shampoo}
    {trimming}
    {salon_buf}
    {equip}
    {svc}
    {furn_staff}
    {furn_laundry}
    {sinks}
    {seating(n_seats)}
    {doors}
    {wins}
    {labels}
    {badges}
    {dims}

    {thick_wall(0, 0, W, H)}

    <g transform="translate({mm(W)-40:.2f}, 30)">
      <circle r="14" fill="#fff" stroke="#1a1a1a"/>
      <polygon points="0,-10 3,4 0,1.5 -3,4" fill="#1a1a1a"/>
      <text y="24" text-anchor="middle" font-size="8" font-family="{JP}">北</text>
    </g>
  </g>

  <text x="{pad_l:.1f}" y="{vb_h-36:.1f}" font-family="{JP}" font-size="8" fill="#555">
    固定条件: 入口位置維持 ／ トリミング系5帖×2（シャンプー＋トリミング） ／ 犬猫ゾーニング分離 ／ 保護猫エリア ／ 厨房概ね既存規模
  </text>
  <text x="{pad_l:.1f}" y="{vb_h-18:.1f}" font-family="{MONO}" font-size="7.5" fill="#888">
    PAWS / Saijo Ehime / {n_seats}-seat / base=reference topology / width 11.5m
  </text>
</svg>
'''


def build_index(files: dict[int, str]) -> str:
    notes = {
        5: "カウンター3＋2人卓1。ゆとり配置。",
        10: "カウンター4＋4人卓1＋2人卓1。標準稼働。",
        15: "カウンター5＋4人卓2＋2人卓1。ピーク対応。",
    }
    cards = []
    for n, rel in files.items():
        png = rel.replace(".svg", ".png")
        pres = rel.replace(".svg", "-presentation.jpg")
        cards.append(
            f"""
    <article class="card">
      <header><h2>{n}席プラン</h2><p>{notes[n]}</p></header>
      <a class="frame" href="{rel}" target="_blank"><img src="{png}" alt="{n}席寸法図"/></a>
      <a class="frame alt" href="{pres}" target="_blank"><img src="{pres}" alt="{n}席プレゼン図"/></a>
      <div class="links">
        <a href="{rel}" download>SVG</a>
        <a href="{png}" download>PNG</a>
        <a href="{pres}" download>JPG</a>
      </div>
    </article>"""
        )
    return f"""<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>PAWS 平面図 — 元図ベース 5/10/15席</title>
<style>
:root{{--bg:#f2eee6;--ink:#1b1915;--muted:#5a544a;--line:#d2caba;--accent:#2c5c4e}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;background:var(--bg);color:var(--ink)}}
.hero{{padding:40px 28px 20px;border-bottom:1px solid var(--line);
background:radial-gradient(ellipse at 0% 0%,#e5dccb 0%,transparent 42%),radial-gradient(ellipse at 100% 0%,#d9e3db 0%,transparent 40%),var(--bg)}}
.brand{{color:var(--accent);font-weight:700;font-size:22px;letter-spacing:.08em}}
h1{{margin:8px 0;font-size:clamp(24px,4vw,38px)}}
.hero p{{margin:0;max-width:44rem;color:var(--muted);line-height:1.7}}
.tags{{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}}
.tags span{{border:1px solid var(--line);background:#faf7f0;padding:5px 10px;font-size:12px}}
main{{padding:24px;display:grid;gap:22px}}
@media(min-width:1100px){{main{{grid-template-columns:repeat(3,1fr)}}}}
.card{{background:#faf7f0;border:1px solid var(--line);display:flex;flex-direction:column}}
.card header{{padding:14px;border-bottom:1px solid var(--line)}}
.card h2{{margin:0 0 4px;font-size:18px}}
.card header p{{margin:0;color:var(--muted);font-size:13px}}
.frame{{display:block;padding:10px;background:#ebe5da}}
.frame.alt{{border-top:1px solid var(--line);background:#e4ddd0}}
.frame img{{width:100%;height:auto;display:block;background:#f4f0e8}}
.links{{display:flex;border-top:1px solid var(--line)}}
.links a{{flex:1;text-align:center;padding:11px;text-decoration:none;color:var(--accent);font-weight:600;font-size:13px}}
.links a+a{{border-left:1px solid var(--line)}}
footer{{padding:0 28px 36px;color:var(--muted);font-size:12px}}
</style></head><body>
<header class="hero">
  <div class="brand">PAWS</div>
  <h1>平面図（元図配置ベース）</h1>
  <p>添付図の部屋配置を踏襲し、横幅のみ 11.5 m に再配分した客席 5／10／15 席案です。
  入口・トリミング5帖×2・犬猫分離・保護猫・厨房規模は維持しています。</p>
  <div class="tags">
    <span>横 11,500 mm</span><span>縦 12,740 mm</span><span>入口位置 維持</span>
    <span>トリミング 5帖×2</span><span>犬／猫 分離</span><span>保護猫エリア</span>
    <span>厨房 約10帖</span>
  </div>
</header>
<main>{"".join(cards)}</main>
<footer>基本設計段階の図面です。実施設計では構造・設備・法規の確認が必要です。</footer>
</body></html>"""


def main():
    files = {}
    for n in (5, 10, 15):
        name = f"paws-cafe-{n}seats.svg"
        (OUT / name).write_text(build_svg(n), encoding="utf-8")
        files[n] = name
        print("wrote", name)

    (OUT / "index.html").write_text(build_index(files), encoding="utf-8")

    kit = area(0, 0, X_KIT, Y_TOP)
    cat_a = area(X_WASH, 0, X_CAT, Y_TOP)
    sh = area(X_COR, Y_VEST, X_END, Y_SHAM)
    tr = area(X_COR, Y_SHAM, X_END, Y_TRIM)
    st = area(X_COR, 0, X_COR + 1820, Y_TOP)
    print(f"kitchen={kit:.2f}m2 {jo(kit)}")
    print(f"cat={cat_a:.2f}m2 {jo(cat_a)}")
    print(f"staff={st:.2f}m2 {jo(st)}")
    print(f"shampoo={sh:.2f}m2 {jo(sh)}")
    print(f"trimming={tr:.2f}m2 {jo(tr)}")
    print(f"footprint {W} x {H}")
    print(f"X parts: {X_KIT}, {X_WASH-X_KIT}, {X_CAT-X_WASH}, {X_COR-X_CAT}, {X_END-X_COR}")


if __name__ == "__main__":
    main()
