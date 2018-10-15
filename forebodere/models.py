from wisdomhord import Bisen, Sweor, Integer, String


class QuoteEntry(Bisen):
    __invoker__ = "Forebodere"
    __description__ = "Quotes"
    id = Sweor("ID", Integer)
    quote = Sweor("QUOTE", String)
