import {
  ProfitLossOverviewData,
  ReportError,
  ReportPeriod
} from '@rotki/common/lib/reports';
import { Zero } from '@/utils/bignumbers';

export enum ReportActions {
  FETCH_REPORTS = 'fetchReports',
  FETCH_REPORT = 'fetchReport',
  EDIT_REPORT = 'editReport'
}

export enum ReportMutations {
  SET_REPORT = 'set',
  SET_REPORTS = 'setReports',
  ADD_REPORT = 'addReport',
  CURRENCY = 'currency',
  REPORT_PERIOD = 'reportPeriod',
  ACCOUNT_SETTINGS = 'accountSettings',
  RESET = 'reset'
}

export const MUTATION_PROGRESS = 'progress';
export const MUTATION_REPORT_ERROR = 'reportError';

export const emptyPeriod: () => ReportPeriod = () => ({
  start: 0,
  end: 0
});

export const emptyError: () => ReportError = () => ({
  error: '',
  message: ''
});

export const tradeHistoryPlaceholder = (): ProfitLossOverviewData => ({
  loanProfit: Zero,
  defiProfitLoss: Zero,
  marginPositionsProfitLoss: Zero,
  settlementLosses: Zero,
  ethereumTransactionGasCosts: Zero,
  ledgerActionsProfitLoss: Zero,
  assetMovementFees: Zero,
  generalTradeProfitLoss: Zero,
  taxableTradeProfitLoss: Zero,
  totalTaxableProfitLoss: Zero,
  totalProfitLoss: Zero
});
