import requests
import requests_cache

from app import _config


class Request:

    def __init__(self, cache_name, time_out=30.0):
        self._cache = cache_name
        self._time_out = time_out

    def _get(self, URL):
        requests_cache.install_cache(self._cache, backend='sqlite', expire_after=self._time_out)
        requests_cache.remove_expired_responses()
        return requests.get(URL)


class CaseRequest(Request):

    def __init__(self):
        Request.__init__(self, cache_name='case_data')
        self.get_case_data(state_code='TT')

    def __case_data(self):
        return self._get(_config.CASE_URL)

    def get_state_wise_cases(self):
        return self.__case_data().json()['statewise']

    def get_case_data(self, state_code):
        idx = int(str([idx for idx, data in enumerate(self.__case_data().json()['statewise']) if
                       data.get('statecode') == state_code])[1:-1])

        return self.__case_data().json()['statewise'][idx]


class StateRequest(Request):

    def __init__(self):
        Request.__init__(self, cache_name='state_data')

    def __state_data(self):
        return self._get(_config.DISTRICT_URL)

    def get_district_data(self, state_code=None):
        __DATA = self.__state_data().json()

        return __DATA if state_code is None else __DATA[state_code]['districtData']

    def get_state_confirmed(self):
        __TN_DATA = self.get_district_data(state_code="Tamil Nadu")
        print(self.__state_data().json())
        return [__TN_DATA[case]['confirmed'] for case in list(__TN_DATA)]