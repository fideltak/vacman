[English](README_en.md)
# コロナワクチン予約状況通知
自治体のワクチン接種予約が全然できず、且つ予約サービスに空き状況の通知機能が無いことにイラっとして作りました。作成後、２時間くらいで希望の場所で予約できました。

## 通知方法
- LINE Notify

## サンプル
<img src="docs/pics/line_notify_sample01.png" width="300px">

## 概要
定期的にワクチン接種の空き状況を取得して通知します。以下のコンポーネントで成り立っています。

### Vaccine Checker
[vaccine-checker](./vaccine-checker)はワクチン接種の空き状況を定期的に取得し、有効なLINE Notifyのトークンが存在する場合にLINE通知します。

事前に自身の自治体が提供するワクチン接種サービス内で、**ワクチン接種場所一覧**と**空き接種場所**を提供するAPIエンドポイントを特定してください。Google Chromeの開発者モードを使えばすぐに特定できます。
[vaccine-checker](./vaccine-checker)は**vaccines.sciseed.jp**が提供しているAPIでテストしています。APIが**vaccines.sciseed.jp**以外から提供されている場合は、データ構造が変わるはずなので動かないと思っています。

#### 例
APIエンドポイントは自治体によって異なります。以下の例は東京都杉並区の場合です。

- 接種場所一覧: https://api-cache.vaccines.sciseed.jp/public/131156/department/
- 空き接種場所: https://api-cache.vaccines.sciseed.jp/public/131156/available_department/

#### パラメータ
各種パラメータはOS環境変数に設定してください。

| KEY | VALUE | 要不要 | デフォルト | 例 |その他 |
| :---: | :---: | :---: | :---: | :--- | :---: |
| VACCINE\_RESERVATION\_URL | 自治体のワクチンの予約サイトURL | 必要 | NA |  |予約しやすいように通知の最後に記載されます |
| VACCINE\_ALL\_PLACE\_URL | 接種場所一覧が取得できるAPIエンドポイント | 必要 | NA | https://api-cache.vaccines.sciseed.jp/public/\<ID\>/department/ |  |
| VACCINE\_AVAILABLE\_PLACE\_URL | 空き接種場所が取得できるAPIエンドポイント | 必要 | NA | https://api-cache.vaccines.sciseed.jp/public/\<ID\>/available_department/ |  |
| LINE_TOKEN\_FILE\_PATH | LINE notifyトークンのファイルパス | 必要 | NA | /app/config/line-token.conf | line-notify-webと同じファイルパスにしてください |
| NOTIFY\_DURATION\_SEC | 空き接種場所を検索して通知する秒間隔 | 必要 | NA | 3600 | サイトへの負荷を軽減するためリロードを禁止している自治体が多いの常識の範囲の間隔にしてください |

### LINE Notify Web
[line-notify-web](./line-notify-web)はLine Notifyへリダイレクト、コールバックを処理して、Line Notify用のアクセストークンを取得します。

事前に[Line Notify](https://notify-bot.line.me/ja/)に登録して、クライアントIDとシークレットを取得しておきます。

また、LINE notifyからのコールバックを受け取る必要があるので、**ウェブサーバーを外部に公開できる環境**が必要となります。

#### パラメータ
各種パラメータはOS環境変数に設定してください。

| KEY | VALUE | 要不要 | デフォルト | 例 |その他 |
| :---: | :---: | :---: | :---: | :--- | :---: |
| LINE\_TOKEN\_FILE\_PATH |  LINE notifyトークンを保存するファイルパス | 必要 | NA | /app/config/line-token.con |  |
| LINE\_NOTIFY\_CLIENT\_ID | LINE notifyクライアントID | 必要 | NA |  |  |
| LINE\_NOTIFY\_CLIENT\_SECRET | LINE notifyクライアントシークレット | 必要 | NA |  |  |
| LINE\_NOTIFY\_CALLBACK\_URL | LINE notifyのコールバックURL | 必要 | NA | https://tak-motors.com/callbac |  |
| WEB\_SERVER\_PORT | Webサーバーのポート番号 | 必要 | NA | 80 | LINE Notifyの登録やコールバックでWebサーバーを使います |

#### URI
- LINE Notify登録: http://\<YOUR_IP\>/line/notify
- LINE Notify Callback: http://\<YOUR_IP\>/line/callback

### コンテナイメージ
- [vaccine-checker](https://hub.docker.com/r/fideltak/vaccine-checker)
- [line-notify-web](https://hub.docker.com/r/fideltak/line-notify-web)

### k8sへデプロイ
テストではk8s上で以下のような構造で稼働させています。各種マニュフェストは[こちら](./k8s)を確認してください。

```
┌────────────────┐  ┌────────────────┐
│line-notify-web │  │vaccine-checker │
│                │  │                │
│                │  │                │
│                │  │                │
└───────▲────────┘  └───────▲────────┘
        │                   │
        │                   │
      ┌─┴───────────────────┴────┐
      │ PV RWX                   │
      │         line-token       │
      │                          │
      └──────────────────────────┘
```

共有ボリュームを用意してその中にline notify tokenを保存することで、２つのコンテナからtokenを参照できるようにしています。