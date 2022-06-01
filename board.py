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
        embed.set_author(name=author.split("<")[0], icon_url=os.environ["FAVICON_URL"])
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
    hook = Webhook(os.environ["DISCORD_WEBHOOK_URL"])

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
