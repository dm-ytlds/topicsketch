import topicsketch.stream as stream
import logging
import re
from collections import defaultdict

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO)

class ReviewStreamFromFile(stream.ItemStream):
    def __init__(self, app):
        app_files = {
            "youtube": "/Users/jichuanzeng/Dropbox/ICSE'18/dataset/ios/youtube/total_info.txt",
        }
        app_file = app_files[app]
        self.is_android = False
        self.app_reviews = self.build_input(app_file)
        self.version_delta = None
        self.z = self.emit()

    def build_input(self, app_file):
        num_docs = 0
        timed_reviews = []
        with open(app_file) as fin:
            lines = fin.readlines()
        for l_id, line in enumerate(lines):
            line = line.strip()
            terms = line.split("******")
            if not self.is_android:  ## for ios
                date = terms[3]
                version = terms[4]
            else:  ## for android
                date = terms[2]
                version = terms[3]
            review_o = terms[1]
            rate = float(terms[0]) if re.match(r'\d*\.?\d+', terms[0]) else 2.0  # 2.0 is the average rate
            timed_reviews.append({"review": review_o, "date": date, "rate": rate, "version": version})
            num_docs += 1
            if l_id % 1000 == 0:
                logging.info("processed %d docs" % (l_id))
        logging.info("total read %d reviews." % (num_docs))

        # build ver_input
        ver_reviews = defaultdict(lambda: [])
        v_max = [0, 0, 0]
        v_min = [999, 999, 999]
        for item in timed_reviews:
            if item["version"] == "Unknown":
                continue
            ver_reviews[item["version"]].append(item)
            vs = list(map(int, item["version"].split(".")))
            for i, v in enumerate(vs):
                if v > v_max[i]:
                    v_max[i] = v
                if v < v_min[i]:
                    v_min[i] = v
        self.v_delta = [v1 - v2 for (v1, v2) in zip(v_max, v_min) if v1 - v2 > 0]
        return ver_reviews

    def ver2ts(self, ver):
        vs = list(map(int, ver.split(".")))
        rst = 0
        base = 10 * 24 * 3600
        for i, v in zip(range(len(self.v_delta) - 1, -1, -1), self.v_delta[::-1]):
            rst += vs[i] * base
            base *= self.v_delta[i]

        return rst

    def emit(self):
        for ver in sorted(self.app_reviews.iterkeys(), key=lambda s: map(int, s.split('.'))):
            if len(self.app_reviews[ver]) > 50:
                print("ver: %s, %s" % (ver, self.ver2ts(ver)))
                for item in self.app_reviews[ver]:
                    yield stream.RawReviewItem(self.ver2ts(item["version"]), item["review"])
        print("end of stream")
        yield stream.End_Of_Stream

    def next(self):
        return next(self.z)
