"""Builds the Placemaking Bangladesh website into dist/.

    python build.py

Content lives in content/*.json, page layouts in templates/*.html, and styles, scripts
and images in src/. Nothing but Python's standard library is needed. GitHub runs this
same script on every push (see .github/workflows/deploy.yml).
"""
import html, json, os, re, shutil, time

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
read = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()
data = lambda name: json.loads(read("content", name + ".json"))
esc = lambda s: html.escape(str(s), quote=True)

site, stories, posts, people = data("site"), data("stories"), data("posts"), data("people")

# slug, template, menu label, title, description
PAGES = [
    ("", "home", "Home", "Placemaking Bangladesh · Public space, shaped by its people",
     "A growing network of Bangladeshi individuals working for public spaces that are inclusive, accessible and alive with possibilities, for everyone."),
    ("stories", "stories", "Stories", "Stories · Placemaking Bangladesh",
     "Films and conversations from Placemaking Bangladesh: rickshaws, schools, displacement and what makes placemaking in South Asia its own."),
    ("blog", "blog", "Blog", "Blog · Placemaking Bangladesh",
     "Essays on placemaking in Bangladesh: vernacular architecture, local craft, tea stalls, ghats and the future of public life."),
    ("about-us", "about", "About Us", "About Us · Placemaking Bangladesh",
     "Placemaking Bangladesh is a collective movement carried forward by the people who shape space through daily life. Meet the initiators, advisors and advocates."),
    ("get-involved", "get-involved", None, "Get Involved · Placemaking Bangladesh",
     "Join Placemaking Bangladesh as a student, researcher, artist, architect, tea stall regular or curious passerby, or write to the team about a collaboration."),
]

ICON_PREV = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 3 5 9l6 6"/></svg>'
ICON_NEXT = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m7 3 6 6-6 6"/></svg>'
ICON_PLAY = '<svg width="18" height="18" viewBox="0 0 18 18" fill="#FBF7F0" aria-hidden="true"><path d="M5 2.5v13l11-6.5z"/></svg>'


def video_id(url):
    m = re.search(r"(?:youtu\.be/|[?&]v=|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})", url)
    if not m: raise SystemExit(f"content/stories.json: not a YouTube link: {url}")
    return m.group(1)


def story(s, level="h3", eager=False):
    vid, short = video_id(s["url"]), "/shorts/" in s["url"]
    return f"""<article class="story">
  <button class="play" data-video="{vid}" aria-label="Play: {esc(s['heading'])}">
    <img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" width="480" height="360" loading="{'eager' if eager else 'lazy'}">
    {'<span class="kind">Short</span>' if short else ''}<span class="disc">{ICON_PLAY}</span>
  </button>
  <{level}>{esc(s['heading'])}</{level}>
  <p>{esc(s['excerpt'])}</p>
</article>"""


def person(p, root):
    links = "".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a>' for t, u in p["links"])
    return f"""<article class="person">
  <div class="face"><img src="{root}img/{p['image']}" alt="Portrait of {esc(p['name'])}" width="520" height="520" loading="lazy"></div>
  <h3>{esc(p['name'])}</h3>
  <p>{esc(p['role'])}</p>
  <p class="study">{esc(p['study'])}</p>
  <div class="links">{links}</div>
</article>"""


def post(p, root, feature=False):
    cls, level = ("post feature", "h2") if feature else ("post", "h3")
    return f"""<article class="{cls}">
  <a class="thumb" href="{esc(p['url'])}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true"><img src="{root}img/{p['image']}" alt="{esc(p['alt'])}" width="1000" height="750" loading="{'eager' if feature else 'lazy'}"></a>
  <div class="post-copy">
    <{level}><a href="{esc(p['url'])}" target="_blank" rel="noopener">{esc(p['title'])}</a></{level}>
    <p class="by">{esc(p['author'])} · {esc(p['date'])}</p>
    <p>{esc(p['excerpt'])}</p>
    <a class="arrow-link" href="{esc(p['url'])}" target="_blank" rel="noopener">Read the essay<span class="sr">: {esc(p['title'])}</span></a>
  </div>
</article>"""


def partner(p, root):
    inner = f"""<span class="logo"><img src="{root}img/{p['image']}" alt="" width="400" height="400" loading="lazy"></span>
  <span class="partner-text"><strong>{esc(p['name'])}</strong><span>{esc(p['role'])}</span></span>"""
    if p["url"]:
        return f'<a class="partner" href="{esc(p["url"])}" target="_blank" rel="noopener">{inner}</a>'
    return f'<div class="partner">{inner}</div>'


def fill(template, values):
    def sub(m):
        key = m.group(1)
        if key not in values: raise SystemExit(f"Unknown placeholder {{{{{key}}}}}")
        return str(values[key])
    return re.sub(r"\{\{(\w+)\}\}", sub, template)


def render(slug, template, title, description, root, is_404=False):
    places = site["places"]
    current = ' aria-current="page"'
    nav = "".join(
        f'<a href="{root}{s + "/" if s else ""}"{current if s == slug and not is_404 else ""}>{label}</a>'
        for s, _, label, _, _ in PAGES if label)
    common = {
        "root": root, "slug": slug or "home", "title": esc(title), "description": esc(description),
        "site_url": site["url"], "canonical": f'{site["url"]}/{slug + "/" if slug else ""}',
        "email": site["email"], "address": esc(site["address"]), "form": site["form"],
        "more_videos": site["more_videos"], "version": VERSION, "nav": nav,
        "social": "".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a>' for t, u in site["social"]),
        "same_as": ",".join(json.dumps(u) for _, u in site["social"]),
        "icon_prev": ICON_PREV, "icon_next": ICON_NEXT,
        "head_extra": '<link href="https://fonts.googleapis.com/css2?family=Anek+Bangla:wght@700&display=swap" rel="stylesheet">' if template == "home" else "",
    }
    page = {
        "place_first": esc(places[0][0]), "place_first_gloss": esc(places[0][1]),
        "place_sentence": "A place can be " + ", ".join(esc(g) for _, g in places[:-1]) + " or " + esc(places[-1][1]) + ".",
        "places_json": json.dumps(places, ensure_ascii=False),
        "stories_rail": "\n".join(story(s, eager=i < 3) for i, s in enumerate(stories[:6])),
        "stories_feature": story(stories[0], "h2", eager=True) if stories else "",
        "stories_grid": "\n".join(story(s) for s in stories[1:]),
        "partners": "\n".join(partner(p, root) for p in site["partners"]),
        "post_feature": post(posts[0], root, True) if posts else "",
        "posts": "\n".join(post(p, root) for p in posts[1:]),
        "initiators": "\n".join(person(p, root) for p in people["initiators"]),
        "advisors": "\n".join(person(p, root) for p in people["advisors"]),
        "advocates": "\n".join(f"<li><b>{esc(n)}</b><span>{esc(r)}</span></li>" for n, r in people["advocates"]),
    }
    content = fill(read("templates", template + ".html"), {**common, **page})
    return fill(read("templates", "base.html"), {**common, "content": content})


def write(rel, text):
    path = os.path.join(DIST, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(text)


VERSION = time.strftime("%Y%m%d%H%M")
# Written over the previous build in place: a running preview server or a syncing
# folder can hold dist/ open, which makes deleting it first fail on Windows.
shutil.copytree(os.path.join(ROOT, "src"), DIST, dirs_exist_ok=True)

for slug, template, _, title, description in PAGES:
    write(os.path.join(slug, "index.html"), render(slug, template, title, description, "../" if slug else ""))

# GitHub Pages serves 404.html for any missing address, at any depth, so it uses absolute links.
write("404.html", render("404", "404", "Page not found · Placemaking Bangladesh", "This page has moved or never existed.", "/", True))

# The old Google Sites home address was /home; send it to the new home page.
write(os.path.join("home", "index.html"),
      f'<!doctype html><meta charset="utf-8"><title>Placemaking Bangladesh</title><link rel="canonical" href="{site["url"]}/"><meta http-equiv="refresh" content="0; url=../"><a href="../">Placemaking Bangladesh</a>')

today = time.strftime("%Y-%m-%d")
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f'  <url><loc>{site["url"]}/{s + "/" if s else ""}</loc><lastmod>{today}</lastmod></url>\n' for s, *_ in PAGES) + "</urlset>\n")
write("robots.txt", f'User-agent: *\nAllow: /\nSitemap: {site["url"]}/sitemap.xml\n')
write(".nojekyll", "")
if os.path.exists(os.path.join(ROOT, "CNAME")): shutil.copy(os.path.join(ROOT, "CNAME"), DIST)

print(f"Built {len(PAGES)} pages, {len(stories)} stories, {len(posts)} posts into dist/")
