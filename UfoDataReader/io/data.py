#!/usr/local/bin python
# -*- coding: UTF-8 -*-
import warnings
import requests
import xml.etree.ElementTree as ElemTree
from pandas_datareader import data
from pandas_datareader.base import _DailyBaseReader, _in_chunks
from time import sleep
from dateutil import parser
import pandas.compat as compat
from pandas import DataFrame
from pandas_datareader._utils import RemoteDataError, SymbolWarning
from io import BytesIO
from zipfile import ZipFile

_SLEEP_TIME = 1.0
_MAX_RETRY_COUNT = 2


class UfoReader(_DailyBaseReader):
    _namespace = '{http://www.w3.org/2005/Atom}'

    def __init__(self, symbols=None, start=None, end=None, fetch_xbrl=False, **kwargs):
        super(UfoReader, self).__init__(symbols=symbols,
                                        start=start,
                                        end=end,
                                        **kwargs)
        self.fetch_xbrl = fetch_xbrl

    @property
    def url(self):
        return 'http://resource.ufocatch.com/atom/edinetx/query/{symbol}'

    def _get_params(self, symbol):
        return {'symbol': symbol}

    def read(self):
        """ read data """
        # If a single symbol
        if isinstance(self.symbols, (compat.string_types, int)):
            d = self._read_one_data(self.url, params=self._get_params(self.symbols))
        # Or multiple symbols
        elif isinstance(self.symbols, DataFrame):
            d = self._dl_mult_symbols(self.symbols.index)
        else:
            d = self._dl_mult_symbols(self.symbols)
        return d

    def _dl_mult_symbols(self, symbols):
        stocks = {}
        failed = []
        passed = []
        for sym_group in _in_chunks(symbols, self.chunksize):
            for sym in sym_group:
                try:
                    stocks[sym] = self._read_one_data(self.url, self._get_params(sym))
                    passed.append(sym)
                except IOError:
                    msg = 'Failed to read symbol: {0!r}, replacing with NaN.'
                    warnings.warn(msg.format(sym), SymbolWarning)
                    failed.append(sym)

        if len(passed) == 0:
            msg = "No data fetched using {0!r}"
            raise RemoteDataError(msg.format(self.__class__.__name__))
        elif len(stocks) > 0 and len(failed) > 0 and len(passed) > 0:
            for sym in failed:
                stocks[sym] = None
        return stocks

    def _read_one_data(self, url, params):
        results = []

        # retrying _MAX_RETRY_COUNT
        for _ in range(1, _MAX_RETRY_COUNT):
            try:
                url = self.url.format(**params)
                tree = ElemTree.fromstring(requests.get(url).text.encode('utf-8'))
                break
            except requests.HTTPError:
                sleep(_SLEEP_TIME)
        else:
            raise Exception

        for el in tree.findall('.//' + self._namespace + 'entry'):
            updated = el.find(self._namespace + 'updated').text
            updated = parser.parse(updated, ignoretz=True)

            if self.start <= updated <= self.end:
                id = el.find(self._namespace + 'id').text
                title = el.find(self._namespace + 'title').text
                docid = el.find(self._namespace + 'docid').text
                url = el.find(self._namespace + 'link[@type="application/zip"]').attrib['href']
                is_yuho = any([word in title for word in ['有価証券報告書', '四半期報告書']])
                is_quarterly =  '四半期報告書' in title

                if self.fetch_xbrl:
                    r = requests.get(url)
                    if r.ok:
                        z = ZipFile(BytesIO(r.content))
                        for info in z.infolist():
                            if is_yuho and '.xbrl' in info.filename and 'AuditDoc' not in info.filename:
                                self.xbrl_filename = info.filename.split('/')[-1]
                                z.extract(info.filename)

                results.append(
                    {
                        'id': id,
                        'title': title,
                        'docid': docid,
                        'url': url,
                        'updated': updated,
                        'is_yuho': is_yuho,
                        'is_quarterly': is_quarterly,
                    }
                )
        sleep(_SLEEP_TIME)
        return results


def DataReader(symbols, data_source=None, start=None, end=None, **kwargs):
    if data_source == 'ufo':
        fetch_xbrl = kwargs.pop('fetch_xbrl', None)
        return UfoReader(symbols=symbols, start=start, end=end, fetch_xbrl=fetch_xbrl, **kwargs).read()
    else:
        return data.DataReader(name=symbols, data_source=data_source, start=start, end=end, **kwargs)


DataReader.__doc__ = data.DataReader.__doc__
