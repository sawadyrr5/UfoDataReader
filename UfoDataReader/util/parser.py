# -*- coding: utf-8 -*-
from xbrl import XBRLParser, XBRLParserException
import re
import logging
from decimal import Decimal


class UfoXBRLParser(XBRLParser):
    def parse(self, file_handle):
        with open(file_handle, 'r', encoding='utf-8') as of:
            xbrl = super().parse(of)
        return xbrl

    def parseGAAP(self,
                  xbrl,
                  doc_date="",
                  context="Current",
                  is_quarterly=False,
                  ignore_errors=0):

        """
        Parse Japan GAAP or US GAAP from our XBRL soup and return a GAAP object.
        """

        if ignore_errors == 2:
            logging.basicConfig(filename='/tmp/xbrl.log',
                                level=logging.ERROR,
                                format='%(asctime)s %(levelname)s %(name)s %(message)s')
            logger = logging.getLogger(__name__)
        else:
            logger = None

        # collect all contexts up that are relevant to us
        context_ids = []
        if context in ('Current', 'Prior1', 'Prior2', 'Prior3', 'Prior4'):
            if is_quarterly:
                context_ids = [context + 'YTDDuration']
            else:
                context_ids = [context + 'YearInstant', context + 'YearDuration']

        dei = self.parseDEI(xbrl)

        # try:
        #     for context_tag in context_tags:
        #         # we don't want any segments
        #         if context in context_tag.attrs['contextref']:
        #             context_ids.append()
        #
        #         if context_tag.find(doc_root + "entity") is None:
        #             continue
        #         if context_tag.find(doc_root + "entity").find(
        #         doc_root + "segment") is None:
        #             context_id = context_tag.attrs['id']
        #
        #             found_start_date = None
        #             found_end_date = None
        # except IndexError:
        #     raise XBRLParserException('problem getting contexts')

        gaap_obj = None

        # incomes
        if dei.accounting_standards == 'Japan GAAP':
            gaap_obj = JapanGAAP()

            netsales = \
                xbrl.find_all(name=re.compile('jpcrp_cor:NetSalesSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.netsales = \
                self.data_processing(netsales, xbrl, ignore_errors, logger, context_ids)

            ordinary_income_loss = \
                xbrl.find_all(name=re.compile('jpcrp_cor:OrdinaryIncomeLossSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.ordinary_income_loss = \
                self.data_processing(ordinary_income_loss, xbrl, ignore_errors, logger, context_ids)

            profit_loss = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:ProfitLossAttributableToOwnersOfParentSummaryOfBusinessResults',
                                    re.IGNORECASE | re.MULTILINE))
            gaap_obj.profit_loss = \
                self.data_processing(profit_loss, xbrl, ignore_errors, logger, context_ids)

            comprehensive_income = \
                xbrl.find_all(name=re.compile('jpcrp_cor:ComprehensiveIncomeSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.comprehensive_income = \
                self.data_processing(comprehensive_income, xbrl, ignore_errors, logger, context_ids)

            net_assets = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:NetAssetsSummaryOfBusinessResults', re.IGNORECASE | re.MULTILINE))
            gaap_obj.net_assets = \
                self.data_processing(net_assets, xbrl, ignore_errors, logger, context_ids)

            total_assets = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:TotalAssetsSummaryOfBusinessResults', re.IGNORECASE | re.MULTILINE))
            gaap_obj.total_assets = \
                self.data_processing(total_assets, xbrl, ignore_errors, logger, context_ids)

            bps = \
                xbrl.find_all(name=re.compile('jpcrp_cor:NetAssetsPerShareSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.bps = \
                self.data_processing(bps, xbrl, ignore_errors, logger, context_ids)

            dps = \
                xbrl.find_all(name=re.compile('jpcrp_cor:DividendPaidPerShareSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.dps = \
                self.data_processing(dps, xbrl, ignore_errors, logger, context_ids)

            basic_eps = \
                xbrl.find_all(name=re.compile('jpcrp_cor:BasicEarningsLossPerShareSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.basic_eps = \
                self.data_processing(basic_eps, xbrl, ignore_errors, logger, context_ids)

            diluted_eps = \
                xbrl.find_all(name=re.compile('jpcrp_cor:DilutedEarningsPerShareSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.diluted_eps = \
                self.data_processing(diluted_eps, xbrl, ignore_errors, logger, context_ids)

            equity_to_asset_ratio = \
                xbrl.find_all(name=re.compile('jpcrp_cor:EquityToAssetRatioSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.equity_to_asset_ratio = \
                self.data_processing(equity_to_asset_ratio, xbrl, ignore_errors, logger, context_ids)

            roe = \
                xbrl.find_all(name=re.compile('jpcrp_cor:RateOfReturnOnEquitySummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.roe = \
                self.data_processing(roe, xbrl, ignore_errors, logger, context_ids)

            per = \
                xbrl.find_all(name=re.compile('jpcrp_cor:PriceEarningsRatioSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.per = \
                self.data_processing(per, xbrl, ignore_errors, logger, context_ids)

            cf_from_operating = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:NetCashProvidedByUsedInOperatingActivitiesSummaryOfBusinessResults',
                                    re.IGNORECASE | re.MULTILINE))
            gaap_obj.cf_from_operating = \
                self.data_processing(cf_from_operating, xbrl, ignore_errors, logger, context_ids)

            cf_from_investing = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:NetCashProvidedByUsedInInvestingActivitiesSummaryOfBusinessResults',
                                    re.IGNORECASE | re.MULTILINE))
            gaap_obj.cf_from_investing = \
                self.data_processing(cf_from_investing, xbrl, ignore_errors, logger, context_ids)

            cf_from_financing = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:NetCashProvidedByUsedInFinancingActivitiesSummaryOfBusinessResults',
                                    re.IGNORECASE | re.MULTILINE))
            gaap_obj.cf_from_financing = \
                self.data_processing(cf_from_financing, xbrl, ignore_errors, logger, context_ids)

        # incomes
        if dei.accounting_standards == 'US GAAP':
            gaap_obj = USGAAP()
            revenues = \
                xbrl.find_all(name=re.compile('jpcrp_cor:RevenuesUSGAAPSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.revenues = \
                self.data_processing(revenues, xbrl, ignore_errors, logger, context_ids)

            operating_income_loss = \
                xbrl.find_all(name=re.compile('jpcrp_cor:OperatingIncomeLossUSGAAPSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.operating_income_loss = \
                self.data_processing(operating_income_loss, xbrl, ignore_errors, logger, context_ids)

            profit_loss_before_tax = \
                xbrl.find_all(name=re.compile('jpcrp_cor:ProfitLossBeforeTaxUSGAAPSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.profit_loss_before_tax = \
                self.data_processing(profit_loss_before_tax, xbrl, ignore_errors, logger, context_ids)

            net_income_loss = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:NetIncomeLossAttributableToOwnersOfParentUSGAAPSummaryOfBusinessResults',
                                    re.IGNORECASE | re.MULTILINE))
            gaap_obj.net_income_loss = \
                self.data_processing(net_income_loss, xbrl, ignore_errors, logger, context_ids)

            comprehensive_income = \
                xbrl.find_all(name=re.compile('jpcrp_cor:ComprehensiveIncomeUSGAAPSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.comprehensive_income = \
                self.data_processing(comprehensive_income, xbrl, ignore_errors, logger, context_ids)

            basic_eps = \
                xbrl.find_all(name=re.compile('jpcrp_cor:BasicEarningsLossPerShareUSGAAPSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.basic_eps = \
                self.data_processing(basic_eps, xbrl, ignore_errors, logger, context_ids)

            diluted_eps = \
                xbrl.find_all(name=re.compile('jpcrp_cor:DilutedEarningsLossPerShareUSGAAPSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.diluted_eps = \
                self.data_processing(diluted_eps, xbrl, ignore_errors, logger, context_ids)

            per = \
                xbrl.find_all(name=re.compile('jpcrp_cor:PriceEarningsRatioUSGAAPSummaryOfBusinessResults',
                                              re.IGNORECASE | re.MULTILINE))
            gaap_obj.per = \
                self.data_processing(per, xbrl, ignore_errors, logger, context_ids)

            cf_from_operating = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:CashFlowsFromUsedInOperatingActivitiesUSGAAPSummaryOfBusinessResults',
                                    re.IGNORECASE | re.MULTILINE))
            gaap_obj.cf_from_operating = \
                self.data_processing(cf_from_operating, xbrl, ignore_errors, logger, context_ids)

            cf_from_investing = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:CashFlowsFromUsedInInvestingActivitiesUSGAAPSummaryOfBusinessResults',
                                    re.IGNORECASE | re.MULTILINE))
            gaap_obj.cf_from_investing = \
                self.data_processing(cf_from_investing, xbrl, ignore_errors, logger, context_ids)

            cf_from_financing = \
                xbrl.find_all(
                    name=re.compile('jpcrp_cor:CashFlowsFromUsedInFinancingActivitiesUSGAAPSummaryOfBusinessResults',
                                    re.IGNORECASE | re.MULTILINE))
            gaap_obj.cf_from_financing = \
                self.data_processing(cf_from_financing, xbrl, ignore_errors, logger, context_ids)

        # balance
        shares_outstanding = \
            xbrl.find_all(name=re.compile('jpcrp_cor:TotalNumberOfIssuedSharesSummaryOfBusinessResults',
                                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.shares_outstanding = \
            self.data_processing(shares_outstanding, xbrl, ignore_errors, logger, context_ids)

        assets = \
            xbrl.find_all(name=re.compile('jppfs_cor:Assets',
                                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.assets = \
            self.data_processing(assets, xbrl, ignore_errors, logger, context_ids)

        current_assets = \
            xbrl.find_all(name=re.compile('jppfs_cor:CurrentAssets',
                                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.current_assets = \
            self.data_processing(current_assets, xbrl, ignore_errors, logger, context_ids)

        non_current_assets = \
            xbrl.find_all(name=re.compile('jppfs_cor:NonCurrentAssets',
                                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.non_current_assets = \
            self.data_processing(non_current_assets, xbrl, ignore_errors, logger, context_ids)

        liabilities = \
            xbrl.find_all(name=re.compile('jppfs_cor:Liabilities',
                                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.liabilities = \
            self.data_processing(liabilities, xbrl, ignore_errors, logger, context_ids)

        current_liabilities = \
            xbrl.find_all(name=re.compile('jppfs_cor:CurrentLiabilities',
                                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.current_liabilities = \
            self.data_processing(current_liabilities, xbrl, ignore_errors, logger, context_ids)

        non_current_liabilities = \
            xbrl.find_all(name=re.compile('jppfs_cor:NonCurrentLiabilities',
                                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.non_current_liabilities = \
            self.data_processing(non_current_liabilities, xbrl, ignore_errors, logger, context_ids)

        net_assets = \
            xbrl.find_all(name=re.compile('jppfs_cor:NetAssets',
                                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_assets = \
            self.data_processing(net_assets, xbrl, ignore_errors, logger, context_ids)

        return gaap_obj

    @classmethod
    def data_processing(self,
                        elements,
                        xbrl,
                        ignore_errors,
                        logger,
                        context_ids=[],
                        **kwargs):
        """
        Process a XBRL tag object and extract the correct value as
        stated by the context.
        """
        options = kwargs.get('options', {'type': 'Number',
                                         'no_context': False})

        if options['type'] == 'String':
            if len(elements) > 0:
                return elements[0].text

        if options['no_context'] == True:
            if len(elements) > 0 and XBRLParser().is_number(elements[0].text):
                return elements[0].text

        try:

            # Extract the correct values by context
            correct_elements = []
            for element in elements:
                contextrefs = element.attrs['contextref'].split('_')

                if any([context_id in contextrefs for context_id in context_ids]):
                    correct_elements.append(element)

            elements = correct_elements

            if len(elements) > 0 and XBRLParser().is_number(elements[0].text):
                return float(elements[0].text)
            else:
                return 0

            # if len(elements) > 0 and XBRLParser().is_number(elements[0].text):
            #     decimals = elements[0].attrs['decimals']
            #     if decimals is not None:
            #         attr_precision = decimals
            #         if xbrl.precision != 0 and xbrl.precison != attr_precision:
            #             xbrl.precision = attr_precision
            #     if elements:
            #         return XBRLParser().trim_decimals(elements[0].text, int(xbrl.precision))
            #     else:
            #         return 0
            # else:
            #     return 0
        except Exception as e:
            if ignore_errors == 0:
                raise XBRLParserException('value extraction error')
            elif ignore_errors == 1:
                return 0
            elif ignore_errors == 2:
                logger.error(str(e) + " error at " + ''.join(elements[0].text))

    @classmethod
    def parseDEI(self,
                 xbrl,
                 ignore_errors=0):
        """
        Parse DEI from our XBRL soup and return a DEI object.
        """
        dei_obj = DEI()

        if ignore_errors == 2:
            logging.basicConfig(filename='/tmp/xbrl.log',
                                level=logging.ERROR,
                                format='%(asctime)s %(levelname)s %(name)s %(message)s')
            logger = logging.getLogger(__name__)
        else:
            logger = None

        # DEI
        edinet_code = \
            xbrl.find_all(name=re.compile('jpdei_cor:EDINETCodeDEI',
                                          re.IGNORECASE | re.MULTILINE))
        dei_obj.edinet_code = \
            self.data_processing(edinet_code, xbrl, ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        trading_symbol = \
            xbrl.find_all(name=re.compile('jpdei_cor:SecurityCodeDei', re.IGNORECASE | re.MULTILINE))
        dei_obj.trading_symbol = \
            self.data_processing(trading_symbol, xbrl, ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        company_name = \
            xbrl.find_all(name=re.compile('jpcrp_cor:CompanyNameCoverPage',
                                          re.IGNORECASE | re.MULTILINE))
        dei_obj.company_name = \
            self.data_processing(company_name, xbrl, ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        accounting_standards = \
            xbrl.find_all(name=re.compile('jpdei_cor:AccountingStandardsDEI',
                                          re.IGNORECASE | re.MULTILINE))
        dei_obj.accounting_standards = \
            self.data_processing(accounting_standards, xbrl, ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        current_fy_start = \
            xbrl.find_all(name=re.compile('jpdei_cor:CurrentFiscalYearStartDateDei',
                                          re.IGNORECASE | re.MULTILINE))
        dei_obj.current_fy_start = \
            self.data_processing(current_fy_start, xbrl, ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        current_fy_end = \
            xbrl.find_all(name=re.compile('jpdei_cor:CurrentFiscalYearEndDateDei',
                                          re.IGNORECASE | re.MULTILINE))
        dei_obj.current_fy_end = \
            self.data_processing(current_fy_end, xbrl, ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        type_of_current_period = \
            xbrl.find_all(name=re.compile('jpdei_cor:TypeOfCurrentPeriodDEI',
                                          re.IGNORECASE | re.MULTILINE))
        dei_obj.type_of_current_period = \
            self.data_processing(type_of_current_period, xbrl, ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        return dei_obj


# Base US GAAP object
class USGAAP(object):
    def __init__(self,
                 revenues=0.0,
                 operating_income_loss=0.0,
                 profit_loss_before_tax=0.0,
                 net_income_loss=0.0,
                 comprehensive_income=0.0,
                 basic_eps=0.0,
                 diluted_eps=0.0,
                 per=0.0,
                 cf_from_operating=0.0,
                 cf_from_investing=0.0,
                 cf_from_financing=0.0,
                 shares_outstanding=0.0):
        self.revenues = revenues
        self.operating_income_loss = operating_income_loss
        self.profit_loss_before_tax = profit_loss_before_tax
        self.net_income_loss = net_income_loss
        self.comprehensive_income = comprehensive_income
        self.basic_eps = basic_eps
        self.diluted_eps = diluted_eps
        self.per = per
        self.cf_from_operating = cf_from_operating
        self.cf_from_investing = cf_from_investing
        self.cf_from_financing = cf_from_financing
        self.shares_outstanding = shares_outstanding


# Base Japan GAAP object
class JapanGAAP(object):
    def __init__(self,
                 netsales=0.0,
                 ordinary_income_loss=0.0,
                 profit_loss=0.0,
                 comprehensive_income=0.0,
                 net_assets=0.0,
                 total_assets=0.0,
                 bps=0.0,
                 dps=0.0,
                 basic_eps=0.0,
                 diluted_eps=0.0,
                 equity_to_asset_ratio=0.0,
                 roe=0.0,
                 per=0.0,
                 cf_from_operating=0.0,
                 cf_from_investing=0.0,
                 cf_from_financing=0.0,
                 shares_outstanding=0.0):
        self.netsales = netsales
        self.ordinary_income_loss = ordinary_income_loss
        self.profit_loss = profit_loss
        self.comprehensive_income = comprehensive_income
        self.net_assets = net_assets
        self.total_assets = total_assets
        self.bps = bps
        self.dps = dps
        self.basic_eps = basic_eps
        self.diluted_eps = diluted_eps
        self.equity_to_asset_ratio = equity_to_asset_ratio
        self.roe = roe
        self.per = per
        self.cf_from_operating = cf_from_operating
        self.cf_from_investing = cf_from_investing
        self.cf_from_financing = cf_from_financing
        self.shares_outstanding = shares_outstanding


# Base DEI object
class DEI(object):
    def __init__(self,
                 edinet_code='',
                 trading_symbol='',
                 company_name='',
                 accounting_standards='',
                 current_fy_start='',
                 current_fy_end='',
                 type_of_current_period=''):
        self.edinet_code = edinet_code
        self.trading_symbol = trading_symbol
        self.company_name = company_name
        self.accounting_standards = accounting_standards
        self.current_fy_start = current_fy_start
        self.current_fy_end = current_fy_end
        self.type_of_current_period = type_of_current_period
