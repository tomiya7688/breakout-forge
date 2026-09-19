# Formal UI Review

Breakout Forgeの正式Releaseでは、自動E2EだけでUIを承認しない。

## Review Pack

Release Gate dry-runは固定条件のスクリーンショットを生成する。

```bash
python scripts/capture_release_ui.py --project-root . --output release-ui
```

生成対象:

1. READY / 開始画面
2. 標準ステージプレイ中
3. 単一画像ステージ
4. remove_background画像ステージ
5. 多層画像ステージ（上層あり）
6. 多層画像ステージ（上層一部破壊・下層露出）
7. CLEAR
8. GAME OVER

`manifest.json` とPNG一式を `release-ui-review-pack` Artifactとして保存する。

## Tester A — Visual Regression

標準: Applitools Eyes。

確認:
- baselineとの差分
- レイアウト崩れ
- 欠落
- 位置ずれ
- 想定外のVisual Regression

Applitoolsを利用できない場合でも、Tester Aを単純なTester B/Cと同一レビューに置き換えず、
別系統のvisual regression evidenceを用意する。

## Tester B — Vision UI/UX

Vision対応AIでスクリーンショット群をレビューする。

確認:
- 読みやすさ
- 視線誘導
- 情報優先順位
- 重なり
- 不自然な余白
- 状態の理解しやすさ
- ゲーム画面としての視認性

## Tester C — Independent Vision

Tester Bとは別モデル系統、または独立セッション/独立promptで確認する。

確認:
- Bの見落とし
- 文字切れ
- コントラスト
- 誤解を招く表示
- 状態変化前後の不整合
- 初見ユーザー視点

## Manual Review

最後にプロジェクトオーナー本人がWindows release candidateを操作する。

確認:
- 実操作に違和感がない
- Paddle/Ball/Blockが見やすい
- READY/CLEAR/GAME OVERが理解できる
- 画像/多層破壊が視覚的に自然
- AIが報告した指摘を全件確認した
- release blocker / must fixが残っていない

## Evidence

レビュー完了後、`release/ui-review-template.json` をコピーして:

```text
release/ui-review-vX.Y.Z.json
```

を作る。

4セクションすべて:
- `status = "approved"`
- reviewer名/識別子
- evidence参照
- `release_blockers = []`

でなければ正式tagのPublish Gateを通さない。

多数決では承認しない。
1テスターでもblockerを報告した場合、解決または人間による明示的な再判定が必要。
