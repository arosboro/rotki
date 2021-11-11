import {
  ReportError,
  ReportProgress,
  TradeHistory
} from '@rotki/common/lib/reports';
import { ActionTree } from 'vuex';
import i18n from '@/i18n';
import { api } from '@/services/rotkehlchen-api';
import { userNotify } from '@/store/notifications/utils';
import {
  ReportActions,
  emptyError,
  ReportMutations,
  MUTATION_PROGRESS,
  MUTATION_REPORT_ERROR
} from '@/store/reports/const';
import { ReportState } from '@/store/reports/types';

import { Message, RotkehlchenState } from '@/store/types';
import { ProfitLossPeriod } from '@/types/pnl';
import { createTask, taskCompletion, TaskMeta } from '@/types/task';
import { TaskType } from '@/types/task-type';
import { logger } from '@/utils/logging';

export const actions: ActionTree<ReportState, RotkehlchenState> = {
  async generate({ commit, rootState }, payload: ProfitLossPeriod) {
    commit('accountingSettings', rootState.session!.accountingSettings);
    commit(MUTATION_PROGRESS, {
      processingState: '',
      totalProgress: '0'
    } as ReportProgress);
    commit(MUTATION_REPORT_ERROR, emptyError());

    const interval = setInterval(async () => {
      const progress = await api.history.getProgress();
      commit(MUTATION_PROGRESS, progress);
    }, 2000);

    try {
      const { report_id, start, end } = payload;
      const { taskId } = await api.processTradeHistoryAsync(
        report_id,
        start,
        end
      );
      commit('reportPeriod', { start, end });
      const task = createTask(taskId, TaskType.TRADE_HISTORY, {
        title: i18n.t('actions.reports.generate.task.title').toString(),
        numericKeys: [
          'paid_in_asset',
          'taxable_amount',
          'paid_in_profit_currency',
          'taxable_bought_cost_in_profit_currency',
          'taxable_received_in_profit_currency',
          'received_in_asset',
          'net_profit_or_loss',
          'loan_profit',
          'defi_profit_loss',
          'margin_positions_profit_loss',
          'ledger_actions_profit_loss',
          'settlement_losses',
          'ethereum_transaction_gas_costs',
          'asset_movement_fees',
          'general_trade_profit_loss',
          'taxable_trade_profit_loss',
          'total_taxable_profit_loss',
          'total_profit_loss',
          'used_amount',
          'amount',
          'rate',
          'fee_rate'
        ],
        ignoreResult: false
      });
      commit('tasks/add', task, { root: true });

      const { result } = await taskCompletion<TradeHistory, TaskMeta>(
        TaskType.TRADE_HISTORY
      );

      if (!result || !result.overview || !result.allEvents) {
        commit(MUTATION_REPORT_ERROR, {
          error: '',
          message: i18n
            .t('actions.reports.generate.error.description', { error: '' })
            .toString()
        } as ReportError);
        return;
      }

      const {
        overview,
        allEvents,
        eventsLimit,
        eventsProcessed,
        firstProcessedTimestamp
      } = result;

      const report = {
        overview: overview,
        allEvents: allEvents,
        limit: eventsLimit,
        processed: eventsProcessed,
        firstProcessedTimestamp
      };
      commit('set', report);
    } catch (e: any) {
      commit(MUTATION_REPORT_ERROR, {
        error: e.message,
        message: i18n.t('actions.reports.generate.error.description').toString()
      } as ReportError);
    }

    clearInterval(interval);

    commit(MUTATION_PROGRESS, {
      processingState: '',
      totalProgress: '0'
    } as ReportProgress);
  },

  async [ReportActions.FETCH_REPORTS]({ commit }) {
    const notify = async (error?: any) => {
      logger.error(error);
      const message = error?.message ?? error ?? '';
      await userNotify({
        title: i18n.t('actions.reports.fetch.error.title').toString(),
        message: i18n
          .t('actions.reports.fetch.error.description', { message })
          .toString(),
        display: true
      });
    };
    try {
      const result = await api.reports.fetchReports();
      commit(ReportMutations.SET_REPORTS, result);
    } catch (e: any) {
      await notify(e);
    }
  },
  async createCSV({ commit }, path: string) {
    let message: Message;
    try {
      const success = await api.exportHistoryCSV(path);
      message = {
        title: i18n.t('actions.reports.csv_export.title').toString(),
        description: success
          ? i18n.t('actions.reports.csv_export.message.success').toString()
          : i18n.t('actions.reports.csv_export.message.failure').toString(),
        success
      };
    } catch (e: any) {
      message = {
        title: i18n.t('actions.reports.csv_export.title').toString(),
        description: e.message,
        success: false
      };
    }
    commit('setMessage', message, { root: true });
  }
};
