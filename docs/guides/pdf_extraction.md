# PDF 抽出パイプライン（観光入込客数）

観光入込客数（令和5年版など）の PDF は、CSV と異なりテーブル抽出が必要です。本リポジトリではまず **スケルトン実装** を用意し、将来的に Camelot や Tabula のような専用ライブラリに差し替えやすい構造にしています。

## 現在の挙動

- `configs/datasets.yml` に `tourism_r05_irikomi` を追加。
- `etl run tourism_r05_irikomi` で PDF を `data/raw/tourism/tourism_r05_irikomi/` にダウンロード。
- `src/kawasaki_etl/core/pdf_utils.py` の `extract_tables_from_tourism_irikomi` が呼ばれ、
  - `PDF と同名の CSV（.csv）` が同じディレクトリに存在する場合はそれを読み込み DataFrame を返します（モック用途）。
  - それ以外は「未実装」メッセージのみを含む DataFrame を返します。
- DataFrame をそのまま `data/normalized/tourism/tourism_r05_irikomi/*_extracted.csv` に保存します。

## 今後の拡張方針

- **抽出ライブラリ**: Camelot、tabula-py などのテーブル抽出ツールを候補とし、`extract_tables_from_tourism_irikomi` の中でライブラリごとの戦略を切り替えられるようにします。
- **モック差し替え**: 当面は PDF と同名の CSV を配置することで、外部依存なしにローカル開発・テストを実施できます。実装が進んだら、PDF 解析が失敗した場合のみモックにフォールバックするようにします。
- **カラムマッピング**: 本番投入時には観光入込客数のカラム仕様を整理し、`extra` 設定でマッピング/型変換を制御できるようにします。

## 注意点

- 現状は DB への upsert を行っていません。パース仕様が固まったら、Wi-Fi パイプラインと同様にテーブル名やキー設定を活用する想定です。
- PDF からの抽出処理は重くなることがあるため、将来的にはキャッシュやメタ情報（`data/meta/`）を活用して再処理をスキップします。
