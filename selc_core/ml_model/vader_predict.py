

import nltk
from nltk import download as nltk_download
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class VaderSentimentAnalyzer:

    def __init__(self):

        try:
            self.download_data()
        except: 
            pass

        #nltk.data.path.append("/opt/render/project/src/nltk_data") #used in the product evironment

        self.intensity_analyzer = SentimentIntensityAnalyzer()
        pass

    def download_data(self):
        try:
            #DOWNLOAD_DIR = 'selc_core/ml-model/nltk_download'

            # Add the directory to nltk search path (before any lookup)
            #nltk.data.path.append(DOWNLOAD_DIR)

            # Check and download each resource only if not available
            required_packages = ["stopwords", "wordnet", "vader_lexicon"]

            for pkg in required_packages:
                try:
                    nltk.data.find(f"{pkg}")
                    print(f"✓ NLTK resource '{pkg}' already exists.")
                except LookupError:
                    print(f"⤵ Downloading NLTK resource: {pkg}")
                    #nltk_download(pkg, download_dir=DOWNLOAD_DIR)
                    nltk_download(pkg, quiet=True)

        except Exception as e:
            print("⚠ NLTK data setup failed:", e)
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
    
