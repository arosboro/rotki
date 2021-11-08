import {
  PagedReport,
  ReportError,
  ReportPeriod,
  ReportProgress,
  ReportsTableData
} from '@rotki/common/lib/reports';
import { MutationTree } from 'vuex';
import {
  MUTATION_PROGRESS,
  MUTATION_REPORT_ERROR,
  ReportMutations
} from '@/store/reports/const';
import { defaultState } from '@/store/reports/state';

import { ReportState } from '@/store/reports/types';
import { AccountingSettings } from '@/types/user';

export const mutations: MutationTree<ReportState> = {
  [ReportMutations.SET_REPORT](state: ReportState, payload: PagedReport) {
    const { overview, events, processed, limit, firstProcessedTimestamp } =
      payload;
    state.data.overview = { ...overview };
    state.data.events = [...events];
    state.data.processed = processed;
    state.data.limit = limit;
    state.data.loaded = true;
    state.data.firstProcessedTimestamp = firstProcessedTimestamp;
  },

  [ReportMutations.SET_REPORTS](state: ReportState, payload: ReportsTableData) {
    state.index = payload;
  },

  [ReportMutations.CURRENCY](state: ReportState, currency: string) {
    state.currency = currency;
  },

  [ReportMutations.REPORT_PERIOD](state: ReportState, payload: ReportPeriod) {
    state.reportPeriod = payload;
  },

  [ReportMutations.ACCOUNT_SETTINGS](
    state: ReportState,
    payload: AccountingSettings
  ) {
    state.accountingSettings = payload;
  },

  [MUTATION_PROGRESS](state: ReportState, payload: ReportProgress) {
    state.progress = payload;
  },

  [MUTATION_REPORT_ERROR](state: ReportState, payload: ReportError) {
    state.reportError = payload;
  },
  reset(state: ReportState) {
    Object.assign(state, defaultState());
  }
};
