from wisdomhord import Bisen, Sweor, Integer, String, DateTime


class QuoteEntry(Bisen):
    __invoker__ = "Forebodere"
    __description__ = "Quotes"
    id = Sweor("ID", Integer)
    submitter = Sweor("SUBMITTER", String)
    submitted = Sweor("SUBMITTED", DateTime)
    quote = Sweor("QUOTE", String)
