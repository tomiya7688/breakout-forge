# Release Procedure

Breakout Forge の正式リリースは、通常の PR CI だけでは行わない。

通常開発では `CI / Data Check / Build Check` を使用し、正式リリース時は追加で
`.github/workflows/release-gate.yml` の **Release Gate** を必須とする。

## Version source of truth

バージョン番号の管理元は次の1箇所。

```text
src/breakout_forge/__init__.py
└─ __version__ = "1.0.0"
```

`pyproject.toml` は `breakout_forge.__version__` を動的参照する。

リリースタグは必ず:

```text
v<__version__>
```

と一致させる。

例:

```text
__version__ = "1.0.0"
tag         = "v1.0.0"
```

一致しない場合は Release Gate が失敗する。

## Release Gate

Release Gate は通常CIの結果を信用して省略せず、リリース対象commitをもう一度独立して検証する。

### Source Regression

Linux上で:

- Python 3.12環境構築
- tag/version一致
- compileall
- Ruff
- 全pytest
- repository全データ検証
- source smoke test
- standard/sample/remove_background_sample/layered_sampleのheadless load
- example MODのimport/register
- machine-readable release probe
- 専用Release E2E
- 既知不具合台帳のblocker/must-fix検査

### Windows Artifact

実際のリリースOS上で:

- 全pytestを再実行
- repository全データを再検証
- `build.bat` で本番と同じPyInstaller onedir build
- ビルド済みEXEへheadless入力を与える
- EXEが返すrelease probe JSONを期待値比較
- stage id入力と明示stage.json path入力を検証
- 別current working directoryから同じ結果になることを検証
- README / LICENSE / THIRD_PARTY_NOTICES / third_party_licenses / config / stages / mods / assets / userdataを確認
- dedicated Release E2EをWindowsでも再実行
- UI Review Packを固定9画面で生成

### ZIP Boundary

実ビルド後:

1. `BreakoutForge-vX.Y.Z-windows-x64.zip` を生成
2. SHA-256を生成
3. 新しい空ディレクトリへZIPを展開
4. 展開後の `BreakoutForge.exe` に対して同じrelease acceptanceを再実行
5. checksumを再計算し一致確認

「distでは動くがZIP配布後は壊れる」をここで検出する。

## Machine-readable expected output

windowed EXEのstdoutには依存しない。

```text
BreakoutForge.exe --release-probe <output.json>
```

期待する契約:

```json
{
  "version": "1.0.0",
  "base_dir": "<BreakoutForge directory>",
  "smoke_test": "ok",
  "validated_stages": [
    "standard_sample",
    "sample",
    "remove_background_sample",
    "layered_sample"
  ],
  "loaded_mods": [
    "example_mod"
  ],
  "userdata_exists": true
}
```

Release Gate はこのJSONを完全一致で検証する。

## Manual dry run

tagを作る前に GitHub Actions の `Release Gate` を workflow_dispatch で実行する。

入力:

```text
release_tag = v1.0.0
```

workflow_dispatchではReleaseの公開は行わず、release candidate Artifactと `release-ui-review-pack` を生成する。UI Review PackをTester A/B/Cとプロジェクトオーナーが確認し、正式tag前に `release/ui-review-vX.Y.Z.json` へ証跡を記録する。

## Formal release

1. mainへリリース対象変更を統合
2. CI / Data Check / Build Checkが成功していることを確認
3. #30 統合受け入れテスト完了
4. #33 ライセンス・同梱物監査完了
5. Release Gateをworkflow_dispatchでdry run
6. UI Review PackをTester A/B/Cでレビュー
7. プロジェクトオーナーがManual UI Reviewを実施
8. `release/ui-review-vX.Y.Z.json` を4者approvedで記録
9. `release/known-issues.json` にopen blocker/must-fixがないことを確認
10. versionと同じannotated tagを作成
11. tagをpush
12. tag起動のRelease Gateを待つ
13. 全gate成功後のみGitHub Releaseが自動作成される

例:

```bash
git tag -a v1.0.0 -m "Breakout Forge v1.0.0"
git push origin v1.0.0
```

Release Gateが失敗した場合、そのtagから正式Releaseを作成しない。
修正commitを作り、必要ならバージョンを上げて新しいtagでやり直す。

## Release assets

正式Releaseへ添付:

- `BreakoutForge-vX.Y.Z-windows-x64.zip`
- `BreakoutForge-vX.Y.Z-windows-x64.zip.sha256`

ZIP内:

```text
BreakoutForge/
├─ BreakoutForge.exe
├─ _internal/
├─ README.md
├─ LICENSE
├─ THIRD_PARTY_NOTICES.md
├─ third_party_licenses/
├─ config/
├─ assets/
├─ stages/
├─ mods/
└─ userdata/
```

## Release notes minimum format

- 概要
- 主な新機能
- ステージ/MOD互換性に関する変更
- 設定schema変更
- 既知の問題
- アップグレード時の注意
- SHA-256付きWindows配布ZIPへの導線

GitHubのgenerated notesを土台にし、必要な互換性・既知問題を追記する。

## Bug policy

既知の再現可能な不具合は、リリース前に次のいずれかへ分類する。

- **release blocker**: データ破損、起動不能、クラッシュ、主要機能不成立、配布物不成立
- **must fix**: 通常操作で高頻度に遭遇する重大な誤動作
- **known issue**: 回避策があり主要機能を阻害しないもの

release blocker / must fix が残った状態ではtagを作成しない。


## UI review evidence gate

正式tagのPublish jobは `release/ui-review-vX.Y.Z.json` を検証する。

必須:
- Tester A: Visual Regression / Applitools Eyes
- Tester B: Vision UI/UX
- Tester C: 独立Vision
- Manual UI Review: プロジェクトオーナー

4者すべて `approved`、reviewer/evidence記録あり、`release_blockers=[]` でなければGitHub Releaseを作成しない。

詳細: `docs/UI_REVIEW.md`

## Machine-readable known bug gate

`release/known-issues.json` を正式Releaseの既知不具合台帳とする。

severity:
- `release_blocker`
- `must_fix`
- `known_issue`

`release_blocker` または `must_fix` が `status=open` の場合、Release Gateは失敗する。


## Automated UI reviewers

Tester A/B/C are part of Release Gate and are not manually transcribed.

- Tester A: deterministic SHA-256 comparison against `release/ui-visual-baseline-v1.0.0.json`
- Tester B: GitHub Copilot SDK + GPT-5 mini
- Tester C: GitHub Copilot SDK + Claude Sonnet 4.6

Tester B/C both receive all nine PNG screenshots, but use different model providers and different review rubrics.
Any `release_blocker`, `must_fix`, rejected response, malformed model output, or model invocation failure fails Release Gate.

Authentication order:
1. optional repository secret `COPILOT_CI_TOKEN`
2. built-in GitHub Actions `GITHUB_TOKEN`

The workflow requests `copilot-requests: write`. If a repository/account policy does not permit built-in token billing, configure `COPILOT_CI_TOKEN` with a Copilot-capable token.

Only the project-owner Manual UI Review remains a human approval before Publish.
