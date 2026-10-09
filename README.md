# yolo-3diabolo-movie

3ディアボロ動画の解析用パッケージ。Python 3.12以上が必要です（開発環境はPython 3.13）。

## GitHubに含めるもの

ソースコード、出力を削除したNotebook、依存関係の定義と`uv.lock`を管理します。`assets/`の入力動画、`outputs/`の生成物、`models/`のモデル重み、実行環境やキャッシュは含めません。READMEに記載した確定動画とその再作成スクリプトも、`outputs/`配下にあるためローカルにのみ存在します。

実行前に入力動画を`assets/`へ用意し、各Notebookの入力ファイル・切り抜き範囲・処理区間を設定してください。現在の人体モデルは`models/yolo26x-pose.pt`です。未取得のYOLOモデルはUltralyticsがダウンロードします。DaSiamRPNの重みは別途必要です。`DEVICE = "mps"`はApple Silicon向けなので、他の環境では`"cpu"`または利用可能なCUDAデバイスに変更してください。

commit前には、動画生成を再実行せずにNotebookの出力と実行番号を削除します。

```sh
uv run jupyter nbconvert --clear-output --inplace pose_video_materials.ipynb pose_object_tracking.ipynb compare_three_videos.ipynb
git status --short
```

人体姿勢推定には[Ultralytics YOLO26 Pose](https://docs.ultralytics.com/models/yolo26/)を使用しています。依存ソフトウェア・モデルのライセンスは、それぞれの配布元を参照してください。

## 姿勢推定＋3ディアボロ追跡の試行

`pose_object_tracking.ipynb` は `pose_video_materials.ipynb` のコピーに、参考元 `diabolo_tracking/dev.ipynb` のDaSiamRPN追跡を追加したものです。

```sh
uv sync
uv run jupyter lab pose_object_tracking.ipynb
```

上から実行し、開始フレームで3つのディアボロを順に囲んでEnterで確定します。対象数は3つ固定です。GUIを使わない場合は `TRACKING_ROIS` に3組の座標を指定します。初期入力は `assets/右利きのイリエ.mp4.mov`、人体モデルは `models/yolo26x-pose.pt`、試行区間は先頭5秒です。

両ノートブックの骨格表示は、各フレームで人物検出枠の面積が最大の1人だけを対象にします。同面積なら検出結果の先頭を選び、人物未検出時は骨格を描画しません。同一人物の追跡ではないため、別の人の枠が大きくなると表示対象が切り替わります。元映像とディアボロの追跡対象は変更しません。実行後は `overlay.mp4`（追跡版では `pose_tracking.mp4` も）で表示を確認できます。選択方式は `manifest.json` の `person_selection` に記録します。

追跡は `models/dasiamrpn_model.onnx`、`dasiamrpn_kernel_r1.onnx`、`dasiamrpn_kernel_cls1.onnx` を使います。カーネル2本は参考プロジェクトからコピーし、本体は同プロジェクトの `models/model_install.sh` に記載された [取得元](https://www.dropbox.com/s/rr1lk9355vzolqv/dasiamrpn_model.onnx?dl=1) から取得しました。FFmpegも必要です。

`outputs/` の実行別フォルダに元の3素材と `tracking.mp4`（追跡枠）、`pose_tracking.mp4`（骨格＋追跡枠）、`skeleton_tracking.mp4`（黒背景の骨格＋追跡枠）、`tracking.csv`、設定を記録した `manifest.json` を保存します。CSVは回転・切り抜き後、縮小前の座標です。3つの追跡器は独立しているため、交差・遮蔽時の取り違えを元映像と比較してください。これは手動指定領域の追跡であり、ディアボロの自動検出ではありません。

## 3本の動画を横並びに合成

`compare_three_videos.ipynb` で、3つのMP4を左・中央・右に並べた比較動画を作れます。

```sh
uv sync
uv run jupyter lab compare_three_videos.ipynb
```

FFmpegとffprobeが必要です。上から実行し、`SOURCE_DIR` に `outputs/` 内の実行フォルダ、`VIDEO_FILES` に3つのファイル名を指定します。初期設定は `skeleton.mp4`、`original.mp4`、`overlay.mp4` の順です。絶対パスで別フォルダの動画も指定できます。

高さをそろえて3本を隙間なく横に並べ、縦横比を保って全体を1920×1080（16:9）に収めます。必要な黒い余白は外側だけに付けます（入力映像自体の余白は除去しません）。先頭をそろえて同時再生します。出力は最短の動画の長さに合わせた無音のMP4（初期値1920×1080、30fps）です。動作のタイミングの自動同期は行いません。`outputs/comparisons/日時_ID/` に `comparison.mp4` と入力・設定の `manifest.json` を保存し、最後のセルで再生できます。

## 動画情報の取得

```sh
uv sync
uv run yolo-3diabolo-movie video-info "assets/アゴウテンセイ.mp4"
```

指定したローカル動画のFPS、解像度（幅 × 高さ）、1フレームの総画素数を標準出力に表示します。総画素数は幅と高さの積で、ファイルサイズではありません。入力動画は変更しません。

Pythonやノートブックからも呼び出せます。

```python
from yolo_3diabolo_movie import get_video_info

info = get_video_info("assets/アゴウテンセイ.mp4")
print(info.fps, info.width, info.height, info.pixel_count)
```

OpenCVで動画情報を読み取るため、YOLOモデルの読み込みやダウンロードは不要です。幅・高さは回転メタデータによる自動回転前の値です。FPSはOpenCVが返す値で、可変FPSの動画では各フレームの時間間隔が一定であることを保証しません。動画を開けない場合や有効な情報を取得できない場合、関数は例外を送出し、CLIはエラーを表示して終了コード1で終了します。

## 5人比較動画の等速マスター（2026-10-10）

承認済み動画は `outputs/five_people_final_20261010/comparison.mp4`。上段original・下段overlay、左からアゴウテンセイ、トミタヒカル、ノナカアオイ、ヤマザキ、右利きのイリエ。1920×1080、30fps、約13.6秒、無音です。

元素材からの開始位置は順に3.25秒・1.05秒・3秒・4.5秒・0秒。入江のみ先頭に黒画面0.5秒を追加。ノナカアオイと入江は上168px・下170px、ヤマザキは上338pxを切り抜き、originalとoverlayに同じ設定を適用しています。ボーンはYOLO26x-poseによる推定結果です。

同フォルダの `manifest.json` に入力・モデル・加工設定・動画のSHA-256を、`create_preview.py` に再作成手順を保存しています。FFmpegと日本語フォントを使用します。再作成はフォルダを別名で複製し、その中の動画・画像出力を取り除いてから `python3 複製先/create_preview.py` を実行してください（スクリプトは既存動画を上書きしません）。確認はMP4の再生、`preview.jpg` と `contact_sheet.jpg` の参照で行えます。確定動画は承認済み試作とハッシュ一致を確認しています。

## 最終版：先頭2秒カット・0.25倍速（2026-10-10承認）

最終成果物は `outputs/five_people_final_quarter_speed_20261010/comparison.mp4` です。等速マスターから先頭2秒をカットし、0.25倍速にしています。1920×1080、30fps、約46.5秒、無音。配置・個人ごとの開始位置・切り抜きは等速マスターを引き継いでいます。フレーム複製で減速し、動作補間は行っていません。

同フォルダの `manifest.json` に最終版の承認状態・加工設定・入力情報・SHA-256を保存しています。全編デコード確認済みです。再作成用の `create_slow.sh` も保存済みで、既存動画は上書きしません。動画を再生して確認できます。以前の等速版と0.5倍速版は残しています。
