import { NumericString } from '@rotki/common';
import { currencies } from '@/data/currencies';
import {
  emptyError,
  emptyPeriod,
  tradeHistoryPlaceholder
} from '@/store/reports/const';
import {
  ProfitLossEvent,
  ProfitLossOverviewData,
  ReportError,
  ReportPeriod,
  ReportProgress
} from '@/store/reports/types';

import { AccountingSettings } from '@/types/user';

export interface ReportState {
  identifier: number;
  name: string;
  created: number;
  startTs: number;
  endTs: number;
  sizeOnDisk: typeof NumericString;
  firstProcessedTimestamp: number;
  processed: number;
  limit: number;
  overview: ProfitLossOverviewData;
  events: ProfitLossEvent[];
  accountingSettings: AccountingSettings | null;
  reportPeriod: ReportPeriod;
  currency: string;
  loaded: boolean;
  progress: ReportProgress;
  reportError: ReportError;
}

export const defaultState = (): ReportState => ({
  identifier: -1,
  name: '',
  created: -1,
  startTs: -1,
  endTs: -1,
  sizeOnDisk: NumericString,
  overview: tradeHistoryPlaceholder(),
  events: [],
  processed: -1,
  limit: -1,
  firstProcessedTimestamp: -1,
  accountingSettings: null,
  reportPeriod: emptyPeriod(),
  currency: currencies[0].tickerSymbol,
  loaded: false,
  progress: {
    processingState: '',
    totalProgress: ''
  },
  reportError: emptyError()
});

export const state: ReportState = defaultState();
