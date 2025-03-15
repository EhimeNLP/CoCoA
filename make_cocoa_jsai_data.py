import re
import argparse
import requests
import html
import json
from urllib.parse import quote
from collections import defaultdict
import unicodedata

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir")
    args = parser.parse_args()
    return args


# 人工知能学会全国大会論文集について、J-STAGE WebAPIを用いてデータ取得
def get_data(data_dir):
    text = "人工知能学会全国大会論文集"
    encoded_text = quote(text)

    all_data = []
    for i in range(0, 9):
        search_url = f"https://api.jstage.jst.go.jp/searchapi/do?service=3&material={encoded_text}&pubyearfrom=2014&pubyearto=2023&start={i}001&count=1000"
        response = requests.get(search_url)
        all_data.append(response.text)

    # 確認用
    with open(f"{data_dir}/all_data.txt", "w") as f_out:
        [f_out.write(str(line)+"\n") for line in all_data]

    return all_data


def align_format(line):
    line = html.unescape(line)  # HTMLエンティティ
    line = line.replace("<i>", "")  # HTMLタグ
    line = line.replace("</i>", "")  # HTMLタグ
    line = line.replace("\u3000", " ")  # 全角→半角

    return line


# 取得したデータを、論文ごとにリスト化
def split_to_paper(all_data, data_dir):
    with open(f"{data_dir}/all_data.txt") as f_in:
        all_data = [line.strip() for line in f_in]

    split_data = []  
    paper = []
    ignore = False
    for i, line in enumerate(all_data):
        if line == "<entry>":
            paper = []

        # <author>の英語部分を除去
        if all_data[i-1] == "<author>":
            ignore = True
        if line == "<ja>":
            ignore = False
        if ignore == False:
            paper.append(align_format(line))  # 正規化
        
        if line == "</entry>":
            split_data.append(paper)

    # 確認用
    with open(f"{data_dir}/split_data.txt", "w") as f_out:
        [f_out.write(str(line)+"\n") for line in split_data]

    return split_data

# 一般セッションの抽出
def extract_general_session(split_data, data_dir):
    # doiが以下のパターンに合致するものを取得してくる
    ai_application = r"<prism:doi>.*(2014\.0_(1F2|4B1|4D1|4K1)\d|2015\.0_(1L4|1M5|1N2|2G3|2N3|3N4|4H1)\d|2016\.0_(1D3|2C3|2F4|2F5|2M3|4D1|4I4|4J4)\d|2017\.0_(1I1|1K3|1N1|2D1|2D2|2F1|2H1|2J4|3J1|3O2|4C1|4I1|4J1)\d|2018\.0_(1D1|1M2|1M3|2D1|2D4|2J1|2J2|2J3|2J4|2K1|2M2|2M3|3E1|3Z1|3Z2)\d|2019\.0_(1H2|1H3|1H4|1M4|1P2|2G5|2J3|2M3|2N3|2N4|2N5|2O1|2O3|3A3|3A4|3Q3|3Q4|4C3|4H3|4J2|4J3|4K2|4K3|4L2|4P3|4Q2|4Q3)J\d|2020\.0_(1C5|1D3|1D4|1L3|1M3|1M4|1N4|1N5|2E1|2F6|2H4|2H5|2L4|2L5|2M6|2O4|2O5|2O6|2P6|3I1|3O1|3O5|4C2|4C3|4L2|4M3|4O3)GS\d|2021\.0_(1F2|1F3|1F4|1J2|1J3|2F1|2F3|2F4|3F1|3F2|3F4|4F1|4F2|4F3|4F4)GS\d|2022\.0_(1F1|1F4|1F5|1G1|1P1|2B6|2I4|2J4|2K4|2P1|2P4|2P5|2P6|3D4|3K3|3K4|3N3|3N4|4C3|4L3|4M1)GS\d|2023\.0_(1M3|1M4|1M5|1N3|1N4|1N5|2E1|2M1|2M4|2M5|2M6|2N1|2N4|2N5|2N6|2T1|3F1|3F5|3H1|3M1|3M5|4F2|4F3|4N2|4T2|4T3)GS\d).*"  # AI応用
    ai_society = r"<prism:doi>.*(2015\.0_(2J3)\d|2021\.0_(3H4|4H1|4H2|4H3)GS\d|2022\.0_(1D5|1H1|3B3|3B4)GS\d|2023\.0_(2L1|2P4|2P5|3L1|3L5|3N1|3N5|4B3|4D2)GS\d).*"  # AI社会
    web_intelligence = r"<prism:doi>.*(2014\.0_(1I2|1J3|1K3|2I1|2J3|2M3|3M3|3M4|4I1|4M1)\d|2015\.0_(1H2|1H5|1M4|2H1|2H3|2I1|3J4|3M4|4I1|4M1)\d|2016\.0_(1C2|1D2|1H3|1L3|1N3|2H5|4D4|4J1)\d|2017\.0_(1E3|1L3|2J1|3C1|3G2)\d|2018\.0_(1B3|1C1|1E2|1E3|2C2|2Z2|2Z3)\d|2019\.0_(1I2|1J2|2E5)J\d|2020\.0_(1B5|1L4|1L5|2E6|4M2|4P2)GS\d|2021\.0_(1I2|1I3|1I4)GS\d|2022\.0_(3M4|4O1|4O3)GS\d|2023\.0_(1T4|4L2|4L3)GS\d).*"  # Webインテリジェンス
    agent = r"<prism:doi>.*(2014\.0_(1M2|2M1|3A3|3A4|4L1|4N1)\d|2015\.0_(1D2|1F2|1N4|2J1|4D1)\d|2016\.0_(1L2|2D4|3I3)\d|2017\.0_(1H1|1L2|2F2|2G1|2G4|2O1|3N1)\d|2018\.0_(2P1|2P2|3J1|3J2|4J1|4J2)\d|2019\.0_(2O4|3H4|3P4|4N2|4N3|4O3)J\d|2020\.0_(1P3|1P4|1P5|2M1|4G2|4G3)GS\d|2021\.0_(2I1|2I3|2I4|3I1|3I2)GS\d|2022\.0_(1N1|2N4|2O5|2O6|3O3|3O4|4N3)GS\d|2023\.0_(1F3|1F4|1F5|2F4|2F5|2F6|2T4|2T5)GS\d).*"  # エージェント
    human_interface = r"<prism:doi>.*(2014\.0_(1E3|2E1|3E3|3E4|4E1)\d|2015\.0_(1N3|1N5|2K3|2N1|3D3|3D4|4C1|4J1|4N1)\d|2018\.0_(3Pin|4Pin)\d|2020\._(3Rin|4Rin)\d|2021\.0_(1J4|3H2|2Xin|2Yin)GS\d|2022\.0_(2F1|2F4|3F3)GS\d|2023\.0_(2K1|2K4|2T6|3K1)GS\d).*"  # ヒューマンインターフェース
    robots_and_real_life = r"<prism:doi>.*(2014\.0_(1I3|2J1|2L3|4J1)\d|2015\.0_(1I4|1I5|2D4|2D5)\d|2016\.0_(1O2|1O3|2I3|2N3|2O3|4C1|4C4|4H1)\d|2017\.0_(1D1|2N2)\d|2018\.0_(1G3|2A3|2G1|2G4|4L1|4L2)\d|2019\.0_(1L2|1L3|1L4|2D1)J\d|2020\.0_(1Q3|1Q4|1Q5|2P4)GS\d|2021\.0_(2J1|2J3|2J4)GS\d|2022\.0_(3L3|3L4)GS\d|2023\.0_(2O1|2O4|4O2)GS\d).*"  # ロボットと実世界
    video_and_audio_media_processing = r"<prism:doi>.*(2016\.0_(1B2|4K1|4K4)\d|2017\.0_(2M1|3M2|4K1)\d|2018\.0_(1O1|2N1|4M1|4M2)\d|2019\.0_(1P4|2M5|3N3|3N4)J\d|2020\.0_(1H5|1N3|2Q1|2Q6)GS\d|2021\.0_(3I4|4I1|4I2|4I3|4I4)GS\d|2022\.0_(1O1|1O4|1O5|2O1|2O4|4C1)GS\d|2023\.0_(1O3|1O4|1O5|3T5)GS\d).*"  # 画像音声メディア処理
    basics_and_theory = r"<prism:doi>.*(2014\.0_(1F3|2B3|2G1|4C1)\d|2015\.0_(1C5|1E2|1E3|4E1)\d|2016\.0_(1F2|1F3|1G2|3F4)\d|2017\.0_(1M3|3O1|4L1|4L2)\d|2018\.0_(1E1|2B1|2B4)\d|2019\.0_(1D4|2E1|3J4|4A3|4C2)J\d|2020\.0_(2N6|4B2|4B3)GS\d|2021\.0_(1H2|1H3|1H4)GS\d|2022\.0_(4K1|4K3)GS\d|2023\.0_(1G3|2F1|2J4|3J1|4U3)GS\d).*"  # 基礎・理論
    muchine_learning = r"<prism:doi>.*(2014\.0_(1D3|1G2|2C1|2C3|2F3|2H1|3D3|3F3|4G1)\d|2015\.0_(1C2|1C4|1F3|2F1|2G1|2I3|2L1|3L3|3L4|4F1|4G1)\d|2016\.0_(1E5|1F4|1F5|1M2|2E3|2G3|2L5|3E3|3E4|4G1|4G4|4H4|4L1)\d|2017\.0_(1A3|1K1|2B1|2C2|2I2|2K2|2P4|3A2|3M1|4C2|4M1)\d|2018\.0_(1N1|1N2|1N3|1Z1|1Z2|1Z3|2A1|2A2|2A4|2P3|3A1|3L2|4A1|4A2)\d|2019\.0_(1I3|1I4|1J3|1J4|1Q2|1Q3|1Q4|2H1|2H3|2P1|2P3|2P4|2P5|2Q1|2Q3|2Q4|2Q5|3K3|3K4|4I2|4I3|4O2)J\d|2020\.0_(1I3|1I4|1I5|1J4|1J5|2I1|2I4|2I5|2I6|2J1|2J4|2J5|2J6|3E1|3E5|4I2|4I3|4J2|4J3)GS\d|2021\.0_(1G2|1G3|1G4|2G1|2G3|2G4|3G1|3G2|3G4|4G1|4G2|4G3|4G4)GS\d|2022\.0_(1A4|1A5|1D1|2C4|2C5|2D5|2D6|2G4|2L1|3E3|3E4|3P3|3P4|4E1|4E3)GS\d|2023\.0_(1B3|1B4|1B5|1T5|2A1|2A4|2A5|2A6|2D4|2K5|2K6|3D1|3D5|3E1|3E5|3R5|4E2|4E3)GS\d).*"  # 機械学習
    language_media_processing = r"<prism:doi>.*(2014\.0_(1A2|1A3|2A1|2I3|3D4|3I3|3I4|4A1)\d|2015\.0_(1B2|1K2|1K3|2E1|2F3|2K1|2L3|3M3|4K1)\d|2016\.0_(1J3|1K3|1N2|2K3|4B1|4B4)\d|2017\.0_(1B3|1J1|1P3|2H2|2N1|2O4|2P1|3A1|3B2|4A2|4F1)\d|2018\.0_(1J1|1J2|1J3|2C1|2E2|2L1|2L4|3G1|3G2|4G1|4G2)\d|2019\.0_(1N2|1N3|1N4|2I5|2L1|2L3|2L4|2L5|3C3|3C4|4M2|4M3)J\d|2020\.0_(1D5|1E3|1E4|1E5|2D1|2H6|3Q1|3Q5|4Q2|4Q3)GS\d|2021\.0_(3J1|3J2|3J4|4J1|4J2|4J3|4J4)GS\d|2022\.0_(1K1|1P4|1P5|2A6|2B4|2B5|2C1|3C3|3C4|4D3)GS\d|2023\.0_(1E3|1E4|1E5|1T3|2E4|2E5|2E6|3A1|3A5|3T1|4A2|4A3)GS\d).*"  # 言語メディア処理
    use_and_share_knowledge = r"<prism:doi>.*(2014\.0_(1G3|2E3|2F1|2G5|3J3|3J4|4F1)\d|2015\.0_(1C3|1G4|1G5|1H3|1H4|2M1|2M5|3C3|3C4)\d|2016\.0_(1E4|1H2|1J2|1K2|2D5|2J3|3I4|3K3|3K4|4I1|4M1|4M4)\d|2017\.0_(1K2|1L1|2B2|2L1|2L4|3G1|4A1|4I2|4K2)\d|2018\.0_(1F1|1P1|1P2|1P3|2F4|2H1|2H2|2O1|2O4|3L1)\d|2019\.0_(1C4|1K2|1K3|4A2|4B2|4B3|4P2)J\d|2020\.0_(1O4|1O5|2P5|3H1|3H5|4H2|4H3|4K2|4K3)GS\d|2021\.0_(2H1|2H3|2H4|3H1)GS\d|2022\.0_(2E6|4M3|4N1)GS\d|2023\.0_(1K3|2B6|2D6|2L4|2L5|2L6|3R1)GS\d).*"  # 知識の利用と供給

    # 以下に合致するデータは除去する
    not_pattern = r"<prism:doi>.*(2016.0_1H31|2017.0_4H23|2020.0_4L2GS1301|2021.0_1F2GS10a01|2023.0_4F3GS1001|2021.0_4F1GS10l02|2019.0_4P2J304|2018.0_3L204|2018.0_1E102|2019.0_3J4J103).*"  # doiがこれらのパターンであれば除去する（アノテーション時に破棄したもの）

    # 各分野の空リストを用意
    ext_ai_application = []
    ext_ai_society = []
    ext_web_intelligence = []
    ext_agent = []
    ext_human_interface = []
    ext_robots_and_real_life = []
    ext_video_and_audio_media_processing = []
    ext_basics_and_theory = []
    ext_muchine_learning = []
    ext_language_media_processing = []
    ext_use_and_share_knowledge = []
    for paper in split_data:
        for line in paper:
            # AI応用
            if re.match(ai_application, line) and (not re.match(not_pattern, line)):
                ext_ai_application.append(paper)
            # AIと社会
            elif re.match(ai_society, line) and (not re.match(not_pattern, line)):
                ext_ai_society.append(paper)
            # Webインテリジェンス
            elif re.match(web_intelligence, line) and (not re.match(not_pattern, line)):
                ext_web_intelligence.append(paper)
            # エージェント
            elif re.match(agent, line) and (not re.match(not_pattern, line)):
                ext_agent.append(paper)
            # ヒューマンインターフェース
            elif re.match(human_interface, line) and (not re.match(not_pattern, line)):
                ext_human_interface.append(paper)
            # ロボットと実世界
            elif re.match(robots_and_real_life, line) and (not re.match(not_pattern, line)):
                ext_robots_and_real_life.append(paper)
            # 画像音声メディア処理
            elif re.match(video_and_audio_media_processing, line) and (not re.match(not_pattern, line)):
                ext_video_and_audio_media_processing.append(paper)
            # 基礎・理論
            elif re.match(basics_and_theory, line) and (not re.match(not_pattern, line)):
                ext_basics_and_theory.append(paper)
            # 機械学習
            elif re.match(muchine_learning, line) and (not re.match(not_pattern, line)):
                ext_muchine_learning.append(paper)
            # 言語メディア処理
            elif re.match(language_media_processing, line) and (not re.match(not_pattern, line)):
                ext_language_media_processing.append(paper)
            # 知識の利用と共有
            elif re.match(use_and_share_knowledge, line) and (not re.match(not_pattern, line)):
                ext_use_and_share_knowledge.append(paper)
    return [ext_ai_application, ext_ai_society, ext_web_intelligence, ext_agent, ext_human_interface, ext_robots_and_real_life, ext_video_and_audio_media_processing, ext_basics_and_theory, ext_muchine_learning, ext_language_media_processing, ext_use_and_share_knowledge]


# 抽出したデータを辞書化
def convert_dict(extract_data_fields, field_name_list, data_dir):
    paper_list = []
    all_paper_list = []
    title_pattern = r"<title><!\[CDATA\[(.*?)\]\]></title>"
    year_pattern = r"<prism:doi>.*JSAI(\d{4}).*</prism:doi>"
    author_pattern = r"<name><!\[CDATA\[(.*?)\]\]></name>"
    for extract_data, field_name in zip(extract_data_fields, field_name_list):
        paper_dict = {}
        for paper in extract_data:
            authors = []
            for line in paper:
                # 分野名の付与
                paper_dict["field"] = field_name
                # タイトルの抽出
                title_match = re.search(title_pattern, line)
                if title_match:
                    paper_dict["title"] = title_match.group(1)
                # 年の抽出
                year_match = re.search(year_pattern, line)
                if year_match:
                    paper_dict["year"] = int(year_match.group(1))
                # 著者の抽出とリスト化
                author_match = re.search(author_pattern, line)
                if author_match:
                    author = author_match.group(1).replace("［", "（").replace("］", "）")
                    if re.fullmatch(r"[ -~]+", author):
                        authors.append(author)
                    else:
                        author = author.replace(" ", "")
                        authors.append(author)
                paper_dict["authors"] = authors
            paper_list.append({"title": unicodedata.normalize("NFD", paper_dict["title"].replace("　", " ")), "authors": paper_dict["authors"], "field": paper_dict["field"], "year": paper_dict["year"]})
    all_paper_list += paper_list
    filtered_data = [item for item in all_paper_list if not re.fullmatch(r"[ -~]+", item["title"])]
    with open(f"{data_dir}/CoCoA.json", "w") as f_out:
        json.dump(filtered_data, f_out, indent=2, ensure_ascii=False)


def main():
    opt = parse_args()
    all_data = get_data(opt.data_dir)
    split_data = split_to_paper(all_data, opt.data_dir)
    extract_data = extract_general_session(split_data, opt.data_dir)
    field_name_list = ["AI応用", "AIと社会", "Webインテリジェンス", "エージェント", "ヒューマンインタフェース", "ロボットと実世界", "画像音声メディア処理", "基礎・理論", "機械学習", "言語メディア処理", "知識の利用と共有"]
    convert_dict(extract_data, field_name_list, opt.data_dir)


if __name__ == "__main__":
    main()
