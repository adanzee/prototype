from crawler import crawl_page


url = "https://campaignme.com/hattan-perfumes-enters-the-uae-with-ai-video-launch-on-instagram"

text = crawl_page(url)

print(text[:5000])