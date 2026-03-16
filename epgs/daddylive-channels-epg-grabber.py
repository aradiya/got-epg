import os
import gzip
import xml.etree.ElementTree as ET
import requests

name = "daddylive-channels"
save_as_gz = True  

output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "epgs")
os.makedirs(output_dir, exist_ok=True)  

tvg_ids_file = os.path.join(os.path.dirname(__file__), f"{name}-tvg-ids.txt")
output_file = os.path.join(output_dir, f"{name}-epg.xml")
output_file_gz = output_file + '.gz'

def fetch_and_extract_xml(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    if url.endswith('.gz'):
        try:
            decompressed_data = gzip.decompress(response.content)
            return ET.fromstring(decompressed_data)
        except Exception as e:
            print(f"Failed to decompress and parse XML from {url}: {e}")
            return None
    else:
        try:
            return ET.fromstring(response.content)
        except Exception as e:
            print(f"Failed to parse XML from {url}: {e}")
            return None

def filter_and_build_epg(urls):
    with open(tvg_ids_file, 'r') as file:
        valid_tvg_ids = set(line.strip() for line in file)

    root = ET.Element('tv')

    for url in urls:
        print(f"Fetching xml ({url})...")
        epg_data = fetch_and_extract_xml(url)
        if epg_data is None:
            continue

        for channel in epg_data.findall('channel'):
            tvg_id = channel.get('id')
            if tvg_id in valid_tvg_ids:
                print(f"tvg-id -> {tvg_id}")
                root.append(channel)

        for programme in epg_data.findall('programme'):
            tvg_id = programme.get('channel')
            if tvg_id in valid_tvg_ids:
                title = programme.find('title')
                if title is not None:
                    title_text = title.text if title is not None else 'No title'

                    if title_text == 'NHL Hockey' or title_text == 'Live: NFL Football':
                        subtitle = programme.find('sub-title')
                        subtitle_text = subtitle.text if subtitle else 'No subtitle'
                        programme.find('title').text = title_text + " " + subtitle_text

                    root.append(programme)

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"New EPG saved to {output_file}")

    if save_as_gz:
        with gzip.open(output_file_gz, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)
        print(f"New EPG saved to {output_file_gz}")


urls = [
    "https://www.open-epg.com/files/indonesia1.xml.gz",
    "https://www.open-epg.com/files/indonesia2.xml.gz",
    "https://www.open-epg.com/files/indonesia3.xml.gz",
    "https://www.open-epg.com/files/indonesia4.xml.gz",
    "https://www.open-epg.com/files/indonesia5.xml.gz",
    "https://www.open-epg.com/files/indonesia6.xml.gz",
    "https://viplink.biz/epgg.xml",
    "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
    "https://github.com/matthuisman/i.mjh.nz/raw/master/PlutoTV/all.xml.gz",
    "https://www.open-epg.com/files/singapore3.xml.gz",
    "https://viplink.biz/malaysia2_fixed.xml",
    "https://raw.githubusercontent.com/AqFad2811/epg/refs/heads/main/sooka.xml",
    "https://www.open-epg.com/files/canada1.xml",
    "https://www.open-epg.com/files/unitedkingdom1.xml",
    "https://www.open-epg.com/files/unitedstates1.xml.gz",
    "https://www.open-epg.com/files/unitedstates10.xml.gz",
    "https://www.open-epg.com/files/unitedstates11.xml.gz",
    "https://raw.githubusercontent.com/AqFad2811/epg/main/astro.xml",
	"https://raw.githubusercontent.com/ggwpmy/epg/refs/heads/main/epg.xml",
	"https://raw.githubusercontent.com/dbghelp/StarHub-TV-EPG/refs/heads/main/starhub.xml",
	"https://raw.githubusercontent.com/walpak1/epg/refs/heads/gh-pages/mana2.xml",
	"https://raw.githubusercontent.com/walpak1/epg/refs/heads/gh-pages/unifi.xml",
	"https://www.open-epg.com/files/indonesia2.xml",
    "https://www.open-epg.com/files/malaysia2.xml"
]

if __name__ == "__main__":
    filter_and_build_epg(urls)
