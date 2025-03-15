# CoCoA: Japanese dataset of **Co**nference Presentation Titles in the Field of **Co**mputer Science for Multi-purpose **A**cademic Text Analysis

- 情報科学分野における日本語の学会発表タイトルを収集し、学術ドメインに特化した評価用データセット**CoCoA**を構築しました。
- 著者名・発表年・発表タイトル・研究分野の4つ組1.7万件からなるデータセットです。
- 情報処理学会全国大会 (IPSJ), 人工知能学会全国大会 (JSAI), 言語処理学会年次大会 (ANLP)から、過去10年分（2014年度から2023年度）の発表情報を取得して構築しました。
- ここでは、J-STAGE WebAPIを用いてデータ取得可能な人工知能学会全国大会について、CoCoAデータ構築用コードを公開します。
- 人工知能学会も含め全てのデータは、miyata@ai.cs.ehime-u.ac.jpまでご連絡いただければお渡しすることが可能です。

## 本コードの使い方
- poetry.tomlから実行環境を構築
- run.shを実行すると、CoCoA.jsonが作成されます。

## ライセンス
本コードは、J-STAGE WebAPIを用いています。<br>
利用規約は[こちら](https://www.jstage.jst.go.jp/static/pages/JstageServices/TAB3/-char/ja)を参照してください。

## 文献情報
\[1\] 宮田莉奈, 眞鍋光汰, 福島啓太, 花房健太郎, 高田一慶, 梶原智之, 桂井麻里衣, 二宮崇.<br>
&emsp;&nbsp;&nbsp;CoCoA: 情報科学分野における日本語の学会発表タイトルの分野推定データセット.<br>
&emsp;&nbsp;&nbsp;情報処理学会第87回全国大会(IPSJ). March 2025.
