# discord-notify

[Discord](https://discordapp.com/)の[Webhook](https://discordapp.com/developers/docs/resources/webhook)を利用した通知botです。

## Requirement

discord-notifyにはPython 3.8以降が必要です。  
また、標準ライブラリ以外に[dhooks](https://github.com/kyb3r/dhooks)と[requests](https://github.com/psf/requests)を使用しています。

```
pip install dhooks requests
```

## Details

### board.py

大学の学科掲示板が更新されると、以下のようなembed形式で通知してくれます。

![](https://user-images.githubusercontent.com/59264002/74111082-2f2fcb00-4bd5-11ea-913b-346c73e71e43.png)

環境変数として`BOARD_ID`にログインに必要なID、`BOARD_PASS`にパスワード、`DISCORD_WEBHOOK_URL`に作成したWebhookのURL、`BOARD_URL`に学科掲示板のURL、`FAVICON_URL`に学科掲示板のfaviconを設定する必要があります。

---

他にも増えたら追記します。

## License

discord-notifyはMITライセンスです。詳しくは[LICENSE](https://github.com/yurkth/discord-notify/blob/master/LICENSE)を見てください。