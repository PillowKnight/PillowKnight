import html
import os
import re
import traceback
from datetime import datetime
from time import sleep

import requests
from dhooks import Embed, Webhook

auth_info = (os.environ["BOARD_ID"], os.environ["BOARD_PASS"])


def get_html(url, timeout=10.0):
    """
    URLのHTMLを返す
    """
    res = requests.get(url, timeout=timeout, auth=auth_info)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    sleep(1)  # アクセス過多の回避
    return res.text


def generate_embed(url):
    """
    URLのページを確認してEmbedに整形する
    """
    article_html = html.unescape(get_html(url))

    # 記事の本文
    body = re.search(
        "<!-- begin text -->\r\n(.+?)<!-- end text -->",
        re.sub("<[^<>!]*>", "__", article_html),
        flags=(re.MULTILINE | re.DOTALL),
    ).group(1)
    # 文字数制限の回避(本文以外の制限は超えることがないので省略)
    # https://discordjs.guide/popular-topics/embeds.html#embed-limits
    if len(body) > 2048:
        body = body[:2014] + "…\n:warning:文字数が2048文字を超えたため省略されました"
    embed = Embed(description=body, color=0x7E6CA8)

    # 記事の詳細
    field = dict(re.findall("(.+?): (.+?)<BR>", article_html))
    if title := field.get("Subject"):
        embed.set_title(title=f":newspaper: {title}", url=url)
    if author := field.get("From"):
        embed.set_author(name=author.split("<")[0], icon_url=os.environ["data:image/jpeg;base64,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"])
    if date := field.get("Date"):
        embed.set_footer(date)
    if reference := field.get("Reference"):
        link, text = re.search('<A HREF="(.+?)">(.+?)</A>', reference).groups()
        embed.add_field(
            name=":book: Reference",
            value=f"[{text}]({requests.compat.urljoin(url, link)})",
        )
    i = 1
    while True:
        if attach := field.get(f"Attach{i}"):
            link, text = re.search(
                '<A HREF="(.+?)" TARGET="attach">(.+?)</A>', attach
            ).groups()
            embed.add_field(
                name=f":file_folder: Attach{i}",
                value=f"[{text}]({requests.compat.urljoin(url, link)})",
            )
            i += 1
        else:
            break
    return embed


def notify():
    hook = Webhook(os.environ["https://discord.com/api/webhooks/981461049880477767/ZHTInTq-95DszcQfpz0wWsS0BQWJhUCNLGGYZv50bI14U7hOv56y3YsRNtk6XYej6u1W"])

    # 記事一覧を取得
    year = now.year if (now := datetime.now()).month >= 4 else now.year - 1  # 年度
    url = f"{os.environ['BOARD_URL']}{year}/boards/new.html"
    try:
        articles_html = get_html(url)
        all_articles = re.findall('<A HREF="(.+?)"', articles_html)

        # 更新分の取得
        with open("latest", "r") as f:
            latest_article = f.read()
        if latest_article in all_articles:
            updated_articles = all_articles[: all_articles.index(latest_article)]
        else:
            hook.send("直近の掲示が削除されたため、最新の掲示を1つ通知します")
            updated_articles = [all_articles[0]]
        if not updated_articles:
            return

        # hook.send("@everyone")  # iPhoneで通知のバッチを付ける用
        for article in reversed(updated_articles):
            hook.send(embed=generate_embed(requests.compat.urljoin(url, article)))
    except Exception:
        hook.send(traceback.format_exc())
        return

    with open("latest", "w") as f:
        f.write(article)


if __name__ == "__main__":
    notify()
