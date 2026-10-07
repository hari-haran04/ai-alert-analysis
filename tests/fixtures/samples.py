TRUE_POSITIVE_ALERT = {
    "alertId": "ALT-1001",
    "screeningType": "SANCTIONS",
    "thirdParty": {
        "entityId": "TP001",
        "name": "Gold Mayning 000",
        "country": "Russia",
        "city": "Yakutsk",
        "registrationNumber": "1201400007291",
        "taxId": "1435353596",
    },
    "hits": [
        {
            "hitId": "HIT001",
            "name": "Gold Mayning 000",
            "country": "Russia",
            "city": "Yakutsk",
            "registrationNumber": "1201400007291",
            "taxId": "1435353596",
            "score": 100,
            "level": "HIGH",
            "listType": "US_50PLUS",
            "source": "KHARON",
        },
        {
            "hitId": "HIT002",
            "name": "Sakha Gold Mayning AO",
            "country": "Russia",
            "city": "Aldan",
            "score": 94,
            "level": "MEDIUM",
            "listType": "US_50PLUS",
            "source": "KHARON",
        },
    ],
}

FALSE_POSITIVE_ALERT = {
    "alertId": "ALT-1002",
    "screeningType": "SANCTIONS",
    "thirdParty": {
        "entityId": "TP002",
        "name": "Michael Jordan",
        "country": "USA",
        "city": "Chicago",
        "dateOfBirth": "1985-06-20",
        "passportNumber": "P12345678",
    },
    "hits": [
        {
            "hitId": "HIT010",
            "name": "Michael B Jordan",
            "country": "USA",
            "city": "New York",
            "dateOfBirth": "1960-01-01",
            "passportNumber": "P99999999",
            "score": 85,
            "level": "LOW",
            "listType": "WATCHLIST",
            "source": "FIRCO",
        }
    ],
}

