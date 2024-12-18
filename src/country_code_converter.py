import pycountry

class CountryCodeConverter:
    """
    A utility class that converts various country identifiers (alpha-2 codes,
    alpha-3 codes, or full country names) into a unified representation.
    
    The returned representation includes:
    - alpha_2: The two-letter ISO code
    - alpha_3: The three-letter ISO code
    - name: The official full country name
    """
    def __init__(self, country_inputs=None):
        """
        Initialize the converter with an optional list of country identifiers.

        Parameters
        ----------
        country_inputs : list of str, optional
            A list of country identifiers in any of these formats:
            - ISO alpha-2 code (e.g., "us", "gb")
            - ISO alpha-3 code (e.g., "usa", "gbr")
            - Full country name (e.g., "United States", "United Kingdom")
        """
        self.country_inputs = country_inputs if country_inputs else []
    
    def set_country_inputs(self, inputs):
        """
        Set or update the list of country identifiers.

        Parameters
        ----------
        inputs : list of str
            The new list of country identifiers.
        """
        self.country_inputs = inputs

    def convert(self):
        """
        Convert the stored country inputs into a list of dictionaries containing alpha_2, alpha_3, and full_name.

        Returns
        -------
        list of dict
            Each dictionary contains:
            - input_value: The original input value provided
            - alpha_2: ISO alpha-2 code or None if not found
            - alpha_3: ISO alpha-3 code or None if not found
            - name: Full country name or None if not found
        """
        results = []
        for val in self.country_inputs:
            country_info = self._lookup_country(val)
            results.append(country_info)
        return results

    def _lookup_country(self, val):
        """
        Look up country information based on the provided value (alpha-2, alpha-3, or full name).

        Parameters
        ----------
        val : str
            The input country identifier.

        Returns
        -------
        dict
            Dictionary with fields: input_value, alpha_2, alpha_3, full_name
        """
        val_stripped = val.strip()
        
        # Attempt lookup based on length or fallback to name
        # pycountry expects uppercase for alpha codes
        country_obj = None
        if len(val_stripped) == 2:
            # Treat as alpha_2 code
            country_obj = pycountry.countries.get(alpha_2=val_stripped.upper())
        elif len(val_stripped) == 3 and val_stripped.isalpha():
            # Treat as alpha_3 code
            country_obj = pycountry.countries.get(alpha_3=val_stripped.upper())
        else:
            # Treat as a full name
            # pycountry name lookups are case sensitive and exact
            # Try exact match first
            country_obj = pycountry.countries.get(name=val_stripped)
            if not country_obj:
                # Attempt a case-insensitive lookup by looping (less efficient but robust)
                # You could enhance this with a dictionary cache if performance is an issue.
                for ctry in pycountry.countries:
                    if ctry.name.lower() == val_stripped.lower():
                        country_obj = ctry
                        break

        if country_obj:
            return {
                "input_value": val_stripped,
                "alpha_2": country_obj.alpha_2,
                "alpha_3": country_obj.alpha_3,
                "name": country_obj.name
            }
        else:
            return {
                "input_value": val_stripped,
                "alpha_2": None,
                "alpha_3": None,
                "name": None
            }


# Example usage:
if __name__ == "__main__":
    inputs = ["us", "USA", "United States", "gb", "gbr", "United Kingdom", "fr", "fra", "France", "de", "deu", "Germany"]
    converter = CountryCodeConverter(inputs)
    converted = converter.convert()
    for c in converted:
        print(f"Input: {c['input_value']} -> alpha_2: {c['alpha_2']}, alpha_3: {c['alpha_3']}, name: {c['name']}")
