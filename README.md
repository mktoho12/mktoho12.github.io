# mktoho.dev

個人サイト。いまやっていること、興味があること、作ったものを載せている

**https://mktoho.dev/**

## 構成

```
src/site.toml         トップページの中身（文章とリンク）
src/notes/*.md        記事（notes/<名前>/ に出る）
src/build.py          上の2つから HTML を作る
assets/site.css       見た目（方眼ノート、BIZ UDPゴシック、ブルーブラック1色）
index.html            できあがったトップページ（build.py が作る。手で直さない）
notes/<名前>/index.html  できあがった記事（同上）
```

GitHub Pages で公開している

## 更新のしかた

1. `src/site.toml` か `src/notes/*.md` を直す
2. リポジトリの一番上で次を実行する

   ```sh
   uv run --with budoux --with markdown python src/build.py
   ```

3. できた HTML も一緒に commit して push する

「最近のこと」は `site.toml` の `[[recent]]` を先頭に足す。上から8件を表示し、それより前はたたむ

## 文章の決まり

- 句点で改行する。句点そのものは表示されない
- 文の途中の折り返しは、BudouX が文節の切れ目に入れる
- 読む人へのお願い（「〜してください」）は書かない。「知りたい」までにとどめる
- 健康・医療、旅行、private リポジトリの中身、住んでいる場所が分かる情報は載せない

## アイコンについて

Skeb で依頼して描いてもらったもの。著作権は絵師にあります
