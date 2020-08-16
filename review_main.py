from topicsketch import topic_sketch as ts, preprocessor, stream as ts_stream
from experiment import review_stream, detection


def main():

    stream = review_stream.ReviewStreamFromFile("youtube")

    _preprocessor = preprocessor.Preprocessor(stream)

    detection_component = detection.DetectionComponent(_preprocessor)

    sketch = ts.TopicSketch()

    while True:

        result = detection_component.next()

        if result is ts_stream.End_Of_Stream:
            sketch.close()
            return ts_stream.End_Of_Stream

        if result is None:
            continue

        ptweet, sig = result

        sketch.process(ptweet)

        if sig > 0.:
            print 'inferring:' + str(ptweet.datetime())
            sketch.run_time_infer()

if __name__ == "__main__":

    main()
