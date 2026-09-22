# Formal UI Review

Breakout Forgeの正式Releaseでは、自動E2EだけでUIを承認しない。

## Review Pack

Release Gate dry-runは固定条件のスクリーンショットを生成する。

```bash
python scripts/capture_release_ui.py --project-root . --output release-ui
```

生成対象:

1. READY / 開始画面
2. 標準ステージ開始直後
3. 標準ステージプレイ中
4. 単一画像ステージ
5. remove_background画像ステージ
6. 多層画像ステージ（上層あり）
7. 多層画像ステージ（上層一部破壊・下層露出）
8. CLEAR
9. GAME OVER

`manifest.json` とPNG一式を `release-ui-review-pack` Artifactとして保存する。

## Tester A — Visual Regression

Release Gateで自動実行する。

- 承認済み9画面のSHA-256を `release/ui-visual-baseline-v1.0.0.json` に保持
- Windows release runnerで9画面を再生成
- screenshot集合と各PNGのdigestを完全一致で比較
- 1pixelでも差分が出た場合はRelease Gateを失敗させる
- 意図したUI変更の場合のみ、人間レビュー後にbaselineを更新する

これにより外部Visual RegressionサービスのAPI keyなしでもfail-closedで運用できる。

## Tester B — Vision UI/UX

Release Gateの `AI UI Review` jobで GitHub Copilot SDK + GPT-5 mini を使用し、
9画面を一括レビューする。

確認:
- 読みやすさ
- 視線誘導
- 情報優先順位
- 重なり
- 不自然な余白
- 状態の理解しやすさ
- ゲーム画面としての視認性

## Tester C — Independent Vision

Release Gateの同じjob内で、Tester Bとは別providerの Claude Sonnet 4.6 を使う。
modelとrubricを分け、GPT系レビューと独立したsecond opinionをCIで必須化する。

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

Tester A/B/Cの証跡はCI Artifactとして自動生成する。
人間の最終確認だけは `release/ui-review-template.json` をコピーして:

```text
release/ui-review-vX.Y.Z.json
```

を作る。

Manual UI Reviewセクションを:
- `status = "approved"`
- reviewer名/識別子
- evidence参照
- `release_blockers = []`

にする。Tester A/B/CはRelease Gateのjob成功そのものを必須証跡とし、
Publish jobは `AI UI Review` job成功 + Manual UI Review approved の両方を要求する。

多数決では承認しない。
1テスターでもblockerを報告した場合、解決または人間による明示的な再判定が必要。
