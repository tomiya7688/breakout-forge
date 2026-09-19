# Breakout Forge

Breakout Forge は、普通のブロック崩しとして遊べるだけでなく、画像・多層破壊・外部JSON・Python MODを使って独自ステージを作れる小型ブロック崩し基盤です。

- Python + pygame
- Windows配布は PyInstaller `--onedir`
- PNG / JPEG / WebP の画像ステージ
- 画像を物理分割せず `source_rect` で論理分割
- 上層を壊すと下層が見える多層画像
- common / user / stage の設定継承
- 外部 Python MOD とイベントAPI
- CI / Data Check / Build Check

内部設計は [DESIGN.md](DESIGN.md)、レイヤー責務は [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) を参照してください。

## すぐ遊ぶ

### Windows配布版

配布ZIPを展開し、`BreakoutForge.exe` を実行します。

```text
BreakoutForge/
├─ BreakoutForge.exe
├─ _internal/
├─ config/
├─ assets/
├─ stages/
├─ mods/
└─ userdata/
```

`config/`, `assets/`, `stages/`, `mods/`, `userdata/` は `_internal/` ではなくexe隣に置きます。これらはユーザーが編集・追加できる外部データです。

標準ステージを遊ぶ:

```bat
BreakoutForge.exe
```

同梱ステージを指定する:

```bat
BreakoutForge.exe --stage sample
BreakoutForge.exe --stage layered_sample
BreakoutForge.exe --stage standard_sample
```

`--stage sample` は `stages/sample/stage.json` を読み込みます。

stage.jsonを直接指定することもできます。

```bat
BreakoutForge.exe --stage stages\sample\stage.json
```

### ソースから起動

Python 3.12 以降が必要です。

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate

# Linux/macOS
# source .venv/bin/activate

python -m pip install -e ".[dev]"
python -m breakout_forge
```

ステージ指定:

```bash
python -m breakout_forge --stage sample
python -m breakout_forge --stage layered_sample
```

## 基本操作

| 操作 | キー |
|---|---|
| Paddle 左移動 | ← / A |
| Paddle 右移動 | → / D |
| ゲーム開始 | Space / Enter |
| CLEAR / GAME OVER後のリスタート | R |
| 終了 | ウィンドウを閉じる |

## 外部ディレクトリ

```text
<base>/
├─ config/
│  ├─ common.json
│  └─ user.example.json
├─ assets/
├─ stages/
│  ├─ standard_sample/
│  ├─ sample/
│  └─ layered_sample/
├─ mods/
│  └─ example_mod/
└─ userdata/
   └─ settings.json
```

ソース実行ではrepository root、PyInstaller `--onedir` では `BreakoutForge.exe` のあるディレクトリが `<base>` です。current working directory には依存しません。

## 設定の優先順位

設定は次の順に再帰マージされます。

```text
config/common.json
       ↓
userdata/settings.json
       ↓
stages/<stage>/stage.json
```

下にある設定ほど優先されます。未指定キーは上位の値を引き継ぎます。

### config/common.json

全ステージ共通の既定値です。

主な設定:

- `display.width / height / fps / title`
- `gameplay.ball_speed`
- `gameplay.ball_size`
- `gameplay.ball_initial_direction`
- `gameplay.paddle_speed`
- `gameplay.paddle_size`
- `stage_size.columns / rows`
- `standard_stage.*`
- `break_image.*`
- `playfield.*`
- `appearance.*`

### userdata/settings.json

ユーザー全体の任意上書きです。なくても起動できます。

例:

```json
{
  "format_version": 1,
  "settings": {
    "display": {
      "width": 1280,
      "height": 720
    }
  }
}
```

`config/user.example.json` をコピーして使えます。

## ステージを追加する

新しいフォルダを `stages/` の下に作ります。

```text
stages/
└─ my_stage/
   └─ stage.json
```

最小の標準ステージ:

```json
{
  "format_version": 1,
  "id": "my_stage",
  "name": "My Stage"
}
```

このように画像Layerがなければ、`stage_size` と `standard_stage` の設定から普通のブロックを生成します。

起動:

```bat
BreakoutForge.exe --stage my_stage
```

実例: [stages/standard_sample/stage.json](stages/standard_sample/stage.json)

## 標準ステージを調整する

例:

```json
{
  "format_version": 1,
  "id": "hard_blocks",
  "name": "Hard Blocks",
  "settings": {
    "stage_size": {
      "columns": 12,
      "rows": 8
    },
    "gameplay": {
      "ball_speed": 420
    },
    "standard_stage": {
      "block_hp": 2,
      "score_per_layer": 200
    }
  }
}
```

## 画像を崩すステージ

画像と `stage.json` を同じステージディレクトリへ置きます。

```text
stages/
└─ my_image_stage/
   ├─ stage.json
   └─ main.png
```

例:

```json
{
  "format_version": 1,
  "id": "my_image_stage",
  "name": "My Image Stage",
  "settings": {
    "break_image": {
      "split": {
        "columns": 24,
        "rows": 18
      },
      "load_mode": "keep_background"
    }
  },
  "layers": [
    {
      "id": "main",
      "image": "main.png",
      "hp": 1,
      "collidable": true,
      "destructible": true,
      "visible": true
    }
  ]
}
```

対応画像形式:

- PNG
- JPEG / JPG
- WebP

画像ファイル自体を数百個へ分割して保存する必要はありません。元画像1枚を読み、`break_image.split` に従って論理分割します。

実例: [stages/sample/stage.json](stages/sample/stage.json)

## stage_size と break_image.split の違い

この2つは別物です。

### stage_size

ステージ全体の論理マス数です。

```json
"stage_size": {
  "columns": 100,
  "rows": 60
}
```

### break_image.split

崩す対象画像を何分割するかです。

```json
"break_image": {
  "split": {
    "columns": 40,
    "rows": 30
  }
}
```

`stage_size = 100x60` でも `break_image.split = 40x30` にできます。

また、どちらも `display.width / height` とは独立です。

## 画像背景の扱い

### keep_background

```json
"load_mode": "keep_background"
```

画像全体をそのまま破壊対象にします。背景部分もタイルとして残ります。

### remove_background

```json
"load_mode": "remove_background"
```

画像四隅から連結している背景色を透過化します。前景がまったく残らないタイルは最初から空Cellになります。

色差の許容値:

```json
"background_tolerance": 16
```

0〜255で指定できます。単純な背景除去なので、複雑な写真背景をAIセグメンテーションする機能ではありません。

## 多層画像ステージ

`layers` は **下 → 上** の順に書きます。

```json
{
  "format_version": 1,
  "id": "layered",
  "name": "Layered",
  "settings": {
    "break_image": {
      "split": {
        "columns": 20,
        "rows": 12
      },
      "load_mode": "keep_background"
    }
  },
  "layers": [
    {
      "id": "bottom",
      "image": "bottom.png",
      "hp": 1
    },
    {
      "id": "top",
      "image": "top.png",
      "hp": 2
    }
  ]
}
```

この例では `top` を2回叩いて破壊すると、そのCellだけ `bottom` が見えるようになります。

実例: [stages/layered_sample/stage.json](stages/layered_sample/stage.json)

複数画像は解像度が異なっても構いませんが、現在は縦横比を揃える必要があります。

例:

- 800x600 + 1600x1200 → OK
- 800x600 + 800x800 → エラー

## Layer設定

各Layerで使える主な項目:

| 項目 | 意味 |
|---|---|
| `id` | Layer ID |
| `image` | ステージディレクトリ基準の画像パス |
| `hp` | このLayerを壊すのに必要なヒット数 |
| `collidable` | Ballとの衝突対象にするか |
| `destructible` | ダメージで破壊可能か |
| `visible` | 描画するか |

既定値は `hp=1`, `collidable=true`, `destructible=true`, `visible=true` です。

## playfield fit

画像ステージの表示方法:

- `contain`: アスペクト比を維持して全体を収める
- `cover`: アスペクト比を維持して領域を覆う
- `stretch`: 領域へ引き伸ばす

`config/common.json` の既定値は `contain` です。

## MODを追加する

MODは次の構成です。

```text
mods/
└─ my_mod/
   ├─ mod.json
   └─ main.py
```

`mod.json`:

```json
{
  "format_version": 1,
  "id": "my_mod",
  "name": "My MOD",
  "version": "0.1.0",
  "entry": "main.py"
}
```

`main.py`:

```python
def setup(api):
    api.subscribe("on_layer_destroyed", on_layer_destroyed)


def on_layer_destroyed(event):
    print(event.data)
```

実例:

- [mods/example_mod/mod.json](mods/example_mod/mod.json)
- [mods/example_mod/main.py](mods/example_mod/main.py)

現在の公開イベント:

- `on_game_start`
- `on_game_update`
- `on_stage_loaded`
- `on_ball_hit_paddle`
- `on_block_hit`
- `on_layer_destroyed`
- `on_cell_destroyed`
- `on_stage_cleared`
- `on_game_over`

### MODのセキュリティ

Python MODはサンドボックス化されません。

MODのPythonコードは、ゲーム本体と同じプロセス権限でファイルアクセス等を行える可能性があります。**信頼できるMODだけを導入してください。**

ユーザーが追加したMODや画像について、Breakout Forge本体はそれらの権利・安全性を保証しません。

## 同梱サンプル

| サンプル | 内容 |
|---|---|
| [stages/standard_sample](stages/standard_sample) | 画像なし標準ブロック |
| [stages/sample](stages/sample) | 単一画像ステージ |
| [stages/layered_sample](stages/layered_sample) | 2層画像、上層HP=2 |
| [mods/example_mod](mods/example_mod) | 公開イベント購読例 |

## よくあるエラー

### common settings not found

`config/common.json` がexeまたはrepository rootから見える位置にあるか確認してください。

### stage definition not found

`--stage my_stage` の場合は次が必要です。

```text
stages/my_stage/stage.json
```

### stage image not found / failed to load image

- `image` のファイル名を確認
- 画像をstage.jsonと同じステージディレクトリ以下へ置く
- PNG / JPEG / WebP を使用
- 壊れた画像ファイルでないか確認

画像パスに `../` を使ってステージディレクトリ外を参照することはできません。

### break_image.split exceeds source image pixel dimensions

分割数が画像のピクセル数を超えています。`columns` と `rows` を小さくしてください。

### layered image assets ... aspect ratio

多層画像の縦横比が一致していません。

### MOD load failed

`mod.json` の `entry`、Python構文、`setup(api)` を確認してください。MODの失敗は可能な限り本体や他MODを止めずログへ記録します。

## 開発者向けテスト

```bash
python -m pip install -e ".[dev]"
pytest
python scripts/validate_data.py --project-root .
python -m breakout_forge --smoke-test
```

## Windows onedir ビルド

```bat
python -m pip install -e ".[dev]"
build.bat
```

出力:

```text
dist/
└─ BreakoutForge/
   ├─ BreakoutForge.exe
   ├─ _internal/
   ├─ config/
   ├─ assets/
   ├─ stages/
   ├─ mods/
   └─ userdata/
```

`--onefile` は使用しません。

## CI

GitHub Actionsは3系統です。

- **CI**: compileall / Ruff / pytest / source smoke
- **Data Check**: stage / image / MOD データ検証
- **Build Check**: Windows onedir build / packaged smoke / Artifact

Windows Artifact名は `breakout-forge-windows-onedir` です。

## ライセンス

Breakout Forge本体は [MIT License](LICENSE) です。

公式repositoryへ含めるサンプル素材・依存ライブラリの最終監査はv1.0.0リリース前チェックで行います。
