from collections import Counter
import tweepy
from retexto import ReTexto


class ResponseService:
    has_error = False
    message = None
    response = []
    author = None
    terms = None

    def __init__(
            self,
            has_error: bool,
            message: str,
            author: str,
            terms: str,
            response: []
    ):
        self.has_error = has_error
        self.message = message
        self.author = author
        self.terms = terms
        self.response = response

    def to_dict(self):
        return {
            'has_error': self.has_error,
            'message': self.message,
            'author': self.author,
            'terms': self.terms,
            'response': self.response
        }


def get_words(sentence: str) -> set:
    text = ReTexto(sentence)
    return text.remove_html() \
        .remove_mentions() \
        .remove_tags() \
        .remove_smiles(by='SMILING') \
        .convert_specials() \
        .convert_emoji() \
        .remove_nochars(preserve_tilde=True) \
        .remove_url() \
        .remove_punctuation(by=' ') \
        .remove_multispaces() \
        .lower() \
        .remove_stopwords() \
        .split_words()


class TwitterService:
    def __init__(
            self,
            tw_consumer_key: str,
            tw_consumer_secret: str,
            tw_access_key: str,
            tw_access_secret: str
    ):
        auth = tweepy.auth.OAuthHandler(tw_consumer_key, tw_consumer_secret)
        auth.set_access_token(tw_access_key, tw_access_secret)
        api = tweepy.API(auth)
        self.api = api

    def search_term(self, terms: str, author: str):
        if len(terms.strip()) <= 3:
            return ResponseService(
                has_error=True,
                author=author,
                terms=terms,
                message='termino de busqueda demasiado corto',
                response=[]
            )

        if len(terms.strip()) > 32:
            return ResponseService(
                has_error=True,
                author=author,
                terms=terms,
                message='termino de busqueda demasiado largo',
                response=[]
            )

        query_term = terms.lower().strip()
        search_results = self.api.search(
            q=query_term,
            count=100,
            lang='es',
            result_type='recent',
            tweet_mode='extended'
        )

        corpus = []
        if len(search_results):
            for status in search_results:
                try:
                    _content = str(status.retweeted_status.full_text)
                except AttributeError:  # Not a Retweet
                    _content = str(status.full_text)
                content = _content.lower().replace('\n', ' ')
                corpus.append(content)
        else:
            return ResponseService(
                has_error=True,
                author=author,
                terms=terms,
                message='no encontramos ningun tweet con ese termino. intenta con otro',
                response=[]
            )

        _words = []
        for sentence in corpus:
            _unique_words = get_words(sentence)
            for word in _unique_words:
                if word != 'no':
                    _words.append(word)

        unique_words = Counter(_words).most_common(100)
        response_words = [[w[0], w[1]] for w in unique_words]
        format_response_words = ['%s(%i)' % (w[0], w[1]) for w in response_words[:10]]
        return ResponseService(
            has_error=False,
            author=author,
            terms=terms,
            message='top words: %s ...' % ', '.join(format_response_words),
            response=response_words
        )
