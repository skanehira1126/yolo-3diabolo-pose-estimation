# yolo-3diabolo-movie

3ディアボロウィンドミルの動画に人体の骨格を重ね、元映像と比較するためのツールです。人体姿勢推定にはUltralytics YOLO26 Poseを使用します。

## 準備

Python 3.12以上、uv、FFmpeg（ffprobeを含む）が必要です。プロジェクト直下で依存関係をインストールし、入力動画を`assets/`に用意してください。動画とモデル重みはリポジトリに含まれません。

```sh
uv sync
```

## 骨格付き動画を作る

```sh
uv run jupyter lab pose_video_materials.ipynb
```

設定セルで次の項目を入力動画に合わせて変更し、上から順に実行します。

| 設定 | 内容 |
| --- | --- |
| `INPUT_VIDEO` | 入力動画のパス |
| `MODEL` | 人体姿勢推定モデル。現在は`models/yolo26x-pose.pt`。未取得の場合は自動ダウンロード |
| `START_SECONDS` / `DURATION_SECONDS` | 開始時刻と処理秒数。長さを`None`にすると末尾まで処理 |
| `CROP_XYWH` | 切り抜き範囲`(左端, 上端, 幅, 高さ)`。全体を使う場合は`None` |
| `DEVICE` | Apple Siliconは`"mps"`、CPUは`"cpu"`、CUDAは`0`など |

`outputs/`内の実行別フォルダに、`original.mp4`（元映像素材）、`overlay.mp4`（骨格付き）、`skeleton.mp4`（骨格のみ）と設定を記録した`manifest.json`を保存します。動画は同じ処理区間の無音素材です。最後のセルで再生して確認できます。

骨格は各フレームで検出枠が最大の1人に描画します。別の人に切り替わる場合があるため、必要に応じて切り抜き範囲を設定してください。骨格は推定結果であり、正しい動作を保証するものではありません。

## 3つのディアボロを追跡する

```sh
uv run jupyter lab pose_object_tracking.ipynb
```

上記と同じ動画・モデル設定に加え、DaSiamRPNの重み3本を`models/`に用意します。

- `dasiamrpn_model.onnx`
- `dasiamrpn_kernel_r1.onnx`
- `dasiamrpn_kernel_cls1.onnx`

上から実行し、開始フレームで3つのディアボロを順に囲んでEnterで確定します。GUIを使わない場合は`TRACKING_ROIS`に3組の`(x, y, 幅, 高さ)`を指定します。座標は回転補正・切り抜き後、縮小前のフレーム基準です。

通常の3素材に加え、`tracking.mp4`（追跡枠）、`pose_tracking.mp4`（骨格＋追跡枠）、`skeleton_tracking.mp4`（黒背景の骨格＋追跡枠）、`tracking.csv`を保存します。`pose_tracking.mp4`を再生して元映像と比較してください。

これは手動指定した領域の追跡です。交差や遮蔽で取り違える場合があります。スティックや紐の検出・追跡は行いません。

## 3本の動画を横並びにする

```sh
uv run jupyter lab compare_three_videos.ipynb
```

設定セルの`SOURCE_DIR`に素材フォルダ、`VIDEO_FILES`に左・中央・右の順でファイル名を指定し、上から実行します。骨格のみ・元映像・骨格付きの比較なら、`skeleton.mp4`、`original.mp4`、`overlay.mp4`を指定します。

`outputs/comparisons/`内の実行別フォルダに`comparison.mp4`と`manifest.json`を保存し、最後のセルで再生できます。初期設定は1920×1080、30fps、無音です。3本の先頭をそろえ、最短の動画の長さに合わせます。動作のタイミングは自動同期しません。

## 動画情報を確認する

```sh
uv run yolo-3diabolo-movie video-info "assets/input.mp4"
```

FPS、解像度、1フレームの総画素数を表示します。YOLOモデルは不要です。

## ライセンス

本プロジェクトのソースコードとNotebookはGNU Affero General Public License v3.0（`AGPL-3.0-only`）で公開します。全文は[LICENSE](LICENSE)を参照してください。

利用するUltralytics YOLOのコードとモデルには、[Ultralyticsのライセンス条件](https://www.ultralytics.com/license)が適用されます。その他の依存ソフトウェア・モデルは各配布元のライセンスに従います。入力動画の権利はそれぞれの権利者に帰属します。
