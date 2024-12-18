# Configuration and Constants
class Config:
    DB_PATH = "hackathon.db"
    CHART_TYPES = ["top-free", "top-paid"]
    LIMIT = 50
    ALLOW_EXPLICIT = "apps"
    DATE_FORMAT = "%Y-%m-%d"

    # Define the countries you want to visualize.
    # You should use valid two-letter country codes supported by the API.
    # See: https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/iTunesConnect_Guide/Appendices/AppStoreTerritories.html for reference.
    TERRITORIES = [
        "ae", "ag", "ai", "al", "am", "ao", "ar", "at", "au", "az", "bb", "be", "bf", "bg", "bh",
        "bj", "bm", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cg", "ch", "cl", "cn",
        "co", "cr", "cv", "cy", "cz", "de", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "fi",
        "fj", "fm", "fr", "ga", "gb", "gd", "gh", "gm", "gr", "gt", "gw", "gy", "hk", "hn", "hr",
        "hu", "id", "ie", "il", "in", "iq", "is", "it", "jm", "jo", "jp", "ke", "kg", "kh", "kn",
        "kr", "kw", "ky", "kz", "la", "lb", "lc", "lk", "lr", "lt", "lu", "lv", "md", "mg", "mk",
        "ml", "mo", "mr", "ms", "mt", "mu", "mw", "mx", "my", "mz", "na", "ne", "ng", "ni", "nl",
        "no", "np", "nz", "om", "pa", "pe", "pg", "ph", "pk", "pl", "pt", "pw", "py", "qa", "ro",
        "ru", "sa", "sb", "sc", "se", "sg", "si", "sk", "sl", "sn", "sr", "st", "sv", "sz", "tc",
        "td", "th", "tj", "tm", "tn", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc",
        "ve", "vg", "vn", "ye", "za", "zm", "zw"
    ]
