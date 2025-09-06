

from nltk import download as nltk_download
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class VaderSentimentAnalyzer:

    def __init__(self):
        self.download_data()

        self.intensity_analyzer = SentimentIntensityAnalyzer()
        pass

    def download_data(self):
        try:
            DOWNLOAD_DIR = '/selc_core/ml-model'
            nltk_download("stopwords", download_dir=DOWNLOAD_DIR)
            nltk_download("wordnet", download_dir=DOWNLOAD_DIR)
            nltk_download("vader_lexicon", download_dir=DOWNLOAD_DIR)
        except Exception:
            #when the model fails to download 
            pass

    def get_compound_score(self, score):

        if score >= 0.05:
            sentiment = "positive"
        elif score <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return sentiment

    def predict(self, text) -> str:
        
        scores = self.intensity_analyzer.polarity_scores(text)
        print(scores)

        sentiment = self.get_compound_score(scores['compound'])
        return sentiment
    

    def predict_multiple(self, texts: list[str]) -> list[str]:
        return [self.predict(text) for text in texts]
    
