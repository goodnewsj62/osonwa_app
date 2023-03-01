from collections import namedtuple

ScopedUrls = namedtuple("ScopedUrls", ["scope", "urls"])

NEWS_RSS_FEED_URLS = [
    r"https://www.techspot.com/backend.xml",
    r"https://appleinsider.com/rss/news/",
    r"https://thenextweb.com/feed",
    "https://www.techmeme.com/feed.xml?x=1",
    "https://www.theverge.com/rss/index.xml",
    "https://www.computerworld.com/index.rss",
    "https://feeds.washingtonpost.com/rss/business/technology",
    r"https://siliconangle.com/feed",
    r"https://vulcanpost.com/feed",
    r"http://feeds.arstechnica.com/arstechnica/technology-lab",
    r"https://lwn.net/headlines/newrss",
    r"https://erpinnews.com/feed/",
    r"https://erpnews.com/feed/",
]


AGILE_RSS_FEED_URLS = [
    r"https://www.leadingagile.com/blog/feed/",
    r"https://www.mountaingoatsoftware.com/blog/rss",
    r"https://kanbanzone.com/feed/",
    r"https://www.agilealliance.org/feed",
]

agile_urls_tuple = ScopedUrls("agile", AGILE_RSS_FEED_URLS)


VR_AR_RSS_FEED_URLS = [
    r"https://www.blog.google/products/google-ar-vr/rss/",
    r"https://www.vrfitnessinsider.com/feed/",
    r"http://vrscout.com/feed/",
    r"https://www.oculus.com/blog/rss/",
    r"http://skarredghost.com/feed/",
    r"https://uploadvr.com/feed/",
    r"https://www.roadtovr.com/feed/",
    r"https://blogs.nvidia.com/blog/category/virtual-reality/feed/",
    r"https://blogs.nvidia.com/blog/category/virtual-reality/feed/",
    "http://doc-ok.org/?feed=rss2",
    r"https://vrgames.io/feed/",
    r"https://www.roadtovr.com/feed/",
]

vr_ar_urls_namedtuple = ScopedUrls(
    "virtual reality augumented reality(VR/AR)", VR_AR_RSS_FEED_URLS
)

PRINTING_3D_RSS_FEED_URLS = [
    r"https://3dprintinguk.com/feed/",
    r"https://www.tctmagazine.com/api/rss/content.rss",
    r"https://www.3dprintingmedia.network/feed/",
    r"https://blog.prusa3d.com/feed/",
    r"https://3dprinting.com/news/feed/",
    r"https://3dprintingindustry.com/feed/",
    r"https://3duniverse.org/feed/",
    r"https://3dprint.com/feed/",
]


printing3d_urls_namedtuple = ScopedUrls("3d printing", PRINTING_3D_RSS_FEED_URLS)

GAME_DEV_RSS_FEED_URLS = [
    r"https://blog.unity.com/feed",
    "https://gameanalytics.com/feed/?x=1",
    r"https://askagamedev.tumblr.com/rss",
    r"https://askagamedev.tumblr.com/rss",
    r"https://blog.kongregate.com/rss/",
    r"https://klabater.com/feed/",
    r"http://game-wisdom.com/feed",
    r"https://www.gamedevelopment.blog/feed/",
    r"https://discuss.cocos2d-x.org/posts.rss",
    "https://gamedev.stackexchange.com/feeds?format=xml",
]


gamedev_urls_namedtuple = ScopedUrls("game development", GAME_DEV_RSS_FEED_URLS)

CYBER_SECURITY_RSS_FEED_URLS = [
    r"https://marcoramilli.com/feed/"
    r"https://tacsecurity.com/feed/"
    r"https://itsecuritycentral.teramind.co/feed/"
    r"https://cybersecurity.att.com/site/blog-all-rss"
    r"https://grahamcluley.com/feed/"
    r"https://www.darkreading.com/rss.xml"
    r"https://threatpost.com/feed/"
    r"https://nakedsecurity.sophos.com/feed/"
    "http://feeds.feedburner.com/TheHackersNews?format=xml"
    r"https://www.bleepingcomputer.com/rss-feeds/"
]

cybersecurity_urls_namedtuple = ScopedUrls(
    "cyber security", CYBER_SECURITY_RSS_FEED_URLS
)

WEB_DEV_RSS_FEED_URLS = [
    r"https://martinfowler.com/feed.atom",
    r"https://dev.to/feed",
    r"https://towardsdatascience.com/feed",
    r"https://pythonistaplanet.com/feed",
    r"https://www.geeksforgeeks.org/feed",
    r"https://stackoverflow.blog/feed",
    r"https://towardsthecloud.com/rss.xml",
    r"https://blog.codepen.io/feed/",
    r"https://davidwalsh.name/feed",
    r"https://www.sitepoint.com/sitepoint.rss",
    r"https://www.smashingmagazine.com/feed",
    r"https://www.tech4states.com/blogs/feed/",
    r"https://web.dev/feed.xml",
    r"https://djangostars.com/blog/feed/",
    r"http://blog.teamtreehouse.com/feed",
    r"https://www.pluralsight.com/blog.rss.xml",
    r"https://reactjs.org/feed.xml",
    r"https://blog.logrocket.com/feed/",
    r"https://cssauthor.com/feed/",
    r"https://www.syncfusion.com/blogs/feed",
]


webdev_urls_namedtuple = ScopedUrls("web development", WEB_DEV_RSS_FEED_URLS)

SCRAPE_URLS = [
    r"https://medium.com/tag/java",
    r"https://css-tricks.com",
    r"https://medium.com/tag/programming",
    r"https://www.digitalocean.com/community/tutorials",
    r"https://www.freecodecamp.org/news",
    r"https://medium.com/tag/go",
    # r"https://www.syncfusion.com/blogs",
    r"https://medium.com/tag/javascript",
    r"https://about.gitlab.com/blog/",
    r"https://medium.com/tag/python",
]


general_tags = [
    "web development",
    "cyber security",
    "game development",
    "3d printing",
    "agile",
]

post_fields = [
    "id",
    "post_id",
    "slug_title",
    "text_content",
    "title",
    "cover_image",
    "date_published",
    "author__username",
    "m_name",
    "author__profile__image",
]
article_fields = [
    "id",
    "gid",
    "slug_title",
    "description",
    "title",
    "image_url",
    "date_published",
    "website",
    "m_name",
    "logo_url",
]


icon_url_from_source = {
    "appleinsider": "https://photos5.appleinsider.com/v10/images/logo-2x.png",
    "thenextweb": "https://next.tnwcdn.com/assets/img/favicon/favicon-48x48.png",
    "techmeme": "https://techmeme.com/img/favicon.ico",
    "theverge": "https://www.theverge.com/icons/android_chrome_192x192.png",
    "washingtonpost": "https://www.washingtonpost.com/favicon.svg",
    "vulcanpost": "https://vulcanpost.com/wp-content/uploads/2021/09/logo-vulcan.png",
    "arstechnica": "https://cdn.arstechnica.net/favicon.ico",
    "erpinnews": "https://erpinnews.com/wp-content/uploads/2022/01/favicon-300x300.png",
    "erpnews": "https://erpnews.com/v2/wp-content/uploads/2018/11/mobile-logo-white@2x.png",
    "dev": "https://res.cloudinary.com/practicaldev/image/fetch/s--E8ak4Hr1--/c_limit,f_auto,fl_progressive,q_auto,w_32/https://dev-to.s3.us-east-2.amazonaws.com/favicon.ico",
}
