# Placemaking Bangladesh website

The source for www.placemakingbangladesh.org. GitHub builds and publishes the site
automatically every time something on the `main` branch changes; it is live about a
minute later.

## Changing content

Most changes are one small file, and can be made in the browser on github.com: open the
file, click the pencil, edit, then **Commit changes**.

| To change | Edit |
|---|---|
| Stories (YouTube videos, headings, excerpts) | `content/stories.json` |
| Blog posts | `content/posts.json` |
| Initiators, advisors, advocates | `content/people.json` |
| Partners, address, email, social links, the "A place can be" words | `content/site.json` |
| Wording on a page | `templates/home.html`, `stories.html`, `blog.html`, `about.html`, `get-involved.html` |
| Page titles and search descriptions | the `PAGES` list at the top of `build.py` |
| Colours, type, layout | `src/css/site.css` |
| Pictures | `src/img/` |

### Add a story

In `content/stories.json`, copy one block, paste it at the top of the list and fill it
in. The first story in the list is the large one on the Stories page, and the first six
show on the home page. Any YouTube link works, Shorts included.

```json
  {
    "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
    "heading": "The title shown under the video",
    "excerpt": "One or two sentences about it."
  },
```

Mind the commas: every block ends with one except the last.

### Add a blog post

Same idea in `content/posts.json`. Put the picture in `src/img/` first (about 1000 px
wide) and give its file name as `image`. The first post in the list is the large one.

## Working on it locally

Only Python 3 is needed.

```
python build.py
```

This writes the finished site to `dist/`. Open it through any local web server, for
example `npx http-server dist`.

## How it is published

`.github/workflows/deploy.yml` runs `python build.py` and publishes `dist/` to GitHub
Pages. In the repository's **Settings > Pages**, **Source** must be set to
**GitHub Actions**.

### Custom domain

1. Add a file named `CNAME` in the top folder containing one line:
   `www.placemakingbangladesh.org`
2. At the domain registrar, point the `www` record (CNAME) at `<owner>.github.io`.
3. In **Settings > Pages**, enter the domain and tick **Enforce HTTPS** once it is offered.

Until the domain is switched, the site is available at
`https://<owner>.github.io/<repository>/`; every link inside it is relative, so it works
at either address.

## Credits

Illustration on the home page: Kazi Md. Tahmid, Stories on Three Wheels, 2026.
Photographs: Healing Space exhibition, Claymire and Placemaking Bangladesh.
Typefaces: Sora and Epilogue (Fontshare), Anek Bangla (Google Fonts).
