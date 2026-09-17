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
│     │  ├─ game.py
│     │  ├─ ball.py
│     │  ├─ paddle.py
│     │  ├─ board.py
│     │  ├─ cell.py
│     │  ├─ layer.py
│     │  └─ collision.py
│     ├─ stage/
│     │  ├─ loader.py
│     │  ├─ schema.py
│     │  └─ image_stage.py
│     ├─ modding/
│     │  ├─ loader.py
│     │  ├─ api.py
│     │  └─ events.py
│     ├─ assets/
│     │  └─ loader.py
│     └─ config/
│        └─ loader.py
├─ assets/
├─ stages/
│  └─ sample/
├─ mods/
│  └─ example_mod/
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

---

## 6. ゲームモデル

### 6.1 Game

ゲーム全体の状態遷移を管理する。

主な責務:

- ゲーム開始 / 終了
- 更新処理
- 描画処理
- ステージクリア判定
- ゲームオーバー判定
- イベント発火

Game 自身へブロックや画像の詳細処理を詰め込まない。

### 6.2 Paddle

主な責務:

- プレイヤー入力による左右移動
- 移動範囲制限
- ボールとの衝突領域提供

### 6.3 Ball

主な責務:

- 位置
- 速度
- 移動
- 衝突後の反射

将来的に複数ボールを扱えるよう、Game が単一 Ball を固定的に持つ設計は避ける。

### 6.4 Board

ブロック領域全体を管理する。

```text
Board
 ├─ Cell[0,0]
 ├─ Cell[1,0]
 ├─ ...
 └─ Cell[x,y]
```

Board はグリッド配置を基本とするが、将来的な自由配置拡張を妨げない構造にする。

### 6.5 Cell

画面上の1マスを表す。

想定データ:

```python
class BlockCell:
    rect
    layers
    metadata
```

Cell 自身は複数の `BlockLayer` を持つ。

### 6.6 BlockLayer

セル上の破壊可能な1層を表す。

想定データ:

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

Breakout Forge の中心機能の一つ。

例:

```text
初期
┌──────────┐
│ armor    │  HP 2
├──────────┤
│ picture  │  HP 1
├──────────┤
│ ground   │  HP 1
└──────────┘
```

ボールが当たると最上位レイヤーの HP を減らす。

```text
Hit 1: armor HP 2 → 1
Hit 2: armor HP 1 → 0 → armor 削除
Hit 3: picture HP 1 → 0 → picture 削除
Hit 4: ground HP 1 → 0 → Cell 空
```

### 7.1 基本ルール

1. 衝突時、Cell の最上位有効レイヤーを取得する
2. レイヤーへ damage を与える
3. HP が 0 以下ならそのレイヤーを破壊する
4. 下位レイヤーが存在すれば即座に表示・衝突対象へ切り替える
5. レイヤーがなくなれば Cell は空になる

### 7.2 クリア判定

単純に「全 Cell が空」を固定ルールにはしない。

ステージ側で将来的に以下を選べるようにする。

- 全破壊
- 特定タグを持つレイヤーの全破壊
- 特定数破壊
- ボスレイヤー破壊
- MOD 独自条件

初期実装では全破壊を標準とする。

---

## 8. 画像ステージ

### 8.1 概要

画像1枚を指定グリッドへ分割し、それぞれを Cell / BlockLayer の表示領域として扱う。

画像そのものを物理的に分割ファイルへ保存する必要はない。

```text
image.png
   ↓
20 x 15 に論理分割
   ↓
300 Cell
```

各 BlockLayer は元画像と `source_rect` を参照する。

### 8.2 描画イメージ

```python
screen.blit(
    image,
    destination_rect,
    source_rect,
)
```

破壊済み Cell は描画しないため、画像に穴が開いていくように見える。

### 8.3 Fit モード

初期候補:

- `contain`: アスペクト比維持、全体表示
- `cover`: アスペクト比維持、領域を埋める
- `stretch`: 領域へ強制フィット

初期実装では `contain` を標準とする。

---

## 9. 多層画像ステージ

複数画像を同一グリッドへ割り当て、上から順番に破壊できる。

```text
layer_2.png   ← 最初に見える
layer_1.png
layer_0.png   ← 最下層
```

例えば一部を壊すと、その場所だけ下の画像が露出する。

```text
AAAAAAAA
AAAABAAA
AAABBAAA
AAAAAAAA
```

A = 上層画像
B = 下層画像

これを標準システムとして実装し、特殊ケースとして扱わない。

---

## 10. ステージ定義

### 10.1 stage.json

初期案:

```json
{
  "format_version": 1,
  "id": "sample_stage",
  "name": "Sample Stage",
  "grid": {
    "columns": 20,
    "rows": 15
  },
  "playfield": {
    "fit": "contain"
  },
  "layers": [
    {
      "id": "background",
      "image": "background.png",
      "hp": 1
    },
    {
      "id": "main",
      "image": "main.png",
      "hp": 1
    },
    {
      "id": "armor",
      "image": "armor.png",
      "hp": 2
    }
  ]
}
```

配列では下から上へ定義することを基本とする。

### 10.2 フォーマットバージョン

`format_version` を必須にする。

将来 stage.json の仕様を変更しても、旧ステージを判定・変換できるようにする。

---

## 11. Cell ごとの差分

画像全体へ同一レイヤーを適用するだけでなく、Cell 単位で設定を変更できる構造を用意する。

用途:

- 一部だけ硬い
- 一部だけ破壊不能
- 中央だけ多層
- 特定ブロックだけアイテムを持つ
- 特定箇所のみイベント発火

初期 stage.json では複雑化を避け、必要になった段階で `overrides` を追加する。

例:

```json
{
  "overrides": [
    {
      "x": 4,
      "y": 3,
      "layer": "armor",
      "hp": 5
    }
  ]
}
```

---

## 12. MOD システム

### 12.1 配置

```text
mods/
└─ example_mod/
   ├─ mod.json
   └─ main.py
```

### 12.2 mod.json

```json
{
  "format_version": 1,
  "id": "example_mod",
  "name": "Example Mod",
  "version": "1.0.0",
  "entry": "main.py"
}
```

### 12.3 初期イベント案

- `on_game_start`
- `on_game_update`
- `on_stage_loaded`
- `on_ball_hit_paddle`
- `on_block_hit`
- `on_layer_destroyed`
- `on_cell_destroyed`
- `on_stage_cleared`
- `on_game_over`

### 12.4 MOD API

MOD は公開 API 経由でゲームへアクセスする。

例:

```python
def setup(api):
    api.events.subscribe("on_layer_destroyed", on_destroyed)


def on_destroyed(event):
    pass
```

### 12.5 セキュリティ上の扱い

Python MOD は任意の Python コードを実行できるため、安全なサンドボックスとはみなさない。

ドキュメント上で次を明示する。

- 信頼できない MOD を実行しない
- MOD はユーザー権限で任意コードを実行可能
- MOD の安全性をゲーム本体が保証しない

---

## 13. アセット管理

ゲーム標準アセットとユーザーコンテンツを分離する。

```text
assets/     標準アセット
stages/     外部ステージ
mods/       MOD
userdata/   設定・ログ等
```

PyInstaller `--onedir` でも、ユーザーが `stages/` と `mods/` を簡単に追加・削除できる配置とする。

---

## 14. パス解決

開発実行と PyInstaller ビルドの双方で同じコードを利用できるよう、パス解決を一元化する。

例えば `paths.py` 相当のモジュールを用意し、以下を提供する。

- application directory
- assets directory
- stages directory
- mods directory
- userdata directory

各モジュールで `__file__` やカレントディレクトリを直接参照しない。

---

## 15. ビルド

### 15.1 Windows

PyInstaller の `--onedir` を標準とする。

概念例:

```bat
python -m PyInstaller ^
  --clean ^
  --noconfirm ^
  --onedir ^
  --windowed ^
  --name BreakoutForge ^
  src/breakout_forge/__main__.py
```

### 15.2 配布物

```text
BreakoutForge/
├─ BreakoutForge.exe
├─ _internal/
├─ assets/
├─ stages/
├─ mods/
└─ userdata/   # 初回起動時生成でも可
```

外部コンテンツを `_internal/` 内へ隠さないことを基本とする。

---

## 16. CI

最低限、GitHub Actions で以下を確認する。

```text
push / pull_request
        ↓
依存関係インストール
        ↓
lint / test
        ↓
import / smoke test
        ↓
PyInstaller build
        ↓
artifact 保存
```

初期段階では Windows ビルドを優先する。

CI が常に「ゲームとして配布可能な状態」を確認することを目標にする。

---

## 17. テスト方針

ゲームループ全体より、ロジック単位を優先してテストする。

初期対象:

- Cell の layer 遷移
- HP 減少
- layer 破壊
- Cell 完全破壊
- ステージ JSON 読み込み
- 不正 JSON のエラー処理
- 画像グリッド分割
- MOD manifest 読み込み
- イベント登録 / 発火
- パス解決

pygame の描画そのものへ過度に依存したテストは避ける。

---

## 18. エラー処理

ユーザーが追加するコンテンツは壊れている可能性があることを前提とする。

### ステージ読み込み失敗

- アプリ全体をクラッシュさせない
- どのファイルに問題があるか表示する
- ログへ詳細を保存する

### MOD 読み込み失敗

- 可能ならその MOD のみ無効化する
- 他 MOD と本体は継続する
- traceback をログへ記録する

### 画像読み込み失敗

- 対応外形式 / 破損画像として明示する
- 代替画像またはステージ選択画面へ戻す

---

## 19. 標準ゲーム仕様 v0.1

最初のプレイ可能版では以下のみ実装する。

- 800x600 程度のウィンドウ
- パドル1本
- ボール1個
- 左右移動
- 壁反射
- パドル反射
- ブロック反射
- Cell / Layer 破壊
- 全対象破壊でクリア
- ボールが下へ落ちたらゲームオーバー
- リスタート
- 標準ステージ1つ

高度な演出は後回しとする。

---

## 20. 開発フェーズ

### Phase 1: Core

- プロジェクト雛形
- pygame 起動
- Game loop
- Paddle
- Ball
- 衝突
- Board / Cell / BlockLayer
- 通常ステージ

### Phase 2: Layer System

- 複数 Layer
- HP
- レイヤー切り替え
- クリア条件

### Phase 3: Image Stage

- PNG / JPEG / WebP 読み込み
- グリッド分割
- 画像ステージ
- 多層画像
- stage.json

### Phase 4: Packaging

- PyInstaller `--onedir`
- build.bat
- CI ビルド
- artifact 出力

### Phase 5: Modding

- mod.json
- MOD loader
- Event system
- 公開 API
- Example MOD

### Phase 6: Tooling

- ステージ選択
- 画像選択
- ドラッグ & ドロップ
- GUI ステージエディタ
- MOD 管理

---

## 21. 初期非目標

v0.1 では次を必須にしない。

- オンライン対戦
- ランキングサーバー
- MOD の完全サンドボックス
- 高度な物理エンジン
- 3D
- ECS
- スクリプト言語の自作
- 大規模 GUI エディタ

小さいコードベースのまま、拡張可能性を確保することを優先する。

---

## 22. 設計上の重要原則

Breakout Forge の基本モデルは次のように保つ。

```text
Game
 ├─ Paddle(s)
 ├─ Ball(s)
 └─ Board
     └─ Cell
         └─ BlockLayer [0..n]
```

そしてコンテンツ側は、

```text
Stage data
   ↓
Board / Cell / BlockLayer を生成
```

MOD 側は、

```text
Public API / Events
   ↓
Game に機能を追加
```

という境界を守る。

これにより、通常のブロック崩し、画像を壊すゲーム、多層画像を剥がすゲーム、特殊ルールを持つ MOD ゲームを同一のコアで扱えるようにする。

---

## 23. 最初の完成条件

最初のマイルストーンでは、以下を満たした時点を「最低限完成」とする。

- リポジトリを clone して依存関係を導入できる
- 開発環境からゲームを起動できる
- 標準ブロック崩しを最後まで遊べる
- 任意画像をステージとして読み込める
- 2枚以上の画像レイヤーを順番に破壊できる
- stage.json からステージを生成できる
- `build.bat` で Windows onedir ビルドできる
- CI でテストとビルドが通る
- `mods/` から Example MOD を読み込める

この状態を v0.1 系の基準とする。
