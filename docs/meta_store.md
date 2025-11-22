# メタ情報管理 (core.meta_store)

ダウンロード済みファイルの SHA256 と処理時刻を JSON で保持し、ETL の冪等性を担保します。メタファイルは `data/meta/` 配下に保存さ
れ、`core.meta_store` の関数から読み書きできます。

## 保存先パス

```
data/meta/<category>/<dataset_id>/<raw_filename>.json
```

`data/raw/` と同じカテゴリ/データセット階層を使い、元ファイル名に `.json` を付与します。

## JSON フォーマット

```json
{
  "dataset_id": "wifi_2020_count",
  "category": "connectivity",
  "source_url": "https://example.com/data/wifi.csv",
  "raw_path": "data/raw/connectivity/wifi_2020_count/wifi.csv",
  "sha256": "<content hash>",
  "downloaded_at": "2024-01-01T00:00:00+00:00",
  "processed_at": "2024-01-02T03:04:05+00:00"
}
```

- `sha256`: ダウンロード後に `calculate_sha256()` で算出したハッシュ。
- `downloaded_at`: raw ファイルの更新時刻 (UTC)。
- `processed_at`: パイプラインで正規化/DB 反映が完了した時刻を ISO8601 で保存。

## 主な操作

- `get_meta_path(dataset, raw_path)`: メタファイルの保存先パスを返す。
- `calculate_sha256(path)`: ファイルの SHA256 を計算する。
- `mark_loaded(dataset, raw_path, sha256, processed_at)`: メタ情報を JSON で書き出す。
- `is_already_loaded(dataset, raw_path, sha256)`: メタ情報と完全一致する場合に処理済みと判定する。

`is_already_loaded` が真を返した場合、同一 URL・同一内容のファイルは再処理をスキップできます。URL 変更やファイル内容の変化によって
SHA256 が異なる場合は再処理されます。

