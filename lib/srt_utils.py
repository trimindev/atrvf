import re


def read_srt_file(file_path):
    subtitles = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        index = 0
        while index < len(lines):
            # Bỏ qua các dòng trống
            while index < len(lines) and lines[index].strip() == "":
                index += 1

            if index >= len(lines):
                break

            # Trích xuất số thứ tự
            number = int(lines[index])
            index += 1

            # Trích xuất thời gian
            time_match = re.match(
                r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", lines[index]
            )
            start_time, end_time = time_match.group(1), time_match.group(2)
            index += 1

            # Trích xuất văn bản
            text = ""
            while index < len(lines) and lines[index].strip() != "":
                text += lines[index].strip() + " "
                index += 1

            # Thêm thông tin vào danh sách
            subtitles.append(
                {
                    "number": number,
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": text.strip(),
                }
            )

            index += 1

    return subtitles
