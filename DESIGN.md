# Breakout Forge 設計書

## 1. 概要

Breakout Forge は、シンプルなブロック崩しを遊ぶためのゲーム本体であると同時に、画像・レイヤー・外部定義・MOD を利用して様々なブロック崩しを作れる小型ゲーム基盤を目指す。

最初の実装は Python + pygame を基本とし、Windows 向け配布は PyInstaller の `--onedir` 形式を前提とする。

本プロジェクトでは、次の3段階の拡張方法を提供する。

1. そのまま遊ぶ標準ブロック崩し
2. 画像・JSON 等の外部データだけで作れるカスタムステージ
3. Python MOD によるゲームロジック拡張

---

## 2. 目的

### 2.1 最小目標

- パドル、ボール、ブロックを持つ基本的なブロック崩しが遊べる
- Windows で配布可能なビルドを生成できる
- 好きな画像を読み込み、画像をタイル状の破壊対象として遊べる
- 1つのセルに複数レイヤーを持たせ、上から順に段階的に破壊できる
- 外部ステージ定義を追加するだけで新しいステージを作れる
- MOD を追加してゲーム挙動を拡張できる

### 2.2 将来目標

- GUI ステージエディタ
- MOD 管理画面
- ステージパック
- 複数ボール、アイテム、特殊ブロック
- サウンド、演出、パーティクル
- 他 OS 向けビルド
- より汎用的なゲームテンプレート化

---

## 3. 設計方針

### 3.1 シンプルさを優先する

ゲーム本体は小さく保ち、データと拡張ロジックを外部化する。

### 3.2 ゲーム本体とコンテンツを分離する

標準ステージ、画像、MOD、ユーザー設定は実行ファイルへ埋め込みすぎない。

### 3.3 画像ブロックと通常ブロックを同じ仕組みで扱う

画像専用のゲームロジックを増やすのではなく、セルへ画像領域を割り当てることで通常ブロックと統一する。

### 3.4 耐久値と多層構造を分離する

- `hp`: 同じレイヤーを何回叩けば壊れるか
- `layers`: 壊れた後に何が現れるか

これにより、3回叩く石壁と、3種類の画像が順番に現れるブロックを別々に表現できる。

### 3.5 MOD API はゲーム内部実装への直接依存を減らす

MOD から pygame の内部オブジェクトや private 実装へ直接依存させず、公開 API とイベントを通して拡張する。

### 3.6 調整値は原則として外部データへ出す

ゲームバランス、表示寸法、盤面構成、画像分割など、利用者・作者が変更したくなる可能性が高い値は原則としてプログラムへハードコードしない。

標準値は `config/common.json` に置き、ステージ固有値は各 `stages/<stage>/stage.json` に置く。

解決規則は次の通り。

1. `common.json` を読み込む
2. `stage.json` に同名設定が存在する場合のみ上書きする
3. `stage.json` に設定がなければ common 値をそのまま使用する

プログラム内定数は、ファイル読込不能時の起動保護など最低限の安全値に限定し、通常のゲーム調整には使用しない。

---

## 4. 想定技術

| 項目 | 採用案 |
|---|---|
| 言語 | Python 3.12 以降を第一候補 |
| 描画 / 入力 | pygame |
| 設定 | JSON |
| 画像 | PNG / JPEG / WebP（pygame が扱える範囲） |
| ビルド | PyInstaller |
| 配布形式 | `--onedir` |
| テスト | pytest |
| CI | GitHub Actions |

Python の最低対応バージョンは、依存ライブラリと PyInstaller の対応状況を確認して正式決定する。

---

## 5. ディレクトリ構成

初期案は次の通り。

```text
breakout-forge/
├─ src/
│  └─ breakout_forge/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ app.py
│     ├─ game/
│     ├─ stage/
│     ├─ modding/
│     ├─ assets/
│     └─ config/
├─ assets/
├─ config/
│  └─ common.json
├─ stages/
│  └─ sample/
│     └─ stage.json
├─ mods/
├─ userdata/
├─ tests/
├─ scripts/
├─ .github/
│  └─ workflows/
├─ pyproject.toml
├─ build.bat
├─ build.sh
├─ README.md
└─ DESIGN.md
```

`userdata/` は実行時生成を基本とし、Git 管理対象外にする。

外部データの基準ディレクトリは、ソース実行時はパッケージ位置からリポジトリルートを解決し、PyInstaller `--onedir` 実行時は実行ファイルのあるディレクトリを使用する。プロセスの current working directory には依存しない。

---

## 6. ゲームモデル

### 6.1 Game

ゲーム全体の状態遷移を管理する。ゲーム開始 / 終了、更新、描画、クリア判定、ゲームオーバー判定、イベント発火を担当するが、ブロックや画像の詳細処理は抱え込まない。

### 6.2 Paddle

- プレイヤー入力による左右移動
- 移動範囲制限
- ボールとの衝突領域提供
- 速度と大きさは解決済みステージ設定から受け取る

### 6.3 Ball

- 位置
- 速度
- 移動
- 衝突後の反射
- 速度は解決済みステージ設定から受け取る

将来的に複数ボールを扱えるよう、Game が単一 Ball を固定的に持つ設計は避ける。

### 6.4 Board

ブロック領域全体を管理する。マス数は解決済みステージ設定から受け取る。

### 6.5 Cell

画面上の1マスを表す。Cell 自身は複数の `BlockLayer` を持つ。

### 6.6 BlockLayer

セル上の破壊可能な1層を表す。

```python
class BlockLayer:
    id
    hp
    max_hp
    image
    source_rect
    collision
    tags
    metadata
```

一番上の有効レイヤーのみが通常は衝突対象となる。

---

## 7. レイヤー破壊システム

Breakout Forge の中心機能の一つ。衝突時は最上位有効 Layer に damage を与え、HP が 0 以下なら破壊し、下位 Layer を有効化する。全 Layer がなくなれば Cell は空になる。

クリア条件は初期実装では全破壊とするが、将来的にはタグ指定、破壊数、ボス、MOD 条件へ拡張する。

---

## 8. 画像ステージ

崩す対象画像1枚を `break_image.split` で論理分割し、それぞれを破壊タイルとして扱う。元画像ファイルそのものは小画像へ分割保存しない。各タイルは元画像の `source_rect` を参照し、UI は元画像を1回だけ保持して必要部分を描画する。

`stage_size` はステージ全体が論理的に何マスあるかを示す値で、崩す対象画像の分割数ではない。`break_image.split` は崩す対象画像を何分割するかを示し、この2つは独立する。表示解像度 `display.width / height` とも別概念である。

画像読み込みモードは次を持つ。

- `keep_background`: 背景を含めて画像全体を破壊対象として扱う
- `remove_background`: 四隅から連結する背景色を透過化し、前景が存在しないタイルは破壊対象にしない
- 背景色判定の許容差は `break_image.background_tolerance` で外部設定する

Fit モードは `contain`, `cover`, `stretch`。標準は `contain`。

---

## 9. 多層画像ステージ

複数の崩す対象画像を同一の `break_image.split` グリッドへ割り当て、`stage.json` の `layers` を下→上の順で各Cellへ積む。描画と衝突は最上位の有効Layerを使用し、上層の一部が壊れると、そのCellだけ下層画像が即時露出する。

Layerごとに `hp`, `collidable`, `destructible`, `visible` を持てる。背景除去によってあるLayerのタイルが空になった場合、そのCellでは最初から下位Layerが見える。

複数画像はピクセル解像度が異なってもよいが、同じタイル座標を同じ表示位置へ重ねるため縦横比は一致必須とする。各Layerの `source_rect` はそれぞれの元画像寸法から計算し、destination Cellは共有する。

---

## 10. 設定システム

### 10.1 common.json

全ステージの既定値を保持する。主要項目の例:

```json
{
  "format_version": 1,
  "gameplay": {
    "ball_speed": 360.0,
    "paddle_speed": 520.0,
    "paddle_size": {
      "width": 120,
      "height": 18
    }
  },
  "stage_size": {
    "columns": 20,
    "rows": 15
  },
  "break_image": {
    "split": {
      "columns": 20,
      "rows": 15
    },
    "load_mode": "keep_background",
    "background_tolerance": 16
  },
  "playfield": {
    "fit": "contain"
  }
}
```

- `stage_size.columns / rows`: ステージ全体の論理マス数
- `break_image.split.columns / rows`: 崩す対象画像の論理分割数
- `display.width / height`: 表示解像度
- 上記3種は独立した概念として扱う

### 10.2 stage.json

ステージ固有設定は必要な項目だけ記述する。

```json
{
  "format_version": 1,
  "id": "sample_stage",
  "name": "Sample Stage",
  "settings": {
    "gameplay": {
      "ball_speed": 420.0
    },
    "stage_size": {
      "columns": 24,
      "rows": 18
    },
    "break_image": {
      "split": {
        "columns": 32,
        "rows": 20
      },
      "load_mode": "remove_background"
    }
  },
  "layers": [
    {
      "id": "main",
      "image": "main.png",
      "hp": 1
    }
  ]
}
```

この例ではステージ全体は24×18論理マス、崩す対象画像は32×20分割であり、両者は同じ値である必要はない。

### 10.3 設定マージ規則

設定はオブジェクト単位で全置換せず、キー単位で再帰的にマージする。

例:

```text
common:
paddle_size.width  = 120
paddle_size.height = 18

stage:
paddle_size.width  = 160

resolved:
paddle_size.width  = 160
paddle_size.height = 18
```

これによりステージ作者は変更したい値だけを書けばよい。

### 10.4 外部化対象

少なくとも以下は外部データ化する。

- ボール速度
- パドル速度
- パドル幅 / 高さ
- ステージ全体の論理マス数
- 崩す対象画像の分割列数 / 行数
- playfield fit
- Layer HP
- 画像パス
- 将来追加するボールサイズ、初期方向、残機、スコア倍率、背景、色、音量、アイテム率などの調整値

新しい機能を実装する際も「ユーザーやステージ作者が変更したくなる値か」を確認し、該当するならプログラム定数ではなく設定項目を優先する。

### 10.5 フォーマットバージョン

`common.json` と `stage.json` はそれぞれ `format_version` を持つ。将来仕様変更時に旧データを判定・変換できるようにする。

---

## 11. Cell ごとの差分

画像全体へ同一レイヤーを適用するだけでなく、Cell 単位で設定を変更できる構造を用意する。将来的に `overrides` を追加し、一部だけ硬い、破壊不能、多層、イベント付き等を表現する。

---

## 12. MOD システム

`mods/<mod>/mod.json` と Python entry を使用する。entry は `setup(api)` を公開し、`api.subscribe(event_name, handler)` で公開イベントを購読する。MOD へはpygameのSurface/Rectやprivateゲームオブジェクトを渡さず、座標、Layer ID、score、delta等のframework-neutralなイベントデータだけを渡す。

1つのMODのimport/setup失敗やhandler例外はログへ記録し、他MODとゲーム本体を可能な限り継続する。

Python MODはサンドボックスではなく通常のPythonコードとして実行される。ファイルアクセスやネットワークアクセス等もPythonプロセスと同じ権限を持ち得るため、信頼できるMODのみ導入する。

初期イベント候補:

- `on_game_start`
- `on_game_update`
- `on_stage_loaded`
- `on_ball_hit_paddle`
- `on_block_hit`
- `on_layer_destroyed`
- `on_cell_destroyed`
- `on_stage_cleared`
- `on_game_over`

---

## 13. 配布

Windows は PyInstaller `--onedir` を使用する。実行ファイル名は `BreakoutForge.exe` とし、Python/依存ライブラリは `_internal/`、`config/`, `assets/`, `stages/`, `mods/`, `userdata/` は実行ファイルと同じ外部ベースディレクトリ配下に配置する。`--onefile` は使用しない。

ソース実行でも同じ相対構成を使用する。起動時のcurrent working directoryには依存せず、ソース時はリポジトリルート、frozen時はexeの親ディレクトリを基準とする。

`userdata/` は存在しなければ自動作成する。`userdata/settings.json` は任意で、設定解決順は `common → user → stage` とする。

Windows配布は `build.bat` から生成し、ビルド後に `BreakoutForge.exe --smoke-test` を実行して、exe隣の必須外部ディレクトリと `config/common.json` をGUI起動なしで確認する。

---

## 14. テスト方針

- common + stage の再帰マージ
- 未指定値の common 継承
- 不正型 / 範囲外値の検証
- stage_size / break_image.split を独立させた生成
- Layer 多層破壊
- MOD 読込失敗境界
- source 実行と onedir 実行の外部パス解決

設定解決は pygame なしで単体テスト可能にする。
