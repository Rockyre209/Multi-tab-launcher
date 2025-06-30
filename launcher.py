import webbrowser
import os
import time
import subprocess
import urllib.parse  # For safe URL encoding

# Firefox path my sweet hacker 🦊
firefox_path = "C:/Program Files/Mozilla Firefox/firefox.exe"

# Flirty little menu 😚
def show_menu():
    print("\nWelcome to your naughty launcher, baby 😈💻")
    print("Choose what you’re craving today~ 💋")
    print("1. Cracked Software")
    print("2. Cracked Games")
    print("3. Movies (GDrive Links)")
    print("4. Movies (Direct Download)")
    print("5. Movies (Torrent Sites)")
    print("6. VFX / Design / Pro Softwares")
    print("0. Exit 😢")

# The hot tab opener 💦
def run_search(sites, raw_keyword, special_handler=None):
    if not raw_keyword:
        print("You forgot to whisper your desire, darling 😳")
        return

    query = urllib.parse.quote_plus(raw_keyword)
    special_query = urllib.parse.quote(raw_keyword) if special_handler else query

    if not os.path.exists(firefox_path):
        print("Firefox isn’t there, baby 💔 Check her path again")
        return

    print("\nWaking up Firefox for you, my sweet tech king 🦊💋")
    subprocess.Popen(f'"{firefox_path}"')
    time.sleep(2)
    browser = webbrowser.get(f'"{firefox_path}" %s')

    for i in range(0, len(sites), 5):
        for site in sites[i:i + 5]:
            search_term = special_query if special_handler and special_handler in site else query
            browser.open_new_tab(site.format(search_term))
            time.sleep(0.5)
        if i + 5 < len(sites):
            input("Press Enter to open more sinful tabs 😈")
        else:
            print("All done, my king 💻💋 Go enjoy your treasures~")

# Your naughty site list 💻🍓
sites = {
    1: [
        "https://getintopc.com/?s={}",
        "https://repack.me/?s={}",
        "https://realsoftpc.com/?s={}",
        "https://mawtoload.com/?s={}",
        "https://www.thepiratecity.co/?s={}",
        "https://crackingpatching.com/search/{}",
        "https://haxpc.net/?s={}",
        "https://gigapurbalingga.net/?s={}",
        "https://dlcrack.com/?s={}",
        "https://thepiratebay.org/search.php?q={}",
        "https://crackhomes.com/?s={}",
        "https://softprober.com/?s={}",
        "https://startcrack.com/?s={}",
        "https://procracksoftwares.com/?s={}",
        "https://haxnode.net/?s={}",
        "https://katzdownload.com/?s={}",
        "https://pcwonderland.com/?s={}",
        "https://4realtorrentz.com/?s={}"
    ],
    2: [
        "https://dodi-repacks.site/?s={}",
        "https://elamigos.site/?s={}",
        "https://fitgirl-repacks.site/?s={}",
        "https://steamunlocked.net/?s={}",
        "https://steamrip.com/?s={}",
        "https://gamesdrive.net/?s={}",
        "https://gamebounty.world/?s={}",
        "https://g4u.to/?s={}",
        "https://gamesleech.com/?s={}",
        "https://gamingbeasts.com/?s={}",
        "https://www.gog-games.to/?s={}",
        "https://rentry.org/pgames#game-search-engines",
        "https://repack-games.com/?s={}"
    ],
    3: [
        "https://olamovies.help/?s={}",
        "https://uhdmovies.tips/?s={}",
        "https://bollyflix.promo/?s={}",
        "https://themoviesflix.ae.org/?s={}",
        "https://www.1tamilmv.kim/index.php?/search/&q={}%20tamil%20gdrive&quick=1&search_and_or=and&sortby=relevancy",
        "https://katmoviehd.nexus/?s={}",
        "https://hdmovie2.spot/?s={}",
        "https://pahe.ink/?s={}",
        "https://katmovie4k.org/?s={}",
        "https://themoviesflix.email/?s={}",
        "https://moviesmod.email/?s={}",
        "https://themoviesflix.ag/?s={}",
        "https://topmovies.tips/?s={}",
        "https://app.vegamovies.bot/?s={}",
        "https://vegamovie.town/?s={}",
        "https://hdmovie2.free/?s={}",
        "https://privatemoviez.info/?s={}"
    ],
    4: [
        "https://bollyflix.fo/?s={}",
        "https://filmygood.com/?s={}",
        "https://streamblasterss.com/hollywood-movies/?s={}",
        "https://katmoviehd.blue/?s={}",
        "https://megaddl.co/?s={}",
        "https://movieparadise.org/?s={}",
        "https://moviiezverse.com/?s={}",
        "https://mp4moviiez.com/?s={}",
        "https://psa.wf/?s={}",
        "https://rarefilmm.com/?s={}",
        "https://m.stagatv.com/?s={}",
        "https://streamblasterss.com/?s={}",
        "https://vegamovies.md/?s={}",
        "https://en.mkvcinema-official.com/?s={}",
        "https://yts-official.mx/?s={}"
    ],
    5: [
        "https://www.thenextplanet.me/?s={}",
        "https://mkvcinema-official.lol/stream/?s={}",
        "https://www.1tamilmv.ms/?s={}",
        "https://en.eztv-official.com/?s={}",
        "https://www.5movierulz.srl/?s={}",
        "https://www.1tamilblasters.earth/?s={}",
        "https://torrentgalaxy-official.com/?s={}",
        "https://ext.to/?s={}",
        "https://torrentz.eu.com/#gsc.tab=0&s={}",
        "https://bitsearch.to/?s={}",
        "https://magnetdl.skin/?s={}",
        "https://magnetdl.hair/?s={}",
        "https://www.torlock.com/?s={}",
        "https://kickasstorrents.to/?s={}",
        "https://kick4ss.com/?s={}",
        "https://limetorrent.net/?s={}",
        "https://www.limetorrents.lol/home?s={}",
        "https://rargb.to/?s={}",
        "https://yts.unblockit.mov/?s={}",
        "https://www2.thepiratebay3.to/?s={}",
        "https://thepiratebay.org/index.html?s={}",
        "https://www.1337x.to/home?s={}"
    ],
    6: [
        "https://vfxdownload.net/?s={}",
        "https://pesktop.com/search/?q={}",
        "https://www.vfxmed.com/?s={}",
        "https://www.gfxcamp.com/?s={}",
        "https://3dzip.org/?s={}",
        "https://grabcad.com/library/software/nx?query={}",
        "https://clara.io/search?q={}",
        "https://www.nukepedia.com/search/node/{}",
        "https://mysoftwarefree.com/?s={}",
        "https://cgpersia.com/?s={}",
        "https://gfxfather.com/?s={}",
        "https://cgdownload.ru/catalog/?search={}",
        "https://cgdownload.ru/?s={}",
        "https://www.blendernation.com/?s={}",
        "https://igetintopc.com/?s={}",
        "https://render-state.to/?s={}",
        "https://intro-hd.net/?s={}",
        "https://filecr.com/en/?s={}",
        "https://www.downloadpirate.com/?s={}",
        "https://extensions.blender.org/?s={}"
    ]
}

# Entry point, sugar 🍬
if __name__ == "__main__":
    while True:
        show_menu()
        try:
            choice = int(input("\nType your choice, lover: "))
        except ValueError:
            print("Oopsie~ That wasn’t a number, my cutie 😅")
            continue

        if choice == 0:
            print("Okay baby 💔 Come back when you wanna play again~")
            break
        elif choice in sites:
            keyword = input("What are we hunting today, love? 🔍: ").strip()
            special_handler = "1tamilmv" if choice == 3 else None
            run_search(sites[choice], keyword, special_handler)
        else:
            print("That’s not on the list, silly 😘 Try again~")
