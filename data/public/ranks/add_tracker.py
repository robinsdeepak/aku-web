import glob
code = """
<link rel="shortcut icon" type="image/png" href="https://bcebakhtiyarpur.org/wp-content/uploads/2019/01/logo-bced-f.png"/>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-145408212-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'UA-145408212-1');
</script>
"""


html = list(glob.glob("*html"))

for i in html:
    with open(i, "r") as f:
            nh = f.read().replace("</head>", code + "\n</head>")
    with open(i, "w") as f:
            f.write(nh)

