# Release Test Matrix

正式リリース時に確認する主要な入出力と期待値。

| 対象 | 入力 | 期待値 |
|---|---|---|
| version source | release tag `vX.Y.Z` | `breakout_forge.__version__ == X.Y.Z` |
| source CLI | `--smoke-test` | exit 0 |
| source stage | `--validate-stage standard_sample` | exit 0 |
| source stage | `--validate-stage sample` | 画像decodeを含めexit 0 |
| source stage | `--validate-stage remove_background_sample` | 背景除去前処理を含めexit 0 |
| source stage | `--validate-stage layered_sample` | 多層画像decodeを含めexit 0 |
| source stage path | `--validate-stage stages/sample/stage.json` | exit 0 |
| source probe | `--release-probe result.json` | version/smoke/4stage/example MOD/userdataが期待JSONと一致 |
| game logic | 全pytest | 全成功 |
| data | `validate_data.py` | 全repository data成功 |
| broken data fixtures | pytest negative cases | 壊れた画像/MOD/参照切れを拒否 |
| Windows build | `build.bat` | exit 0 |
| packaged layout | onedir | exe/_internal/config/assets/stages/mods/userdata/README/LICENSE/THIRD_PARTY_NOTICES/third_party_licensesが存在 |
| packaged stage id | `BreakoutForge.exe --validate-stage sample` | exit 0 |
| packaged explicit path | `--validate-stage stages\sample\stage.json` | exit 0 |
| packaged probe | `--release-probe result.json` | JSON完全一致 |
| foreign cwd | 別directoryからEXE probe | base_dirと結果が変化しない |
| ZIP | release ZIP展開 | clean directoryで同じacceptanceが成功 |
| archive integrity | SHA-256 | 生成値と再計算値が一致 |
| release E2E | dedicated pytest | Data→Process→MOD→state transitionsが成功 |
| UI review pack | 9 fixed screenshots | manifestとPNG 9枚生成 |
| AI UI review | Tester A/B/C | 全員approved、blockerなし |
| manual UI review | owner | approved、blockerなし |
| known bug ledger | release/known-issues.json | open release_blocker/must_fixが0件 |

## Game behavior regression coverage

Release GateではWindows上でも全pytestを再実行するため、以下のProcess契約を含む既存テスト一式をリリースOSで再確認する。

- Paddle移動境界
- Ball移動・壁反射・Paddle反射・落下
- Board / Cell / BlockLayer
- HP damage
- 上層破壊後の下層露出
- Ball/Board衝突面反射
- 1frame多重衝突対策
- standard stage clear / game over / restart
- score
- common/user/stage設定継承
- stage loader validation
- PNG/JPEG/WebP
- keep_background / remove_background
- stage_size と break_image.split の独立性
- contain fit
- 多層画像のHP/露出/reset
- MOD manifest/import/setup
- MOD handler例外隔離
- external path source/frozen規則
- distribution preparation
- CLI stage selection

新しいバグを修正した場合、可能な限り「そのバグを再現して修正前に失敗するテスト」を追加し、
Release Gateの全pytestへ恒久的に組み込む。


## Release UI states

固定スクリーンショット:
1. READY
2. 標準ステージ開始直後
3. 標準ステージプレイ中
4. 単一画像
5. remove_background
6. 多層上層あり
7. 多層下層露出
8. CLEAR
9. GAME OVER

## Integrated release E2E

`tests/test_release_e2e.py` では実repository dataを通して次を結合確認する。

- common + stage読み込み
- standard / image / remove-background / layered fixture
- 背景除去前処理
- HP2上層の2hit破壊
- 下層露出
- resetによるLayer/HP復元
- CLEAR + score + restart
- GAME OVER + restart
- MOD event発火
- example MOD実import/register
- broken MODがgood MODと本体を巻き込まないこと
