from pathlib import Path

# Preserve 3.0.28 UI/focus behavior and bump this enhanced multi-source lookup build.
b=Path('app/build.gradle')
g=b.read_text()
for old in ('30028','30027','30026','30025','30024','30023'):
    g=g.replace('versionCode '+old,'versionCode 30029')
for old in ('3.0.28','3.0.27','3.0.26','3.0.25','3.0.24','3.0.23'):
    g=g.replace("versionName '"+old+"'","versionName '3.0.29'")
b.write_text(g)
